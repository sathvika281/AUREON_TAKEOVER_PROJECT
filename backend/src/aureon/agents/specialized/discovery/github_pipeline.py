import uuid
from dataclasses import asdict
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.agents.mission.mission import Mission
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.specialized.discovery.github_evidence import (
    ReasoningFacts,
    RepoFacts,
    SkillFinding,
    build_repo_facts,
    extract_skills,
)
from aureon.agents.specialized.discovery.github_reader import GitHubFetchResult, parse_repo_url
from aureon.agents.specialized.discovery.github_reasoning import analyze_repository
from aureon.agents.specialized.discovery.github_schemas import GitHubInvestigationTurnOutput
from aureon.agents.specialized.discovery.tools import GitHubReaderTool
from aureon.agents.tools.base import ToolStatus, run_tool_safely
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.github_investigation import GitHubInvestigationRecord, GitHubSkillRecord
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName

GITHUB_INVESTIGATION_STAGES = [
    "Mission Created",
    "Repository Validation",
    "Reading Repository",
    "Extracting Engineering Evidence",
    "Engineering Analysis",
    "Knowledge Fusion",
    "Updating Career DNA",
    "Updating Discovery Notebook",
    "Investigation Complete",
]

#: Conservative, structural-only Career DNA rules — every rule fires only
#: from real repository structure/technology signals, never popularity.
#: Scores are moderate (not maxed) since this is one inferential signal
#: among many the student's Career DNA already draws from conversation.
_CURIOSITY_SCORE = 0.6
_COMMUNICATION_SCORE = 0.6
_ANALYTICAL_THINKING_SCORE = 0.65
_MOTIVATION_SCORE = 0.55
_README_SUBSTANTIAL_CHARS = 300


def _confidence_label(score: float) -> str:
    if score >= 0.7:
        return "High"
    if score >= 0.4:
        return "Medium"
    return "Emerging"


class CareerDnaUpdatePlan(BaseModel):
    trait: str
    score: float
    summary: str
    evidence_text: str


def _plan_career_dna_updates(facts: ReasoningFacts) -> list[CareerDnaUpdatePlan]:
    """Every plan here is grounded only in structural/technical facts —
    never facts.reasoning's absence of stars/forks is even checked,
    since ReasoningFacts never carries them at all."""
    plans: list[CareerDnaUpdatePlan] = []

    diverse_tech = sorted(set(facts.languages) | set(facts.topics))
    if len(diverse_tech) >= 3:
        plans.append(
            CareerDnaUpdatePlan(
                trait="curiosity", score=_CURIOSITY_SCORE,
                summary="Explores a broad range of technologies in real projects.",
                evidence_text=f"Diverse technologies detected in this repository: {', '.join(diverse_tech)}.",
            )
        )

    if facts.readme_present and facts.readme_length >= _README_SUBSTANTIAL_CHARS:
        plans.append(
            CareerDnaUpdatePlan(
                trait="communication", score=_COMMUNICATION_SCORE,
                summary="Writes substantial project documentation.",
                evidence_text=f"A real README of {facts.readme_length} characters was found in this repository.",
            )
        )

    if facts.has_tests and facts.has_ci:
        plans.append(
            CareerDnaUpdatePlan(
                trait="analytical_thinking", score=_ANALYTICAL_THINKING_SCORE,
                summary="Builds projects with structured testing and continuous integration.",
                evidence_text="Both a tests directory and CI workflow configuration were found in this repository.",
            )
        )

    supporting_infra = [
        label for present, label in [
            (facts.has_tests, "a tests directory"),
            (facts.has_ci, "CI configuration"),
            (bool(facts.build_files_found), "build/package configuration"),
        ] if present
    ]
    if supporting_infra:
        plans.append(
            CareerDnaUpdatePlan(
                trait="motivation", score=_MOTIVATION_SCORE,
                summary="Follows through on projects with real supporting infrastructure.",
                evidence_text=f"This repository includes {', '.join(supporting_infra)}.",
            )
        )

    return plans


class GitHubInvestigationResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    url: str
    status: ToolStatus
    explanation: str | None = None
    repo_facts: RepoFacts | None = None
    skills: list[SkillFinding] = Field(default_factory=list)
    analysis: GitHubInvestigationTurnOutput | None = None
    stages: list[str] = Field(default_factory=list)
    evidence_added: bool = False
    mission: Mission
    artifacts_updated: list[str] = Field(default_factory=list)


async def investigate_repository(
    url: str, *, student_id: str, profile: StudentProfile, llm: LLMClient
) -> GitHubInvestigationResult:
    """GitHub Intelligence's pipeline (V9) — Discovery's own flagship
    capability end-to-end, no delegation (Discovery already owns every
    artifact this touches: Career DNA, Skill Evidence, Discovery
    Notebook). Reuses MissionOrchestrator/Evidence/ToolResult exactly as
    V6/V8 built them."""
    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective="github_investigation", primary_agent=AgentName.DISCOVERY.value,
    )
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[0])  # "Mission Created"
    MissionOrchestrator.begin_execution(mission)

    identifier = parse_repo_url(url)
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[1])  # "Repository Validation"
    if identifier is None:
        MissionOrchestrator.complete(mission)
        return GitHubInvestigationResult(
            url=url, status=ToolStatus.FAILED, mission=mission, stages=mission.stage_log,
            explanation=(
                "This doesn't look like a public GitHub repository URL. GitHub Intelligence "
                "currently supports only https://github.com/{owner}/{repo} links — not "
                "organizations, gists, pull requests, issues, or discussions."
            ),
        )

    tool_result = await run_tool_safely(GitHubReaderTool(), owner=identifier.owner, repo=identifier.repo)
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[2])  # "Reading Repository"
    mission.artifacts.setdefault("tool_results", {})[AgentName.DISCOVERY.value] = [tool_result.model_dump()]

    if tool_result.status != ToolStatus.COMPLETED:
        MissionOrchestrator.complete(mission)
        return GitHubInvestigationResult(
            url=url, status=tool_result.status, explanation=tool_result.explanation,
            mission=mission, stages=mission.stage_log,
        )

    raw = tool_result.evidence[0].metadata
    fetch_result = GitHubFetchResult(
        status="completed", repo_data=raw["repo_data"], languages=raw["languages"],
        readme_text=raw["readme_text"], root_files=raw["root_files"],
        dependency_names=raw["dependency_names"], has_ci_workflows=raw["has_ci_workflows"],
    )
    facts = build_repo_facts(fetch_result)
    skills = extract_skills(facts.reasoning)
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[3])  # "Extracting Engineering Evidence"

    analysis = await analyze_repository(facts.reasoning, skills, llm=llm)
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[4])  # "Engineering Analysis"

    MissionOrchestrator.fuse_knowledge(
        mission, {"github_analysis": analysis.model_dump(), "skills": [asdict(s) for s in skills]}
    )
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[5])  # "Knowledge Fusion"

    artifacts_updated: list[str] = []
    now = datetime.now(timezone.utc)

    if not analysis.insufficient_content:
        career_dna_updates = _plan_career_dna_updates(facts.reasoning)
        for plan in career_dna_updates:
            profile.career_dna.apply_update(trait=plan.trait, score=plan.score, summary=plan.summary)
            profile.evidence_graph.append(
                EvidenceRecord(
                    id=str(uuid.uuid4()), text=plan.evidence_text, source="github",
                    related_trait=plan.trait, relation="supports", created_at=now,
                )
            )
            profile.notebook_entries.append(
                NotebookEntry(
                    id=str(uuid.uuid4()), kind="observation", text=plan.summary, source="github",
                    related_trait=plan.trait, confidence_label=_confidence_label(plan.score), created_at=now,
                )
            )
        if career_dna_updates:
            artifacts_updated.append("Career DNA Updated")
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[6])  # "Updating Career DNA"

    if not analysis.insufficient_content:
        for skill in skills:
            profile.evidence_graph.append(
                EvidenceRecord(
                    id=str(uuid.uuid4()), text=f"{skill.skill} ({skill.category}) — {skill.evidence}",
                    source="github", relation="supports", created_at=now,
                )
            )
            profile.notebook_entries.append(
                NotebookEntry(
                    id=str(uuid.uuid4()), kind="observation",
                    text=f"Demonstrated {skill.category.lower()} through {skill.skill}.",
                    source="github", created_at=now,
                )
            )
        profile.notebook_entries.append(
            NotebookEntry(
                id=str(uuid.uuid4()), kind="observation", text=analysis.overall_summary,
                source="github", created_at=now,
            )
        )
        if skills:
            artifacts_updated.append("Skill Evidence Recorded")
        artifacts_updated.append("Discovery Notebook Updated")

        # V12 — Investigation History needs a genuinely reopenable record,
        # which GitHub Intelligence never persisted before; additive only,
        # no change to the reasoning/evidence above.
        profile.github_investigations.append(
            GitHubInvestigationRecord(
                id=str(uuid.uuid4()), url=url, owner=identifier.owner, repo=identifier.repo,
                name=facts.reasoning.name, description=facts.reasoning.description,
                primary_language=facts.reasoning.primary_language, languages=facts.reasoning.languages,
                topics=facts.reasoning.topics, license=facts.reasoning.license,
                stars=facts.display.stars, forks=facts.display.forks, last_activity=facts.display.last_activity,
                skills=[GitHubSkillRecord(skill=s.skill, category=s.category, evidence=s.evidence) for s in skills],
                overall_summary=analysis.overall_summary, project_purpose=analysis.project_purpose,
                technical_complexity=analysis.technical_complexity, problem_solving=analysis.problem_solving,
                code_organization=analysis.code_organization, technology_breadth=analysis.technology_breadth,
                documentation_quality=analysis.documentation_quality, learning_signals=analysis.learning_signals,
                engineering_maturity=analysis.engineering_maturity, research_orientation=analysis.research_orientation,
                ai_ml_signals=analysis.ai_ml_signals, created_at=now,
            )
        )
        artifacts_updated.append("Investigation History Updated")
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[7])  # "Updating Discovery Notebook"

    evidence_added = bool(artifacts_updated)
    MissionOrchestrator.complete(mission)
    mission.record_stage(GITHUB_INVESTIGATION_STAGES[8])  # "Investigation Complete"

    return GitHubInvestigationResult(
        url=url, status=tool_result.status, repo_facts=facts, skills=skills, analysis=analysis,
        explanation=analysis.insufficient_content_reason, stages=mission.stage_log,
        evidence_added=evidence_added, mission=mission, artifacts_updated=artifacts_updated,
    )

from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.agents.specialized.discovery.github_evidence import ReasoningFacts, SkillFinding
from aureon.services.llm.schemas import LLMMessage

#: The single most important rule for this prompt — repeated here rather
#: than assumed, since accidentally leaking a popularity signal into the
#: reasoning would be exactly the kind of subtle fabrication this whole
#: product refuses to allow.
POPULARITY_EXCLUSION_RULE = (
    "You have NOT been given stars, forks, or commit counts, and you must never assume or "
    "estimate them. Popularity and activity metrics say nothing about engineering ability and "
    "must never influence any part of your analysis. Reason only from repository structure, "
    "technologies actually used, dependencies, build configuration, documentation quality, "
    "testing presence, CI configuration, architectural organization, and project completeness."
)


def _facts_block(facts: ReasoningFacts, skills: list[SkillFinding]) -> str:
    lines = [
        f"Repository: {facts.owner}/{facts.name}",
        f"Description: {facts.description or 'None provided'}",
        f"Primary language: {facts.primary_language or 'Unknown'}",
        f"Languages used: {', '.join(facts.languages) or 'None detected'}",
        f"Topics: {', '.join(facts.topics) or 'None'}",
        f"License: {facts.license or 'None'}",
        f"README present: {facts.readme_present} (length: {facts.readme_length} characters)",
        f"Root files: {', '.join(facts.root_files) or 'None'}",
        f"Build/package files found: {', '.join(facts.build_files_found) or 'None'}",
        f"Has CI configuration (.github/workflows): {facts.has_ci}",
        f"Has a tests directory: {facts.has_tests}",
        f"Declared dependencies: {', '.join(facts.dependencies) or 'None detected'}",
    ]
    if skills:
        lines.append("Skills detected from real repository evidence:")
        for s in skills:
            lines.append(f"  - {s.skill} ({s.category}) — {s.evidence}")
    else:
        lines.append("No specific skills matched the known technology list.")
    return "\n".join(lines)


def build_github_investigation_messages(
    *, facts: ReasoningFacts, skills: list[SkillFinding]
) -> list[LLMMessage]:
    system = (
        "You are Aureon's Discovery Agent, running GitHub Intelligence — an engineering "
        "portfolio investigation grounded entirely in real repository data. You evaluate what "
        "the student has actually built, never what they claim.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        f"{POPULARITY_EXCLUSION_RULE}\n\n"
        "Cover: project purpose, technical complexity, problem solving, code organization, "
        "technology breadth, documentation quality, learning signals, engineering maturity, "
        "research orientation, and AI/ML signals — each a short, grounded sentence. If the "
        "repository facts are too thin to responsibly assess any of this, set "
        "insufficient_content to true and explain why, rather than filling gaps with "
        "plausible-sounding guesses. Always respond by calling the record_github_investigation "
        "tool."
    )
    context = _facts_block(facts, skills)
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="What does this repository show about this student's engineering ability?"),
    ]

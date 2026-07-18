"""Responsibility: continuous long-term guidance — "what's the single
highest-impact next action for this student?" Owns: ``JourneyGuidance``
and ``guide()``'s thin, real reuse of ``ProgressReport.next_priorities``.
Does NOT own: Growth's own priority computation
(``agents/specialized/growth/evidence_summary.py``/``reasoning.py`` —
untouched); no cross-Career-Memory-domain override table yet (extension
point — why: nothing else produces real signal through Build
Orchestrator in this foundation yet, since Network/Portfolio are inert
placeholders; when: once a future milestone gives them real workflows;
who: that future milestone). Consumed by: ``BuildOrchestrator`` only.

Always at most one recommendation, never a fabricated one — returns
``None`` when there isn't enough real signal, mirroring
``insufficient_evidence`` used elsewhere in this codebase.
"""

from dataclasses import dataclass
from enum import StrEnum

from aureon.domain.models.career_memory import CareerMemory
from aureon.domain.models.opportunity_fit import OpportunityFitResult
from aureon.domain.models.progress_report import ProgressReport


class JourneyActionType(StrEnum):
    BUILD_PROJECT = "build_project"
    APPLY_INTERNSHIP = "apply_internship"
    CONTACT_MENTOR = "contact_mentor"
    IMPROVE_DOCUMENTATION = "improve_documentation"
    PRACTICE_INTERVIEW = "practice_interview"
    COMPLETE_TODAYS_MISSION = "complete_todays_mission"


#: A real keyword heuristic over Growth's own free-text priority action,
#: not invented structure — same "vary presentation via keywords over
#: real text" pattern already used by the frontend's MissionCard
#: category labels. First match wins; nothing here is LLM-invented.
_ACTION_KEYWORDS: list[tuple[JourneyActionType, tuple[str, ...]]] = [
    (JourneyActionType.BUILD_PROJECT, ("build", "project", "create", "prototype", "ship")),
    (JourneyActionType.APPLY_INTERNSHIP, ("internship", "apply", "application")),
    (JourneyActionType.CONTACT_MENTOR, ("mentor", "expert", "guidance")),
    (JourneyActionType.IMPROVE_DOCUMENTATION, ("document", "readme", "portfolio", "resume")),
    (JourneyActionType.PRACTICE_INTERVIEW, ("interview", "practice")),
]


def _classify_action(text: str) -> JourneyActionType:
    lowered = text.lower()
    for action_type, keywords in _ACTION_KEYWORDS:
        if any(keyword in lowered for keyword in keywords):
            return action_type
    # Honest fallback — no keyword matched, not a guess dressed up as one
    # of the more specific categories.
    return JourneyActionType.COMPLETE_TODAYS_MISSION


#: Phase 2 Stage 2 — Opportunity Hub's "not ready" preparation
#: classifier. Keyword-matches the exact gap-label wording
#: agents/specialized/opportunity/scoring.py's requirements tally
#: produces ("skill"/"portfolio"/"academic"/"location") — a documented
#: cross-module wording dependency. Reuses the existing
#: JourneyActionType enum; no new member needed.
_PREPARATION_KEYWORDS: list[tuple[JourneyActionType, tuple[str, ...]]] = [
    (JourneyActionType.BUILD_PROJECT, ("skill", "project")),
    (JourneyActionType.IMPROVE_DOCUMENTATION, ("portfolio", "evidence", "documentation")),
    (JourneyActionType.CONTACT_MENTOR, ("academic", "eligibility", "location")),
]


def _classify_preparation_action(fit: OpportunityFitResult) -> JourneyActionType:
    combined = " ".join(fit.gaps).lower()
    for action_type, keywords in _PREPARATION_KEYWORDS:
        if any(keyword in combined for keyword in keywords):
            return action_type
    # Honest default — "not ready" always implies something concrete to build.
    return JourneyActionType.BUILD_PROJECT


@dataclass(frozen=True)
class JourneyGuidance:
    action_type: JourneyActionType
    reason: str
    evidence: list[str]
    priority_score: float


class JourneyGuidanceEngine:
    def guide(
        self,
        *,
        progress_report: ProgressReport | None,
        career_memory: CareerMemory,
        opportunity_fit: OpportunityFitResult | None = None,
    ) -> JourneyGuidance | None:
        """Stage 1 scope is deliberately thin: reuse Growth's own top
        priority, already real and evidence-cited. ``career_memory`` is
        accepted now (not yet used by the Stage 1 path) so a future
        milestone can add cross-domain rules without changing this
        method's signature.

        Phase 2 Stage 2 (Opportunity Hub) addition: ``opportunity_fit``
        is checked first, and only overrides Stage 1's behavior when the
        student isn't ready for a specific opportunity — existing
        callers that never pass it keep their exact original behavior.
        """
        if opportunity_fit is not None and opportunity_fit.readiness_label == "not_ready":
            gap = opportunity_fit.highest_impact_gap
            reason = (
                f"You currently meet {opportunity_fit.requirements_met} of "
                f"{opportunity_fit.requirements_total} requirements for this opportunity"
            )
            if gap is not None:
                reason += f" — {gap.recommended_action}"
            else:
                reason += " — strengthening these first will make a real application far stronger."
            return JourneyGuidance(
                action_type=_classify_preparation_action(opportunity_fit),
                reason=reason,
                evidence=list(opportunity_fit.gaps),
                priority_score=round(1.0 - opportunity_fit.overall_score, 4),
            )

        if progress_report is None or progress_report.insufficient_evidence:
            return None
        if not progress_report.next_priorities:
            return None

        top = min(progress_report.next_priorities, key=lambda p: p.rank)
        return JourneyGuidance(
            action_type=_classify_action(top.action),
            reason=top.action,
            evidence=[top.evidence],
            priority_score=1.0 / top.rank if top.rank > 0 else 1.0,
        )

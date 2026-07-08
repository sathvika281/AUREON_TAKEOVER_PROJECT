from aureon.agents.specialized.decision.confidence import evidence_strength_label
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.schemas import DecisionTimelineMilestoneDTO, DecisionTimelineResponse

"""Decision Timeline — a pure read-aggregation over already-persisted
data (notebook_entries, career_comparisons, parallel_universe_scenarios).
No new writer, no LLM call: every milestone traces to something the
system already stored for a real reason, nothing is fabricated here."""


def build_decision_timeline(profile: StudentProfile) -> DecisionTimelineResponse:
    milestones: list[DecisionTimelineMilestoneDTO] = []

    for entry in profile.notebook_entries:
        if entry.kind == "observation":
            milestones.append(
                DecisionTimelineMilestoneDTO(kind="career_dna_change", text=entry.text, created_at=entry.created_at)
            )
        elif entry.kind == "belief_revision" and entry.related_hypothesis:
            milestones.append(
                DecisionTimelineMilestoneDTO(kind="hypothesis_update", text=entry.text, created_at=entry.created_at)
            )
        elif entry.kind == "belief_revision" and entry.related_career:
            milestones.append(
                DecisionTimelineMilestoneDTO(kind="career_candidate", text=entry.text, created_at=entry.created_at)
            )

    for comparison in profile.career_comparisons:
        names = " vs ".join(comparison.career_names.get(cid, cid) for cid in comparison.career_ids)
        milestones.append(
            DecisionTimelineMilestoneDTO(
                kind="comparison", text=f"Compared {names}", created_at=comparison.created_at
            )
        )

    for scenario in profile.parallel_universe_scenarios:
        names = " vs ".join(b.career_name for b in scenario.branches)
        milestones.append(
            DecisionTimelineMilestoneDTO(
                kind="parallel_universe", text=f"Simulated futures: {names}", created_at=scenario.created_at
            )
        )

    milestones.sort(key=lambda m: m.created_at)

    return DecisionTimelineResponse(
        milestones=milestones,
        current_direction_summary=_current_direction_summary(profile),
    )


def _current_direction_summary(profile: StudentProfile) -> str:
    shortlisted = [
        c for c in profile.career_candidates if c.is_shortlisted and c.status != "discarded"
    ]
    if shortlisted:
        return f"Currently shortlisted: {shortlisted[0].career_name}"

    active = [c for c in profile.career_candidates if c.status != "discarded"]
    if active:
        top = max(active, key=lambda c: c.confidence)
        return f"Currently exploring: {top.career_name} ({evidence_strength_label(top.confidence)})"

    return "No clear direction yet — still early in exploration."

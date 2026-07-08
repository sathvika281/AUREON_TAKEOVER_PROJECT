from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.agents.specialized.growth.evidence_summary import ProgressEvidenceBundle
from aureon.services.llm.schemas import LLMMessage


def _dimensions_block(bundle: ProgressEvidenceBundle) -> str:
    lines = ["Progress dimensions (direction and evidence are already computed — do not restate them as your own claim, only explain why):"]
    for dim in bundle.dimensions:
        lines.append(f"- {dim.key} ({dim.label}): direction={dim.direction}")
        for fact in dim.evidence_summary:
            lines.append(f"    {fact}")
    return "\n".join(lines)


def _timeline_block(bundle: ProgressEvidenceBundle) -> str:
    lines = ["Timeline (already computed):"]
    for window in bundle.timeline:
        lines.append(f"- {window.label}: {window.description}")
    return "\n".join(lines)


def build_progress_messages(bundle: ProgressEvidenceBundle) -> list[LLMMessage]:
    system = (
        "You are Aureon's Progress Agent, running Progress Intelligence — the student's "
        "continuous growth analysis. This is NOT a checklist or a streak counter: you reason "
        "about what the evidence below actually shows, you never calculate anything yourself.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "For each dimension, explain WHY it moved the way its direction already indicates — "
        "never contradict the given direction, never invent a statistic or percentage that "
        "isn't in the evidence below. growing_strengths and areas_slowing_down must each "
        "reference a specific dimension. next_priorities must be ranked (rank 1 = most "
        "important) and each action's evidence field must quote or closely paraphrase a real "
        "fact from the evidence above — never a generic tip like 'work harder' with no "
        "evidence behind it. Always respond by calling the record_progress_report tool."
    )
    context = "\n\n".join([_dimensions_block(bundle), _timeline_block(bundle)])
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="How is my progress going, and what should I focus on next?"),
    ]

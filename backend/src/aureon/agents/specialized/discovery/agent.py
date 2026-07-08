import uuid
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage

from aureon.agents.base import BaseAgent
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.discovery import evidence  # noqa: F401  (registers evidence sources)
from aureon.agents.specialized.discovery.confidence import effective_confidence
from aureon.agents.specialized.discovery.evidence.registry import EvidenceSourceRegistry
from aureon.agents.specialized.discovery.hypothesis_lifecycle import compute_status
from aureon.agents.specialized.discovery.prompts import build_discovery_messages
from aureon.agents.specialized.discovery.schemas import DISCOVERY_TOOL, DiscoveryTurnOutput
from aureon.agents.specialized.discovery.tools import (
    ChatExportReaderTool,
    DocumentReaderTool,
    ImageUnderstandingTool,
    PDFReaderTool,
    ResumeReaderTool,
)
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.core.config import get_settings
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.career_hypothesis import CareerHypothesis
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import ConfidenceSnapshot, StudentProfile
from aureon.domain.services.evidence_recording import record_new_evidence
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName, Mode

#: Deterministic cap on how many times the Why Engine may probe the same
#: topic. The LLM is told this in the prompt, but the code enforces it —
#: mirrors the confidence-gate pattern of LLM freedom bounded by a hard
#: backstop.
WHY_PROBE_DEPTH_CAP = 2

#: Confidence must move at least this much turn-to-turn to count as a
#: belief-revision-worthy shift, not just noise.
CONFIDENCE_DELTA_THRESHOLD = 0.15


def _new_id() -> str:
    return str(uuid.uuid4())


def _confidence_label(score: float | None) -> str:
    s = score if score is not None else 0.3
    if s >= 0.7:
        return "High"
    if s >= 0.4:
        return "Medium"
    return "Emerging"


def _latest_human_message(messages: list) -> str | None:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return None


def _record_trait_evidence_and_observations(
    profile: StudentProfile, updates: list, now: datetime
) -> None:
    """Every Career DNA update this turn is *meant* to be new or changed
    information (the LLM is instructed to only emit an update when
    there's real signal), but in practice it sometimes re-states an
    unchanged trait verbatim — observed live during verification. Skip
    recording evidence/observations for a trait whose score and summary
    are identical to what's already there, so the Notebook doesn't fill
    up with duplicate entries for the same unchanged reading."""
    for update in updates:
        existing = profile.career_dna.traits.get(update.trait)
        unchanged = (
            existing is not None
            and existing.summary == update.summary
            and existing.score == update.score
        )
        if unchanged:
            continue

        profile.career_dna.apply_update(trait=update.trait, score=update.score, summary=update.summary)
        profile.evidence_graph.append(
            EvidenceRecord(
                id=_new_id(),
                text=update.rationale,
                source="conversation",
                related_trait=update.trait,
                relation="supports",
                created_at=now,
            )
        )
        profile.notebook_entries.append(
            NotebookEntry(
                id=_new_id(),
                kind="observation",
                text=update.summary,
                source="conversation",
                related_trait=update.trait,
                confidence_label=_confidence_label(update.score),
                created_at=now,
            )
        )


def _upsert_hypotheses(profile: StudentProfile, updates: list, *, mode: str, now: datetime) -> None:
    """The Hypothesis Engine's lifecycle: new ideas are created
    Investigating/Growing, confidence shifts of >=0.15 or a lifecycle
    status change get recorded as a belief-revision Notebook entry, and a
    hypothesis absent from this turn's output is marked Discarded (kept,
    not deleted, so its history survives) rather than silently vanishing.
    """
    by_name = {h.career_name: h for h in profile.career_hypotheses}
    updated_names = {u.career_name for u in updates}

    # The LLM returns the complete current set of active hypotheses each
    # turn (same assumption the "dropped means discarded" logic below
    # relies on) — the leading one among them is the only candidate for
    # "validated" this turn.
    top_name = max(updates, key=lambda u: u.confidence).career_name if updates else None

    for update in updates:
        record_new_evidence(
            profile,
            related_hypothesis=update.career_name,
            items=update.supporting_evidence,
            relation="supports",
            now=now,
        )
        record_new_evidence(
            profile,
            related_hypothesis=update.career_name,
            items=update.contradicting_evidence,
            relation="contradicts",
            now=now,
        )

        new_status = compute_status(
            confidence=update.confidence,
            mode=mode,
            is_top_hypothesis=update.career_name == top_name,
        )
        existing = by_name.get(update.career_name)

        if existing is None:
            reason = "Aureon started testing a new idea."
            profile.career_hypotheses.append(
                CareerHypothesis(
                    career_name=update.career_name,
                    confidence=update.confidence,
                    missing_evidence=update.missing_evidence,
                    status=new_status,
                    transition_reason=reason,
                    updated_at=now,
                )
            )
            profile.notebook_entries.append(
                NotebookEntry(
                    id=_new_id(),
                    kind="belief_revision",
                    text=f"Aureon started testing a new idea: {update.career_name}.",
                    source="conversation",
                    related_hypothesis=update.career_name,
                    previous_state="none",
                    new_evidence=update.supporting_evidence[0] if update.supporting_evidence else "",
                    updated_belief=f"Considering {update.career_name}",
                    reason=reason,
                    created_at=now,
                )
            )
            continue

        old_confidence, old_status = existing.confidence, existing.status
        delta = update.confidence - old_confidence
        transitioned = new_status != old_status or abs(delta) >= CONFIDENCE_DELTA_THRESHOLD

        if transitioned:
            if delta >= CONFIDENCE_DELTA_THRESHOLD:
                reason = "New evidence strengthened this hypothesis."
                belief_text = f"This strengthened: {update.career_name}."
                new_evidence_text = update.supporting_evidence[0] if update.supporting_evidence else ""
            elif delta <= -CONFIDENCE_DELTA_THRESHOLD:
                gap = update.missing_evidence[0] if update.missing_evidence else "some uncertainty"
                reason = f"{gap.capitalize()} is still unclear, which weakened confidence."
                belief_text = f"Aureon is reconsidering {update.career_name} — {gap} still isn't clear."
                new_evidence_text = (
                    update.contradicting_evidence[0] if update.contradicting_evidence else ""
                )
            else:
                reason = f"Status moved from {old_status} to {new_status}."
                belief_text = f"{update.career_name} is now {new_status}."
                new_evidence_text = ""

            profile.notebook_entries.append(
                NotebookEntry(
                    id=_new_id(),
                    kind="belief_revision",
                    text=belief_text,
                    source="conversation",
                    related_hypothesis=update.career_name,
                    previous_state=old_status,
                    new_evidence=new_evidence_text,
                    updated_belief=f"{update.career_name} ({new_status})",
                    reason=reason,
                    created_at=now,
                )
            )
            existing.transition_reason = reason

        existing.confidence = update.confidence
        existing.missing_evidence = update.missing_evidence
        existing.status = new_status
        existing.updated_at = now

    for hypothesis in profile.career_hypotheses:
        if hypothesis.career_name not in updated_names and hypothesis.status != "discarded":
            previous_status = hypothesis.status
            reason = "No longer supported by the recent conversation."
            hypothesis.status = "discarded"
            hypothesis.transition_reason = reason
            hypothesis.updated_at = now
            profile.notebook_entries.append(
                NotebookEntry(
                    id=_new_id(),
                    kind="belief_revision",
                    text=f"Aureon set aside the idea of {hypothesis.career_name} for now.",
                    source="conversation",
                    related_hypothesis=hypothesis.career_name,
                    previous_state=previous_status,
                    new_evidence="",
                    updated_belief="discarded",
                    reason=reason,
                    created_at=now,
                )
            )


class DiscoveryAgent(BaseAgent):
    """Discovers interests, strengths, values and persona through
    conversation, reflection and behavior rather than direct questions;
    aggregates evidence from every registered ``EvidenceSource`` and
    maintains the student's Career DNA, Career Hypotheses, Evidence
    Graph, and Discovery Notebook — all persisted server-side so they
    survive a refresh or a new device.

    Never gated by the confidence safety floor itself — it is the agent
    that raises confidence in the first place, so it must always be
    reachable regardless of the current score.
    """

    name = AgentName.DISCOVERY.value
    description = (
        "Discovers interests/strengths/values/persona through conversation, "
        "reflection and behavior; maintains Career DNA, tentative career "
        "hypotheses, and the Evidence Graph behind both; estimates the "
        "confidence score used to gate recommendation-stage agents."
    )

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        stages = AGENT_EXECUTION_STAGES[self.name]
        executed_stages: list[str] = []
        profile = state["student_profile"] or StudentProfile(student_id=state["student_id"])
        previous_pending_prompt = state.get("pending_reflection_prompt")
        student_message = _latest_human_message(state["messages"])

        # Discovery's own document-understanding toolset — attempted every
        # turn (honest not_connected today, since there's no upload
        # pipeline yet). The stage is recorded because the tool call
        # genuinely happened, not because a resume was found.
        tool_results = [
            await run_tool_safely(ResumeReaderTool()),
            await run_tool_safely(DocumentReaderTool()),
            await run_tool_safely(PDFReaderTool()),
            await run_tool_safely(ImageUnderstandingTool()),
            await run_tool_safely(ChatExportReaderTool()),
        ]
        executed_stages.append(stages[0])  # "Reading Resume"

        llm_messages = build_discovery_messages(
            conversation_messages=state["messages"],
            career_dna=profile.career_dna,
            hypotheses=profile.career_hypotheses,
            evidence_graph=profile.evidence_graph,
            why_probe_state=state.get("why_probe_state") or {},
            pending_reflection_prompt=previous_pending_prompt,
        )
        response = await llm.complete(
            llm_messages, tools=[DISCOVERY_TOOL], tool_choice="required"
        )
        output = self._parse_output(response, previous_confidence=profile.confidence_score)

        # Why Engine depth cap — deterministic override, not LLM-trusted.
        why_probe_state = dict(state.get("why_probe_state") or {})
        if output.probe.is_probing:
            topic = output.probe.topic or "general"
            depth_so_far = why_probe_state.get(topic, 0) + 1
            if depth_so_far > WHY_PROBE_DEPTH_CAP:
                output.probe.is_probing = False
            else:
                why_probe_state[topic] = depth_so_far
        state["why_probe_state"] = why_probe_state

        # Reflection Journal: record the answer to last turn's prompt, if any.
        answered_reflection: dict | None = None
        if previous_pending_prompt and student_message is not None:
            profile.reflection_journal.append(
                ReflectionEntry(
                    prompt=previous_pending_prompt,
                    response=student_message,
                    answered_at=datetime.now(timezone.utc),
                )
            )
            answered_reflection = {
                "prompt": previous_pending_prompt,
                "response": student_message,
            }
            executed_stages.append(stages[1])  # "Analyzing Reflection Journal"

        # Recorded from the output that's about to drive the remaining
        # persistence steps below, not after the fact — mirrors the real
        # conditions each of those steps actually runs under.
        executed_stages.append(stages[2])  # "Extracting Evidence" — the EvidenceSourceRegistry loop below always runs
        if output.career_dna_updates:
            executed_stages.append(stages[3])  # "Updating Career DNA"
        executed_stages.append(stages[4])  # "Building Discovery Report" — a report is always built

        # Persist this turn's structured output first — EvidenceSources and
        # the Career Evidence Engine (API/UI transparency) both read it.
        state["agent_outputs"][self.name] = AgentOutput(
            agent_name=self.name,
            payload={
                "extracted_evidence": [e.model_dump() for e in output.extracted_evidence],
                "answered_reflection": answered_reflection,
                "career_dna_updates": [u.model_dump() for u in output.career_dna_updates],
                "hypotheses": [h.model_dump() for h in output.hypotheses],
                "suggested_activity": (
                    output.suggested_activity.model_dump()
                    if output.suggested_activity
                    else None
                ),
                "probe": output.probe.model_dump(),
                "execution_stages": executed_stages,
                "tool_results": [r.model_dump() for r in tool_results],
            },
        )

        for source_cls in EvidenceSourceRegistry.all():
            events = await source_cls().extract(state)
            profile.exploration_history.extend(events)

        # Confidence must be settled before the hypothesis lifecycle runs,
        # since "validated" depends on the recommendation-mode boundary.
        confidence = effective_confidence(
            output.confidence_score, len(profile.exploration_history)
        )
        profile.confidence_score = confidence
        profile.confidence_history.append(
            ConfidenceSnapshot(score=confidence, source_agent=self.name)
        )
        state["confidence_score"] = confidence
        settings = get_settings()
        mode = (
            Mode.RECOMMENDATION.value
            if confidence >= settings.min_recommendation_confidence
            else Mode.EXPLORATION.value
        )
        state["mode"] = mode

        now = datetime.now(timezone.utc)
        _record_trait_evidence_and_observations(profile, output.career_dna_updates, now)
        _upsert_hypotheses(profile, output.hypotheses, mode=mode, now=now)

        state["messages"] = [AIMessage(content=output.reply_to_student)]
        state["pending_reflection_prompt"] = output.reflection_prompt

        profile.updated_at = now
        state["student_profile"] = profile
        state["agent_history"].append(self.name)
        return state

    @staticmethod
    def _parse_output(response, *, previous_confidence: float) -> DiscoveryTurnOutput:
        if not response.tool_calls:
            # Defensive fallback: the model ignored tool_choice="required".
            # Treat any free-text content as the reply and make no other
            # claims — never fabricate evidence/DNA/hypotheses that weren't
            # actually produced. Confidence holds steady rather than being
            # reset, since this is a parsing gap, not new negative evidence.
            return DiscoveryTurnOutput(
                reply_to_student=response.content or "Could you tell me more about that?",
                probe={"is_probing": False},
                confidence_score=previous_confidence,
            )
        return DiscoveryTurnOutput.model_validate(response.tool_calls[0].arguments)

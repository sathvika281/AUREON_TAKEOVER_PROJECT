from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_comparison import (
    CareerComparison,
    ComparisonDimension,
    ParallelUniverseBranch,
    ParallelUniverseScenario,
)
from aureon.domain.models.career_dna import CareerDNA, TraitSignal
from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.career_hypothesis import CareerHypothesis
from aureon.domain.models.decision_memory import DecisionMemoryEntry
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.mentor_handoff import MentorHandoff
from aureon.domain.models.mentor_match import CollegeMatch, MentorMatch
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import (
    CareerInteraction,
    ConfidenceSnapshot,
    ExplorationEvent,
    LearningProgress,
    StudentProfile,
)

#: Every custom Pydantic model that can end up nested inside AureonState
#: (directly on student_profile, or in agent_outputs) needs to be
#: explicitly allowlisted for msgpack checkpoint (de)serialization —
#: otherwise LangGraph logs a "will be blocked in a future version"
#: warning per the permissive default and will eventually refuse to load
#: checkpoints containing them.
_ALLOWED_MSGPACK_MODULES = [
    StudentProfile,
    CareerDNA,
    TraitSignal,
    CareerHypothesis,
    ReflectionEntry,
    MentorHandoff,
    AgentOutput,
    ConfidenceSnapshot,
    ExplorationEvent,
    CareerInteraction,
    LearningProgress,
    NotebookEntry,
    EvidenceRecord,
    CareerCandidate,
    CareerExplorationEvent,
    CareerComparison,
    ComparisonDimension,
    ParallelUniverseBranch,
    ParallelUniverseScenario,
    MentorMatch,
    CollegeMatch,
    DecisionMemoryEntry,
]


@lru_cache
def get_checkpointer() -> MemorySaver:
    """In-process checkpointer for this scaffold phase; ``conversation_id``
    doubles as the LangGraph ``thread_id``. Swapping to a durable backend
    (e.g. ``PostgresSaver`` from ``langgraph-checkpoint-postgres``, pointed
    at the Supabase connection string) later is a one-line change here —
    nothing else in the orchestrator depends on which backend is used.
    Deferred deliberately: in-memory persistence is correct for local
    development and is lost on restart, which is acceptable until the
    persistence-hardening module.
    """
    serde = JsonPlusSerializer(allowed_msgpack_modules=_ALLOWED_MSGPACK_MODULES)
    return MemorySaver(serde=serde)

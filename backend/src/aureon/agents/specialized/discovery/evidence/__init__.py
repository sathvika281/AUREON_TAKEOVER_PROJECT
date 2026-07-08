# Importing this package registers every EvidenceSource with
# EvidenceSourceRegistry via EvidenceSource.__init_subclass__ side effects
# — same pattern as agents/specialized/__init__.py, one level down.
#
# Future sources (micro-challenge completion, behavioral patterns, student
# feedback, mentor feedback, ...) are added by creating one new module in
# this package and importing it here.

from aureon.agents.specialized.discovery.evidence.conversation import (  # noqa: F401
    ConversationEvidenceSource,
)
from aureon.agents.specialized.discovery.evidence.reflection import (  # noqa: F401
    ReflectionEvidenceSource,
)

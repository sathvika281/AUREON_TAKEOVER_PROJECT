# Importing this package registers the seeded Knowledge Base provider
# (the first real OpportunityProvider) via register_provider(...) below —
# same "import the package to wire it up" convention as
# agents/specialized/__init__.py. A future provider (e.g. a
# DevpostProvider) is a new file implementing the same protocol plus one
# register_provider(...) call here — zero edits to OpportunityAgent or
# opportunity_objective_plans.py.

from aureon.agents.specialized.opportunity.providers.registry import register_provider
from aureon.agents.specialized.opportunity.providers.seeded import SeededKnowledgeBaseProvider

register_provider(SeededKnowledgeBaseProvider())

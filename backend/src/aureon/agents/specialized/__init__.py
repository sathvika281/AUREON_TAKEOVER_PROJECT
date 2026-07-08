# Importing this package registers every specialized agent with
# AgentRegistry via BaseAgent.__init_subclass__ side effects. The
# orchestrator graph (agents/orchestrator/graph.py) builds itself entirely
# from AgentRegistry.describe_all() and never imports these modules
# directly.
#
# Adding a future agent (Research, Scholarship, Resume, Interview,
# Portfolio, Internship, Market Trends, ...) means: create one new module
# under agents/specialized/<name>/agent.py, add one import line below.
# Nothing else changes.

from aureon.agents.specialized.career_intelligence.agent import (  # noqa: F401
    CareerIntelligenceAgent,
)
from aureon.agents.specialized.decision.agent import DecisionAgent  # noqa: F401
from aureon.agents.specialized.discovery.agent import DiscoveryAgent  # noqa: F401
from aureon.agents.specialized.growth.agent import GrowthAgent  # noqa: F401
from aureon.agents.specialized.institution.agent import InstitutionAgent  # noqa: F401
from aureon.agents.specialized.mentor.agent import MentorAgent  # noqa: F401
from aureon.agents.specialized.opportunity.agent import OpportunityAgent  # noqa: F401
from aureon.agents.specialized.roadmap.agent import RoadmapAgent  # noqa: F401
from aureon.agents.specialized.skill_gap.agent import SkillGapAgent  # noqa: F401

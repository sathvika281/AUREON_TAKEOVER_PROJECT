# Importing this package registers today's real Build Orchestrator
# objectives (see default_objective_plans.py) via its module-level
# register_objective_plan(...) calls. Mirrors the existing
# agents/specialized/__init__.py convention: importing the package is
# what wires things up, not calling anything explicitly at startup.
from aureon.agents.foundation import default_objective_plans  # noqa: F401
from aureon.agents.foundation import opportunity_objective_plans  # noqa: F401

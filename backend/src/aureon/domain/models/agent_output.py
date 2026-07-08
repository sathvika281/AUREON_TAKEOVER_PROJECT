from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Generic scratch-output envelope every specialized agent writes into
    ``AureonState.agent_outputs[agent_name]``. Keeping this generic (rather
    than one Pydantic model per agent) is what lets new agents plug in
    without the shared state schema changing shape for every addition;
    each agent defines and interprets its own ``payload`` contents."""

    agent_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

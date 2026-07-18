from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

CircleResourceStatus = Literal["bookmarked", "completed"]


class CircleResourceProgress(BaseModel):
    """One student's bookmark/completion state on one composed Knowledge
    Circle resource. Composed resources are plain strings pulled from
    five different source models (``CareerWorld``, ``TopicResourceDomain``,
    ``Career``, ``Trend``, ``LifeMission``) with no stable id of their
    own, so identity here is the composite ``(circle_id, resource_type,
    resource_label)`` key — the only stable identity available. Same
    toggle simplicity as ``StudentProfile.saved_experts``, adapted for a
    resource that has no natural id.

    A third ``"want_to_explore"`` status was raised and explicitly
    deferred by the user as a future enhancement — not built now.
    """

    id: str
    circle_id: str
    resource_type: str
    resource_label: str
    status: CircleResourceStatus
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

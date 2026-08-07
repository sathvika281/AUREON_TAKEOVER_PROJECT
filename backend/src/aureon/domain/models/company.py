"""Responsibility: the Company Knowledge Base's own data shape. Company is
the connective tissue Career/Mentor/Opportunity/Trend all currently point
at as independent free-text `companies`/`organization` strings instead of
one real entity — see docs/AUREON_DATA_ARCHITECTURE.md §5.

Like Skill (see skill.py), Company describes real, verifiable
organizations — factual, not illustrative composite narrative — so it
carries no `source_note` disclaimer, for the same reason.

`organization_kind` deliberately reuses `OrganizationKind` from
`domain.models.opportunity` rather than defining a second, parallel
taxonomy — the real seeded `companies` data includes genuine
governments and NGOs alongside for-profit companies (e.g. "World Health
Organization", "Indian Foreign Service"), so a single "Company" label
with no distinction would misrepresent what these actually are.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from aureon.domain.models.opportunity import OrganizationKind

#: Only meaningful for organization_kind == "company" — left unset (None)
#: for governments, nonprofits, and universities rather than forcing a
#: category that doesn't honestly apply to them.
CompanySizeCategory = Literal["startup", "mid_size", "enterprise"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Company(BaseModel):
    """One entry in the Company Knowledge Base."""

    id: str
    name: str
    organization_kind: OrganizationKind
    #: Shares vocabulary with Career.industry so cross-entity filtering
    #: actually works, per the architecture doc's own explicit rationale.
    industry: str
    size_category: CompanySizeCategory | None = None
    what_they_do: str
    #: Real, verifiable reference only — never fetched/generated. None
    #: when no real domain is confidently known, rather than guessing one
    #: and risking a wrong logo.
    logo_url: str | None = None
    hiring_focus_areas: list[str] = Field(default_factory=list)
    notable_for: str = ""
    #: Mirrors Institution/Career's existing `is_partner` convention for
    #: any real future collaboration — not set for any row this sprint.
    is_partner: bool = False

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

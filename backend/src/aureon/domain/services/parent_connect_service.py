"""Responsibility: Parent Connect's career-view composition — combines
reusable `Career` fields with the new `ParentCareerGuide` row and real
`advice_for_parents`/`faqs` from every expert linked to this career.
Owns: `build_parent_career_view`. Never invents a parent-facing quote —
every piece of expert advice traces back to a real seeded `Mentor` row.
Consumed by: `api/v1/parent_connect.py`.
"""

from dataclasses import dataclass, field

from aureon.domain.models.career import Career, CareerFAQ, SalaryRange
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.parent_connect import ParentCareerGuide


@dataclass(frozen=True)
class ParentExpertAdvice:
    expert_id: str
    expert_name: str
    expert_profession: str
    advice_for_parents: str
    faqs: list[CareerFAQ] = field(default_factory=list)


@dataclass(frozen=True)
class ParentCareerView:
    career_id: str
    career_name: str
    one_liner: str
    required_education: str
    salary_ranges: list[SalaryRange] = field(default_factory=list)
    demand_2030: str = ""
    demand_2035: str = ""
    demand_2040: str = ""
    #: From `ParentCareerGuide` — parent-framed, never a duplicate of
    #: `Career.reality`/`Career.common_misconceptions`.
    common_misconceptions: list[str] = field(default_factory=list)
    earning_reality: str = ""
    career_stability: str = ""
    work_life_balance: str = ""
    growth_opportunities: str = ""
    educational_pathways: list[str] = field(default_factory=list)
    alternative_routes: list[str] = field(default_factory=list)
    global_demand: str = ""
    risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    expert_advice: list[ParentExpertAdvice] = field(default_factory=list)


def build_parent_career_view(
    career: Career, guide: ParentCareerGuide | None, experts_for_career: list[Mentor]
) -> ParentCareerView:
    expert_advice = [
        ParentExpertAdvice(
            expert_id=e.id, expert_name=e.name, expert_profession=e.profession,
            advice_for_parents=e.advice_for_parents, faqs=e.faqs,
        )
        for e in experts_for_career
        if e.advice_for_parents
    ]
    return ParentCareerView(
        career_id=career.id,
        career_name=career.name,
        one_liner=career.one_liner,
        required_education=career.reality.required_education,
        salary_ranges=career.reality.salary_ranges,
        demand_2030=career.future_lens.demand_2030,
        demand_2035=career.future_lens.demand_2035,
        demand_2040=career.future_lens.demand_2040,
        common_misconceptions=guide.common_misconceptions if guide else [],
        earning_reality=guide.earning_reality if guide else "",
        career_stability=guide.career_stability if guide else "",
        work_life_balance=guide.work_life_balance if guide else "",
        growth_opportunities=guide.growth_opportunities if guide else "",
        educational_pathways=guide.educational_pathways if guide else [],
        alternative_routes=guide.alternative_routes if guide else [],
        global_demand=guide.global_demand if guide else "",
        risks=guide.risks if guide else [],
        opportunities=guide.opportunities if guide else [],
        expert_advice=expert_advice,
    )

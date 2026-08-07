"""One-time seed script for Sprint 1's Skill Knowledge Base
(docs/SPRINT_1.md). Run via: python -m aureon.scripts.seed_skills

Every skill below is derived directly from the real `required_skills`
text already sitting in the 27 seeded Career rows (`reality.required_skills`)
— not invented in parallel. Depth over breadth, per the sprint's explicit
scope: 23 real, well-defined skills across all four categories, each
covering a genuine cluster of near-duplicate free-text phrases found in
the real data (e.g. "statistics" / "statistical analysis" / "data
analysis" all canonicalize to one real `statistical_analysis` skill).
Idempotent: upserts by id, safe to re-run.
"""

import asyncio

from aureon.domain.models.skill import Skill
from aureon.services.supabase.client import get_supabase_client

SKILLS: list[dict] = [
    # -- technical --
    {
        "id": "programming",
        "name": "Programming",
        "category": "technical",
        "description": "Writing and debugging code to build tools, analyze data, or automate a process.",
        "evidence_types_that_count": ["a completed project with real code", "a public repository with genuine commit history"],
    },
    {
        "id": "statistical_analysis",
        "name": "Statistical Analysis",
        "category": "technical",
        "description": "Using statistics and structured data analysis to find real patterns and support a conclusion, not just eyeball a spreadsheet.",
        "evidence_types_that_count": ["a completed project with real analysis", "a research methodology course"],
    },
    {
        "id": "data_visualization",
        "name": "Data Visualization",
        "category": "technical",
        "description": "Turning raw data into a chart or figure that actually communicates something true and clear to someone else.",
        "evidence_types_that_count": ["a completed project with a real published chart or dashboard"],
    },
    {
        "id": "gis_mapping",
        "name": "GIS & Mapping Tools",
        "category": "technical",
        "description": "Working with geographic information systems to analyze or present location-based data.",
        "evidence_types_that_count": ["a completed project using real GIS software"],
    },
    {
        "id": "simulation_modeling",
        "name": "Simulation & Systems Modeling",
        "category": "technical",
        "description": "Building a model of a real system to test how it behaves under different conditions before touching the real thing.",
        "evidence_types_that_count": ["a completed simulation or systems-design project"],
    },
    {
        "id": "experimental_design",
        "name": "Experimental Design & Research Methodology",
        "category": "technical",
        "description": "Designing a real study or experiment so its results can actually be trusted — controls, sample size, and honest limitations included.",
        "evidence_types_that_count": ["a completed research project", "a documented field study"],
    },
    # -- domain_knowledge --
    {
        "id": "policy_analysis",
        "name": "Policy Analysis",
        "category": "domain_knowledge",
        "description": "Reading and evaluating a real policy or public program to understand what it actually does and who it affects.",
        "evidence_types_that_count": ["a completed policy-analysis project or brief"],
    },
    {
        "id": "regulatory_knowledge",
        "name": "Regulatory & Compliance Knowledge",
        "category": "domain_knowledge",
        "description": "Understanding the real rules a field operates under — healthcare data standards, financial compliance, or similar — well enough to work within them.",
        "evidence_types_that_count": ["a completed compliance-focused project", "a real internship or role touching regulated work"],
    },
    {
        "id": "genomics_molecular_biology",
        "name": "Genomics & Molecular Biology Fundamentals",
        "category": "domain_knowledge",
        "description": "A real working understanding of genetics and molecular biology, enough to reason about a genomics dataset or research question.",
        "evidence_types_that_count": ["a completed genomics or biology-focused project", "relevant coursework"],
    },
    {
        "id": "public_health_data_literacy",
        "name": "Public Health Data Literacy",
        "category": "domain_knowledge",
        "description": "Reading and reasoning honestly about population-level health data — not just individual clinical facts.",
        "evidence_types_that_count": ["a completed public-health data project"],
    },
    {
        "id": "linguistics_fundamentals",
        "name": "Linguistics Fundamentals",
        "category": "domain_knowledge",
        "description": "A real grounding in how language works structurally — useful for anything from computational linguistics to language-model evaluation.",
        "evidence_types_that_count": ["relevant coursework", "a completed linguistics-focused project"],
    },
    {
        "id": "clinical_reasoning",
        "name": "Clinical Reasoning & Patient Communication",
        "category": "domain_knowledge",
        "description": "Working through a real clinical situation methodically, and communicating it clearly and kindly to the patient it affects.",
        "evidence_types_that_count": ["real clinical or shadowing experience", "a mentor's real observation"],
    },
    {
        "id": "financial_reporting",
        "name": "Financial Reporting & Budget Management",
        "category": "domain_knowledge",
        "description": "Reading, preparing, or managing a real budget or financial report accurately.",
        "evidence_types_that_count": ["a completed project involving real budget or financial data"],
    },
    # -- soft_skill --
    {
        "id": "stakeholder_communication",
        "name": "Stakeholder Communication & Management",
        "category": "soft_skill",
        "description": "Keeping the different people who care about a project's outcome genuinely informed and aligned, not just updated.",
        "evidence_types_that_count": ["a mentor's real observation", "a completed group or team project"],
    },
    {
        "id": "cross_cultural_communication",
        "name": "Cross-Cultural Communication",
        "category": "soft_skill",
        "description": "Communicating clearly and respectfully across real differences in background, language, or context.",
        "evidence_types_that_count": ["real experience working across cultures or languages"],
    },
    {
        "id": "public_speaking_writing",
        "name": "Public Speaking & Written Communication",
        "category": "soft_skill",
        "description": "Explaining something clearly to a real audience, whether out loud or in writing — reports, briefs, grant writing, presentations.",
        "evidence_types_that_count": ["a real presentation given", "a piece of real written work shared publicly"],
    },
    {
        "id": "attention_to_detail",
        "name": "Attention to Detail",
        "category": "soft_skill",
        "description": "Catching the small things that actually matter — in documentation, data, or a plan — before they become a real problem.",
        "evidence_types_that_count": ["a mentor's real observation", "a completed project with genuinely careful documentation"],
    },
    {
        "id": "negotiation",
        "name": "Negotiation & Persuasion",
        "category": "soft_skill",
        "description": "Making a real case for something and finding genuine common ground, not just pushing harder.",
        "evidence_types_that_count": ["a mentor's real observation", "real experience in a negotiation-shaped role"],
    },
    {
        "id": "adaptability_resilience",
        "name": "Adaptability & Resilience",
        "category": "soft_skill",
        "description": "Staying genuinely effective when a real plan changes or a real setback happens, not just tolerating it.",
        "evidence_types_that_count": ["a real reflection on a genuine setback or change", "a mentor's real observation"],
    },
    {
        "id": "project_management",
        "name": "Project & Program Management",
        "category": "soft_skill",
        "description": "Actually keeping a real project moving — priorities, timelines, and people — not just tracking a task list.",
        "evidence_types_that_count": ["a completed project with real planning artifacts", "a mentor's real observation"],
    },
    {
        "id": "interviewing_research",
        "name": "Interviewing & Investigative Research",
        "category": "soft_skill",
        "description": "Asking real questions that get to what's actually true, and verifying what you're told rather than accepting it at face value.",
        "evidence_types_that_count": ["a completed project involving real interviews or investigation"],
    },
    # -- tool --
    {
        "id": "spreadsheet_erp_tools",
        "name": "Spreadsheet & ERP Tools",
        "category": "tool",
        "description": "Real fluency with spreadsheet or enterprise-resource-planning software for tracking data that matters.",
        "evidence_types_that_count": ["a completed project using real spreadsheet or ERP tools"],
    },
    {
        "id": "monitoring_observability_tools",
        "name": "Monitoring & Observability Tools",
        "category": "tool",
        "description": "Using real tooling to watch whether a system is actually working, not just assuming it is.",
        "evidence_types_that_count": ["a completed project using real monitoring tooling"],
    },
]

# Real free-text strings already sitting in careers.reality.required_skills,
# mapped to the canonical skill id above that genuinely represents them.
# Built directly from the actual seeded data, not guessed — see the audit
# in docs/SPRINT_1.md's Sprint 1 notes. Deliberately partial: not every
# raw phrase in the real data maps to a skill seeded this sprint (e.g.
# "discipline," "rapid learning" are real but don't yet have a canonical
# home) — depth over forced completeness.
REQUIRED_SKILL_ALIASES: dict[str, str] = {
    "programming": "programming",
    "programming (Python/R)": "programming",
    "coding ability": "programming",
    "debugging": "programming",
    "statistics": "statistical_analysis",
    "statistical analysis": "statistical_analysis",
    "data analysis": "statistical_analysis",
    "data-driven decision making": "statistical_analysis",
    "data visualization": "data_visualization",
    "GIS mapping": "gis_mapping",
    "GIS/mapping tools": "gis_mapping",
    "simulation tools": "simulation_modeling",
    "systems design": "simulation_modeling",
    "systems engineering": "simulation_modeling",
    "experimental design": "experimental_design",
    "research methodology": "experimental_design",
    "field research methods": "experimental_design",
    "policy analysis": "policy_analysis",
    "policy implementation": "policy_analysis",
    "public administration": "policy_analysis",
    "regulatory knowledge": "regulatory_knowledge",
    "regulatory literacy": "regulatory_knowledge",
    "regulatory compliance": "regulatory_knowledge",
    "regulatory analysis": "regulatory_knowledge",
    "privacy/compliance knowledge": "regulatory_knowledge",
    "healthcare data standards": "regulatory_knowledge",
    "genomics domain knowledge": "genomics_molecular_biology",
    "molecular biology fundamentals": "genomics_molecular_biology",
    "public health data literacy": "public_health_data_literacy",
    "linguistics fundamentals": "linguistics_fundamentals",
    "clinical reasoning": "clinical_reasoning",
    "patient communication": "clinical_reasoning",
    "financial reporting": "financial_reporting",
    "budget management": "financial_reporting",
    "donor reporting": "financial_reporting",
    "stakeholder communication": "stakeholder_communication",
    "stakeholder engagement": "stakeholder_communication",
    "stakeholder management": "stakeholder_communication",
    "stakeholder negotiation": "stakeholder_communication",
    "cross-functional communication": "stakeholder_communication",
    "cross-team communication": "stakeholder_communication",
    "cross-cultural communication": "cross_cultural_communication",
    "public speaking/writing": "public_speaking_writing",
    "scientific writing": "public_speaking_writing",
    "written briefing skills": "public_speaking_writing",
    "written/verbal communication": "public_speaking_writing",
    "report writing": "public_speaking_writing",
    "grant writing": "public_speaking_writing",
    "attention to detail": "attention_to_detail",
    "rigorous documentation": "attention_to_detail",
    "negotiation": "negotiation",
    "sales/persuasion": "negotiation",
    "adaptability": "adaptability_resilience",
    "resilience": "adaptability_resilience",
    "stress management": "adaptability_resilience",
    "patience": "adaptability_resilience",
    "project management": "project_management",
    "program management": "project_management",
    "resource prioritization": "project_management",
    "crisis management": "project_management",
    "interviewing": "interviewing_research",
    "investigative research": "interviewing_research",
    "evidence verification": "interviewing_research",
    "spreadsheet/ERP tools": "spreadsheet_erp_tools",
    "monitoring/observability tools": "monitoring_observability_tools",
}


async def seed() -> None:
    client = get_supabase_client()
    skills = [Skill.model_validate(s) for s in SKILLS]

    def _upsert() -> None:
        client.table("skills").upsert([s.model_dump(mode="json") for s in skills]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(skills)} skills.")


if __name__ == "__main__":
    asyncio.run(seed())

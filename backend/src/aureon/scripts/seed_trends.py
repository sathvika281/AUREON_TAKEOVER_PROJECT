"""One-time seed script for Explore Batch 1's Global Trends Knowledge
Base.

Run via: python -m aureon.scripts.seed_trends

A modest (~16), honestly-labeled set of illustrative composite trends
spanning all 7 categories — industry/market-level content, deliberately
distinct from any single career's own FutureLens narrative. Every entry
carries its own `source_note` honesty disclaimer (see
domain/models/trend.py) — never presented as live, currently-verified
labor-market data. Idempotent: upserts by id, safe to re-run.
"""

import asyncio

from aureon.domain.models.trend import Trend
from aureon.services.supabase.client import get_supabase_client

TRENDS: list[dict] = [
    {
        "id": "trend_applied_ai_engineering",
        "title": "Applied AI Engineering Keeps Expanding Across Industries",
        "category": "emerging_industry",
        "summary": "Roles that apply existing AI models to real business problems are growing faster than roles building foundational models.",
        "description": "Most organizations don't need to train new foundation models — they need people who can responsibly apply, evaluate, and integrate existing ones into real products. This has created a wide, fast-growing layer of applied AI roles across healthcare, finance, education, and manufacturing.",
        "affected_industries": ["technology", "healthcare", "finance", "manufacturing"],
        "affected_skills": ["applied machine learning", "prompt/systems evaluation", "responsible AI practices"],
        "regions": [],
        "time_horizon": "near_term",
    },
    {
        "id": "trend_traditional_data_entry_decline",
        "title": "Routine Data Entry Roles Continue a Long, Gradual Decline",
        "category": "declining_industry",
        "summary": "Manual, repetitive data entry work keeps shrinking as automation and better source-data capture spread.",
        "description": "This is a long-running, gradual shift rather than a sudden one — routine transcription and entry work has been declining for years as automation matures, and that pattern continues.",
        "affected_industries": ["administration", "finance"],
        "affected_skills": [],
        "regions": [],
        "time_horizon": "long_term",
    },
    {
        "id": "trend_brain_computer_interfaces",
        "title": "Brain-Computer Interface Research Is Moving From Lab to Early Real-World Trials",
        "category": "future_technology",
        "summary": "Neural-interface research is progressing from pure lab research toward small-scale real clinical trials.",
        "description": "Early clinical trials for assistive brain-computer interfaces (for conditions like paralysis) are genuinely underway at a handful of research institutions — still early-stage, not yet mainstream, but a real and active research direction.",
        "affected_industries": ["healthcare", "technology"],
        "affected_skills": ["computational neuroscience", "signal processing", "clinical research"],
        "regions": [],
        "time_horizon": "long_term",
    },
    {
        "id": "trend_ai_literacy_as_baseline_skill",
        "title": "Basic AI Literacy Is Becoming a Baseline Expectation, Not a Specialty",
        "category": "skill_shift",
        "summary": "Understanding how to work alongside AI tools is increasingly expected across many roles, not just technical ones.",
        "description": "Much like spreadsheet literacy became a baseline office skill, a working understanding of AI tools (what they're good at, where they fail, how to verify their output) is spreading well beyond technical roles.",
        "affected_industries": ["technology", "education", "finance", "administration"],
        "affected_skills": ["working with AI tools", "verifying AI-generated output", "prompt literacy"],
        "regions": [],
        "time_horizon": "near_term",
    },
    {
        "id": "trend_remote_hiring_normalization",
        "title": "Remote and Distributed Hiring Has Become a Lasting Norm, Not a Temporary Shift",
        "category": "hiring_shift",
        "summary": "Many companies that adopted remote hiring have kept it as a permanent practice rather than reverting.",
        "description": "For many knowledge-work roles, distributed/remote hiring has settled into a lasting norm rather than a temporary pandemic-era adjustment, meaningfully widening the real geographic pool of opportunities for students outside major hub cities.",
        "affected_industries": ["technology", "finance", "education"],
        "affected_skills": ["asynchronous communication", "self-directed work"],
        "regions": [],
        "time_horizon": "near_term",
    },
    {
        "id": "trend_ai_assisted_scientific_discovery",
        "title": "AI-Assisted Discovery Is Accelerating Materials and Drug Research",
        "category": "ai_influence",
        "summary": "AI models are increasingly used to narrow down candidate materials/molecules for human researchers to test.",
        "description": "AI is genuinely being used today to help propose candidate materials and drug compounds — real acceleration of the early discovery funnel — while the actual validation and decision-making stays human-led.",
        "affected_industries": ["biotechnology", "manufacturing", "research"],
        "affected_skills": ["computational chemistry", "materials science", "AI-assisted research methods"],
        "regions": [],
        "time_horizon": "mid_term",
    },
    {
        "id": "trend_low_resource_language_ai",
        "title": "Research Attention Is Growing on AI for Low-Resource Languages",
        "category": "research_direction",
        "summary": "A real, growing research focus on making language AI work fairly for languages with less existing training data.",
        "description": "Most language AI historically performed best on a small number of high-resource languages; there's a genuine, growing research direction focused on closing this gap for the majority of the world's languages.",
        "affected_industries": ["technology", "education"],
        "affected_skills": ["computational linguistics", "multilingual NLP"],
        "regions": [],
        "time_horizon": "mid_term",
    },
    {
        "id": "trend_climate_adaptation_engineering",
        "title": "Climate Adaptation Is Becoming a Standard Part of Infrastructure Engineering",
        "category": "emerging_industry",
        "summary": "Engineering roles increasingly require real climate-resilience planning, not just traditional structural design.",
        "description": "Urban planning and civil engineering roles increasingly require factoring in real climate-adaptation requirements (flooding, heat, extreme weather) as a standard part of the job, not a specialty add-on.",
        "affected_industries": ["engineering & construction", "urban development"],
        "affected_skills": ["climate risk modeling", "resilient infrastructure design"],
        "regions": [],
        "time_horizon": "mid_term",
    },
    {
        "id": "trend_genomics_cost_decline",
        "title": "Genomic Sequencing Costs Keep Falling, Widening Real Access",
        "category": "future_technology",
        "summary": "The real cost of sequencing a genome has fallen dramatically over the past two decades, and continues to decline.",
        "description": "This is one of the most well-documented real cost curves in science — dramatically falling sequencing costs are genuinely widening access to genomic research and personalized medicine.",
        "affected_industries": ["healthcare", "biotechnology"],
        "affected_skills": ["genomics", "bioinformatics"],
        "regions": [],
        "time_horizon": "mid_term",
    },
    {
        "id": "trend_devrel_ai_shift",
        "title": "Developer-Facing Roles Are Shifting Toward AI-Tooling Support",
        "category": "skill_shift",
        "summary": "Developer relations and technical support roles increasingly focus on AI-assisted developer tools specifically.",
        "description": "As more companies ship AI-powered developer tools, DevRel/technical-support roles increasingly specialize in helping developers adopt and debug AI-assisted workflows specifically, alongside traditional tooling.",
        "affected_industries": ["technology"],
        "affected_skills": ["developer relations", "AI tooling support"],
        "regions": [],
        "time_horizon": "near_term",
    },
    {
        "id": "trend_public_health_data_systems",
        "title": "Public Health Systems Are Investing Heavily in Real-Time Data Infrastructure",
        "category": "emerging_industry",
        "summary": "Governments and health systems are building genuinely better real-time data pipelines after recent public-health experience.",
        "description": "Many public health systems have real, funded initiatives underway to modernize outbreak/resource data infrastructure — a genuine growth area for people who can work at the intersection of public health and data systems.",
        "affected_industries": ["healthcare", "government", "public health & policy"],
        "affected_skills": ["public health data analysis", "epidemiological modeling"],
        "regions": [],
        "time_horizon": "near_term",
    },
    {
        "id": "trend_declining_routine_bookkeeping",
        "title": "Routine Bookkeeping Continues Shifting Toward Automated Reconciliation",
        "category": "declining_industry",
        "summary": "Basic transaction reconciliation work continues moving toward automated tools, shifting accountant time toward interpretation.",
        "description": "This mirrors the same long-running pattern already visible in accounting — routine reconciliation keeps automating, while the real remaining human work concentrates on judgment, interpretation, and oversight.",
        "affected_industries": ["finance"],
        "affected_skills": [],
        "regions": [],
        "time_horizon": "long_term",
    },
    {
        "id": "trend_space_commercialization",
        "title": "Commercial Space Access Keeps Expanding Beyond a Handful of National Programs",
        "category": "emerging_industry",
        "summary": "Falling launch costs are genuinely widening real participation in space systems work beyond national space agencies.",
        "description": "Reusable launch technology has genuinely lowered real costs, widening the real pool of organizations (not just national agencies) building and operating spacecraft and satellite systems.",
        "affected_industries": ["aerospace", "technology"],
        "affected_skills": ["space systems engineering", "satellite operations"],
        "regions": [],
        "time_horizon": "mid_term",
    },
    {
        "id": "trend_ai_incident_response_skills",
        "title": "AI Incident Response Is Becoming Its Own Real Skill Area",
        "category": "skill_shift",
        "summary": "As more companies run AI systems in production, real skills in diagnosing and responding to AI failures are growing in demand.",
        "description": "Mirrors the earlier rise of DevOps/site-reliability skills — as production AI systems become more common, the real, specific skill of diagnosing and responding to AI system failures is emerging as its own valued specialty.",
        "affected_industries": ["technology"],
        "affected_skills": ["AI monitoring", "incident response", "ML reliability"],
        "regions": [],
        "time_horizon": "near_term",
    },
    {
        "id": "trend_decentralized_clinical_trials",
        "title": "Clinical Trials Are Shifting Toward More Decentralized, Digital Models",
        "category": "hiring_shift",
        "summary": "More clinical trial roles now involve remote/digital coordination rather than exclusively site-based work.",
        "description": "A real, ongoing shift toward decentralized trial models means clinical research coordination increasingly involves digital, distributed patient monitoring alongside traditional site-based work.",
        "affected_industries": ["healthcare research", "biotechnology"],
        "affected_skills": ["decentralized trial coordination", "remote patient monitoring"],
        "regions": [],
        "time_horizon": "mid_term",
    },
    {
        "id": "trend_ai_safety_research_growth",
        "title": "AI Safety Research Is Growing as a Distinct, Funded Research Direction",
        "category": "research_direction",
        "summary": "Real, growing research funding and attention is going specifically toward AI safety and alignment research.",
        "description": "AI safety/alignment has grown from a niche academic interest into a real, distinctly funded research direction at both universities and AI labs — a genuine, active field for students drawn to both AI and ethics/risk research.",
        "affected_industries": ["technology", "research"],
        "affected_skills": ["AI safety research", "alignment research", "responsible AI practices"],
        "regions": [],
        "time_horizon": "mid_term",
    },
]


async def seed() -> None:
    client = get_supabase_client()
    trends = [Trend.model_validate(t) for t in TRENDS]

    def _upsert() -> None:
        client.table("trends").upsert([t.model_dump(mode="json") for t in trends]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(trends)} trends.")


if __name__ == "__main__":
    asyncio.run(seed())

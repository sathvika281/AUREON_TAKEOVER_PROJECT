"""One-time enrichment script for Connect Batch 2 — backfills the 10 new
Journey Story fields (timeline through source_reference) onto all 15
existing career_stories rows, honestly reflecting only what each
story's original narrative already implies (never inventing a gap year
or career switch that wasn't in the original text). Uses targeted
`.update()` per story id, never `.upsert()` — same discipline as
`enrich_trends.py`. Every story here stays `story_type="composite"`
(illustrative persona, not a real named individual) — no
`source_reference` is fabricated.

Run via: python -m aureon.scripts.enrich_career_stories

Idempotent: safe to re-run.
"""

import asyncio

from aureon.services.supabase.client import get_supabase_client

ENRICHMENTS: dict[str, dict] = {
    "story_physician_general_1": {
        "timeline": [
            {"stage": "university", "label": "Medical school", "description": "Chose medicine after volunteering at a community clinic during university.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Residency", "description": "Entered residency expecting to specialize in a hospital subspecialty.", "year_label": "Year 4"},
            {"stage": "turning_point", "label": "A routine check-up that mattered", "description": "A patient credited a routine check-up with catching a serious condition early, reshaping their view of unglamorous, everyday care.", "year_label": "Year 6"},
            {"stage": "current_role", "label": "Family Physician", "description": "Builds long-term relationships with patients and their families in general practice.", "year_label": "Year 8"},
        ],
        "career_switch": False, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Continues to practice as a family physician, having chosen long-term patient relationships over subspecialty prestige.",
        "industry": "healthcare", "story_type": "composite", "source_reference": "",
    },
    "story_civil_engineer_1": {
        "timeline": [
            {"stage": "university", "label": "Civil engineering degree", "description": "Studied civil engineering, drawn to how bridges and buildings shape how people move through a city.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Design engineer", "description": "Started in a design role calculating loads and stresses.", "year_label": "Year 1"},
            {"stage": "turning_point", "label": "First bridge, start to finish", "description": "Led their first bridge project from design through completion, learning how much judgment matters beyond textbook formulas.", "year_label": "Year 5"},
            {"stage": "current_role", "label": "Site-facing civil engineer", "description": "Splits time between design and site supervision, seeing designs actually get built.", "year_label": "Year 10"},
        ],
        "career_switch": False, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Works across design and construction supervision, valuing the judgment that only comes from being on site.",
        "industry": "engineering & construction", "story_type": "composite", "source_reference": "",
    },
    "story_teacher_k12_1": {
        "timeline": [
            {"stage": "university", "label": "A different subject entirely", "description": "Originally studied a different subject in university, before realizing during a tutoring job that teaching itself was the real draw.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "Switch into teaching", "description": "Switched into a teaching certification program and took a first job in a challenging, under-resourced school.", "year_label": "Year 1"},
            {"stage": "failure", "label": "Near burn-out", "description": "Nearly burned out in the first two years balancing large class sizes with individual student needs.", "year_label": "Year 2"},
            {"stage": "turning_point", "label": "One student's turnaround", "description": "A formerly disengaged student's turnaround after finding one subject that clicked reaffirmed why the work mattered.", "year_label": "Year 3"},
            {"stage": "current_role", "label": "Middle School Teacher", "description": "Teaches with sustainable boundaries built after the early burnout years.", "year_label": "Year 6"},
        ],
        "career_switch": True, "gap_year": False,
        "uncertainty_period": "The first two years, balancing large class sizes with individual student needs, came close to burnout before finding a sustainable rhythm.",
        "current_outcome": "Teaches middle school with firmer personal boundaries than when they started, still driven by the same moments of student breakthrough.",
        "industry": "education", "story_type": "composite", "source_reference": "",
    },
    "story_ai_ops_specialist_1": {
        "timeline": [
            {"stage": "first_job", "label": "Data analyst", "description": "Came from a data analytics background as companies started deploying more machine learning models into production.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "Move into AI operations", "description": "Moved into AI operations largely learning the role on the job, since formal training barely existed yet.", "year_label": "Year 1"},
            {"stage": "failure", "label": "A public incident", "description": "A deployed model behaved unexpectedly in production, forcing a rapid investigation under real pressure.", "year_label": "Year 2"},
            {"stage": "turning_point", "label": "Building real monitoring", "description": "The incident led to building a proper monitoring system from scratch, which became a model for the whole team's approach.", "year_label": "Year 3"},
            {"stage": "current_role", "label": "AI Operations Lead", "description": "Leads the team's approach to reliability for models in production.", "year_label": "Year 4"},
        ],
        "career_switch": True, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Leads AI operations for their team, treating the early production incident as the foundation of their current monitoring practice.",
        "industry": "technology", "story_type": "composite", "source_reference": "",
    },
    "story_genomics_data_scientist_1": {
        "timeline": [
            {"stage": "university", "label": "Biology and computer science", "description": "Studied both biology and computer science, drawn to questions neither field alone could answer.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Genomics lab, pipeline work", "description": "Joined a genomics lab straight out of graduate school, spending the first year mostly building data pipelines rather than doing analysis.", "year_label": "Year 1"},
            {"stage": "turning_point", "label": "An analysis that mattered clinically", "description": "A finding from their analysis directly informed a clinical research direction — the first time the work felt tangibly consequential.", "year_label": "Year 3"},
            {"stage": "current_role", "label": "Genomics Data Scientist", "description": "Works at the interface of statistical analysis and biological meaning.", "year_label": "Year 5"},
        ],
        "career_switch": False, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Continues translating between statistical results and biological meaning, now trusted with clinically consequential analyses.",
        "industry": "biotechnology", "story_type": "composite", "source_reference": "",
    },
    "story_sustainability_analyst_1": {
        "timeline": [
            {"stage": "university", "label": "Environmental science degree", "description": "Studied environmental science, wanting to work on climate issues from inside a large company rather than only through activism.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "General corporate role", "description": "Started in a general corporate role before a dedicated sustainability team existed.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "Move to the sustainability team", "description": "Moved into a dedicated sustainability team as the company built out the function.", "year_label": "Year 1"},
            {"stage": "turning_point", "label": "A business case that landed", "description": "Successfully built a business case tying a sustainability initiative to real cost savings, changing how the team was perceived internally.", "year_label": "Year 2"},
            {"stage": "current_role", "label": "Sustainability Analyst", "description": "Works to translate environmental priorities into business-relevant cases.", "year_label": "Year 3"},
        ],
        "career_switch": True, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Continues building the internal business case for sustainability work, now with real credibility earned through cost-saving results.",
        "industry": "corporate sustainability", "story_type": "composite", "source_reference": "",
    },
    "story_bioinformatics_scientist_1": {
        "timeline": [
            {"stage": "university", "label": "Pure computer science track", "description": "Started in a pure computer science track before a college genomics course pulled them toward biology.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "A bridging graduate program", "description": "Pursued a graduate program specifically designed to bridge computer science and biology, still a fairly new offering at the time.", "year_label": "Year 1"},
            {"stage": "failure", "label": "Belonging to neither field", "description": "Often felt like neither a 'real' biologist nor a 'real' programmer to specialists in either field early in their career.", "year_label": "Year 2"},
            {"stage": "turning_point", "label": "Research neither field alone could produce", "description": "Presented research that neither a pure biologist nor pure programmer could have produced alone — the moment the interdisciplinary approach clicked.", "year_label": "Year 4"},
            {"stage": "current_role", "label": "Bioinformatics Scientist", "description": "Holds two different ways of thinking at once rather than picking a single field.", "year_label": "Year 6"},
        ],
        "career_switch": True, "gap_year": False,
        "uncertainty_period": "Early years spent feeling like an outsider to both biology and computer science specialists before the interdisciplinary value became clear.",
        "current_outcome": "No longer apologizes for being a generalist across two fields — it's the exact combination the role now depends on.",
        "industry": "biotechnology", "story_type": "composite", "source_reference": "",
    },
    "story_ux_researcher_1": {
        "timeline": [
            {"stage": "university", "label": "Psychology degree", "description": "Studied psychology, initially assuming a career path in clinical work.", "year_label": "Year 0"},
            {"stage": "internship", "label": "Discovering user research", "description": "Discovered user research during an internship in a generalist product role.", "year_label": "Year 1"},
            {"stage": "career_transition", "label": "Move into a research specialty", "description": "Moved from a generalist product role into a dedicated research specialty after realizing how much impact good research had on product direction.", "year_label": "Year 2"},
            {"stage": "turning_point", "label": "A reversed product decision", "description": "A study that reversed a major planned product decision — later validated by the product's success — earned lasting credibility for the research function.", "year_label": "Year 5"},
            {"stage": "current_role", "label": "UX Researcher", "description": "Surfaces what product teams didn't expect, not just what they already believed.", "year_label": "Year 7"},
        ],
        "career_switch": True, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Leads user research with credibility built on findings that changed real product decisions, not just confirmed assumptions.",
        "industry": "technology & design", "story_type": "composite", "source_reference": "",
    },
    "story_materials_research_scientist_1": {
        "timeline": [
            {"stage": "university", "label": "PhD in battery materials", "description": "Was fascinated by chemistry in school and pursued a PhD studying battery materials.", "year_label": "Year 0"},
            {"stage": "failure", "label": "Years of failed experiments", "description": "Spent years running experiments that mostly failed before a project on a new battery material started showing promising results.", "year_label": "Year 3"},
            {"stage": "turning_point", "label": "Lab discovery to industrial prototype", "description": "The first successful scale-up of a lab discovery into an industrial prototype made years of failed experiments feel worthwhile.", "year_label": "Year 6"},
            {"stage": "current_role", "label": "Materials Scientist", "description": "Continues research requiring genuine tolerance for repeated failed experiments.", "year_label": "Year 9"},
        ],
        "career_switch": False, "gap_year": False,
        "uncertainty_period": "Years of funding uncertainty and mostly-failed experiments before a material finally showed promising results.",
        "current_outcome": "Continues materials research, having proven a lab discovery can scale into a real industrial prototype.",
        "industry": "manufacturing & research", "story_type": "composite", "source_reference": "",
    },
    "story_startup_founder_1": {
        "timeline": [
            {"stage": "first_job", "label": "Large company employee", "description": "Worked at a large company for years before deciding to start a company solving a problem they'd personally experienced.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "Bootstrapping the first year", "description": "Bootstrapped the first year with savings before raising outside funding, learning sales, hiring, and finance largely by necessity.", "year_label": "Year 1"},
            {"stage": "failure", "label": "Nearly running out of money", "description": "Nearly ran out of money in the first year and had to make painful decisions about what to cut.", "year_label": "Year 1"},
            {"stage": "turning_point", "label": "The first paying customer", "description": "Closing the first paying customer, after months of free pilots, was the moment the business started to feel real.", "year_label": "Year 2"},
            {"stage": "current_role", "label": "Startup Founder", "description": "Runs the company built from that first paying customer onward.", "year_label": "Year 5"},
        ],
        "career_switch": True, "gap_year": False,
        "uncertainty_period": "The first year, nearly running out of money while learning sales, hiring, and finance under real pressure.",
        "current_outcome": "Continues running the company, having survived the first year's near-failure through resilience learned under pressure.",
        "industry": "entrepreneurship", "story_type": "composite", "source_reference": "",
    },
    "story_developer_relations_engineer_1": {
        "timeline": [
            {"stage": "first_job", "label": "Software engineer", "description": "Worked as a software engineer for several years before realizing they enjoyed helping other developers more than writing production code themselves.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "Move into DevRel", "description": "Moved into a DevRel role at a smaller company, building documentation, sample projects, and community engagement from scratch.", "year_label": "Year 3"},
            {"stage": "turning_point", "label": "Content that drove adoption", "description": "A piece of technical content they wrote became one of the platform's most-referenced resources, visibly driving adoption.", "year_label": "Year 4"},
            {"stage": "current_role", "label": "Developer Relations Engineer", "description": "Keeps coding skills sharp to maintain credibility with the developers they support.", "year_label": "Year 4"},
        ],
        "career_switch": True, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Continues in developer relations, having proven the role's business value through content that measurably drove adoption.",
        "industry": "technology", "story_type": "composite", "source_reference": "",
    },
    "story_foreign_service_officer_1": {
        "timeline": [
            {"stage": "university", "label": "International relations degree", "description": "Studied international relations and was drawn to representing their country abroad after a university exchange program.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Entrance process and early postings", "description": "Passed a competitive entrance process and began serving postings across several very different countries and cultural contexts.", "year_label": "Year 1"},
            {"stage": "failure", "label": "Disorienting early postings", "description": "Found early postings in unfamiliar cultural and political contexts genuinely disorienting.", "year_label": "Year 2"},
            {"stage": "turning_point", "label": "A bilateral agreement", "description": "Successfully negotiated a small but meaningful bilateral agreement after months of relationship-building, reshaping their understanding of the patience diplomacy requires.", "year_label": "Year 7"},
            {"stage": "current_role", "label": "Foreign Service Officer", "description": "Practices diplomacy built on sustained relationship-building rather than single dramatic negotiations.", "year_label": "Year 12"},
        ],
        "career_switch": False, "gap_year": False,
        "uncertainty_period": "Early postings in unfamiliar cultural and political contexts were genuinely disorienting before the role's rhythms became familiar.",
        "current_outcome": "Continues serving in the foreign service, having learned that trust in diplomacy is built slowly rather than through formal meetings alone.",
        "industry": "diplomacy & international relations", "story_type": "composite", "source_reference": "",
    },
    "story_ngo_program_manager_1": {
        "timeline": [
            {"stage": "first_job", "label": "Field volunteer", "description": "Started as a field volunteer after university.", "year_label": "Year 0"},
            {"stage": "promotion", "label": "Into program management", "description": "Worked their way into program management over several years, managing increasingly larger humanitarian programs.", "year_label": "Year 3"},
            {"stage": "turning_point", "label": "Adapting mid-crisis", "description": "Successfully adapted a program mid-crisis, after the original plan became impossible, teaching the value of built-in flexibility.", "year_label": "Year 6"},
            {"stage": "current_role", "label": "NGO Program Manager", "description": "Leads budget and team decisions for humanitarian programs designed to adapt.", "year_label": "Year 8"},
        ],
        "career_switch": False, "gap_year": False, "uncertainty_period": "",
        "current_outcome": "Manages humanitarian programs built to adapt, having learned that the best plans are the flexible ones, not the ones that look perfect on paper.",
        "industry": "international development", "story_type": "composite", "source_reference": "",
    },
    "story_conservation_biologist_1": {
        "timeline": [
            {"stage": "university", "label": "Ecology degree", "description": "Grew up near a national park and became fascinated by the wildlife there, eventually studying ecology in university.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Field research", "description": "Spent years doing field research on an endangered species.", "year_label": "Year 1"},
            {"stage": "career_transition", "label": "Move to policy-facing work", "description": "Moved from field research into a policy-facing conservation role.", "year_label": "Year 4"},
            {"stage": "turning_point", "label": "Community adoption of a practice", "description": "Seeing a local community adopt a conservation practice they'd helped design showed how community buy-in matters as much as the science.", "year_label": "Year 5"},
            {"stage": "current_role", "label": "Conservation Biologist", "description": "Splits attention between ecological science and the people and policy work conservation actually depends on.", "year_label": "Year 6"},
        ],
        "career_switch": False, "gap_year": False,
        "uncertainty_period": "Struggled with how slow policy change felt compared to the urgency of the ecological problems being studied.",
        "current_outcome": "Works across science and policy, treating community coordination as inseparable from the biology.",
        "industry": "environmental conservation", "story_type": "composite", "source_reference": "",
    },
    "story_ias_officer_india_1": {
        "timeline": [
            {"stage": "university", "label": "UPSC exam preparation", "description": "Spent years preparing for the UPSC exam alongside university studies, after growing up watching local government struggle to deliver basic services.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "District-level postings", "description": "Began a career administering district-level programs after selection.", "year_label": "Year 3"},
            {"stage": "failure", "label": "Political pressure", "description": "Faced significant political pressure early in postings while trying to implement policies fairly and transparently.", "year_label": "Year 4"},
            {"stage": "turning_point", "label": "Resolving a stalled infrastructure issue", "description": "Successfully resolved a long-standing local infrastructure issue, after previous attempts had stalled for years, building lasting community trust.", "year_label": "Year 6"},
            {"stage": "current_role", "label": "IAS Officer", "description": "Practices governance built through consistent, patient follow-through.", "year_label": "Year 10"},
        ],
        "career_switch": False,
        "gap_year": False,
        "uncertainty_period": "Years spent preparing for a highly competitive entrance exam with no guarantee of selection.",
        "current_outcome": "Continues in district administration, having built lasting community trust through patient, consistent follow-through rather than single dramatic decisions.",
        "industry": "public administration", "story_type": "composite", "source_reference": "",
    },
}


async def enrich() -> None:
    client = get_supabase_client()
    missing = []
    for story_id, fields in ENRICHMENTS.items():

        def _update(sid: str = story_id, payload: dict = fields) -> None:
            result = client.table("career_stories").update(payload).eq("id", sid).execute()
            if not result.data:
                missing.append(sid)

        await asyncio.to_thread(_update)

    if missing:
        print(f"WARNING — no matching row updated for: {missing}")
    print(f"Enriched {len(ENRICHMENTS) - len(missing)} of {len(ENRICHMENTS)} career stories.")


if __name__ == "__main__":
    asyncio.run(enrich())

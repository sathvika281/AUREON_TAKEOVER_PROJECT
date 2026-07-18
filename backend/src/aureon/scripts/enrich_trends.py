"""One-time enrichment script for the Explore Polish Batch — backfills
9 new Trend fields (key_milestones through opportunities) onto all 16
existing trends. Uses targeted `.update()` per trend id, never
`.upsert()`. Research-paper references use real, well-known landmark
work where genuinely applicable; otherwise they're honestly labeled as
illustrative research directions, never a fabricated specific citation
— same "never fabricate" discipline as the rest of this catalog.

Run via: python -m aureon.scripts.enrich_trends

Idempotent: safe to re-run.
"""

import asyncio

from aureon.domain.models.trend import Trend
from aureon.services.supabase.client import get_supabase_client

ENRICHMENTS: dict[str, dict] = {
    "trend_applied_ai_engineering": {
        "key_milestones": ["Widespread adoption of pretrained foundation models via API access (2023+)", "Growth of retrieval-augmented generation as a standard applied pattern", "Rise of dedicated 'AI engineer' job titles distinct from ML research roles"],
        "countries_leading": ["United States", "United Kingdom", "India", "Singapore"],
        "affected_careers": ["AI Operations Specialist", "Developer Relations Engineer", "Product-Led Growth Specialist"],
        "research_papers": ["Illustrative research direction: applied evaluation methods for retrieval-augmented generation systems in production settings"],
        "companies": ["OpenAI", "Anthropic", "Google DeepMind", "Microsoft"],
        "startups": ["Perplexity", "Cursor", "Glean"],
        "government_initiatives": ["EU AI Act implementation guidance for applied AI deployments", "US NIST AI Risk Management Framework adoption"],
        "risks": ["Overreliance on models without adequate evaluation of failure modes", "Skills gap between traditional software engineering and applied AI engineering"],
        "opportunities": ["Growing demand for engineers who can integrate AI models into real products, not just train them", "New career paths bridging product and AI capability"],
    },
    "trend_traditional_data_entry_decline": {
        "key_milestones": ["Widespread OCR and intelligent document processing adoption in enterprises", "Growth of API-first data capture replacing manual re-entry", "Automation of routine reconciliation tasks in finance and logistics"],
        "countries_leading": ["United States", "Germany", "Japan"],
        "affected_careers": ["Accountant (Corporate Finance)"],
        "research_papers": ["Illustrative research direction: labor-market studies tracking routine cognitive task automation across administrative roles"],
        "companies": ["UiPath", "Automation Anywhere", "SAP"],
        "startups": ["Hyperscience", "Rossum"],
        "government_initiatives": ["National workforce retraining programs targeting administrative automation impact"],
        "risks": ["Displacement risk for workers whose roles are narrowly focused on manual data entry without upskilling support"],
        "opportunities": ["Shift of human time toward data interpretation, exception-handling, and oversight roles rather than manual entry"],
    },
    "trend_brain_computer_interfaces": {
        "key_milestones": ["First human clinical trials of implantable neural interfaces (early 2020s)", "FDA breakthrough device designations for BCI-assisted communication devices", "Growth of non-invasive EEG-based BCI research for consumer applications"],
        "countries_leading": ["United States", "Switzerland", "China"],
        "affected_careers": ["Neuroscience Postdoctoral Researcher", "Bioinformatics Scientist"],
        "research_papers": ["Illustrative research direction: safety and efficacy studies of implantable neural interfaces in early clinical trial populations"],
        "companies": ["Synchron", "Blackrock Neurotech"],
        "startups": ["Neuralink", "Paradromics"],
        "government_initiatives": ["NIH BRAIN Initiative funding for neural interface research"],
        "risks": ["Long regulatory timelines before widespread clinical availability", "Significant ethical and privacy questions around neural data"],
        "opportunities": ["Emerging research and engineering roles at the intersection of neuroscience, hardware, and software"],
    },
    "trend_ai_literacy_as_baseline_skill": {
        "key_milestones": ["Widespread integration of AI writing/coding assistants into everyday workplace tools", "Growth of 'AI literacy' as a stated hiring criterion across non-technical roles"],
        "countries_leading": ["United States", "United Kingdom", "South Korea", "Singapore"],
        "affected_careers": ["K-12 Teacher", "Accountant (Corporate Finance)", "Foreign Service Officer (Diplomat)"],
        "research_papers": ["Illustrative research direction: workplace surveys tracking AI-tool adoption rates across non-technical job functions"],
        "companies": ["Microsoft", "Google", "Salesforce"],
        "startups": ["Notion (AI features)", "Grammarly"],
        "government_initiatives": ["National digital/AI literacy curriculum additions in several countries' school systems"],
        "risks": ["Widening gap between workers with and without practical AI-tool fluency"],
        "opportunities": ["Low-barrier entry point for building genuinely useful AI fluency without needing a technical degree"],
    },
    "trend_remote_hiring_normalization": {
        "key_milestones": ["Sustained post-2020 growth in fully-remote job postings across knowledge-work sectors", "Rise of distributed-first companies with no central office"],
        "countries_leading": ["United States", "United Kingdom", "Netherlands", "India"],
        "affected_careers": ["Developer Relations Engineer", "Product-Led Growth Specialist", "UX Researcher"],
        "research_papers": ["Illustrative research direction: longitudinal labor studies comparing pre- and post-2020 remote job posting rates"],
        "companies": ["GitLab", "Automattic", "Zapier"],
        "startups": ["Deel", "Remote.com"],
        "government_initiatives": ["Digital nomad visa programs introduced by several countries to attract remote knowledge workers"],
        "risks": ["Increased global competition for the same remote roles", "Uneven access to reliable high-speed internet limiting who can participate"],
        "opportunities": ["Genuinely widened geographic access to roles previously tied to specific cities"],
    },
    "trend_ai_assisted_scientific_discovery": {
        "key_milestones": ["AlphaFold's protein structure prediction breakthrough (2020-2021)", "Growth of AI-assisted candidate screening in pharmaceutical R&D pipelines"],
        "countries_leading": ["United States", "United Kingdom", "China"],
        "affected_careers": ["Materials Science Research Scientist", "Bioinformatics Scientist", "Genomics Data Scientist"],
        "research_papers": ["DeepMind's AlphaFold protein structure prediction work (2021, published in Nature)"],
        "companies": ["DeepMind", "Insilico Medicine", "Recursion Pharmaceuticals"],
        "startups": ["Isomorphic Labs", "Iambic Therapeutics"],
        "government_initiatives": ["National AI-for-science research funding initiatives (e.g. US DOE AI programs)"],
        "risks": ["Risk of over-trusting model predictions without sufficient wet-lab validation"],
        "opportunities": ["New hybrid research roles combining domain science expertise with computational/AI fluency"],
    },
    "trend_low_resource_language_ai": {
        "key_milestones": ["Growth of multilingual open-source language model initiatives", "Increased academic focus on low-resource language benchmarks"],
        "countries_leading": ["India", "Nigeria", "South Africa", "Indonesia"],
        "affected_careers": ["Computational Linguist"],
        "research_papers": ["Illustrative research direction: benchmark development for underrepresented languages in large language model evaluation"],
        "companies": ["Google (multilingual research)", "Meta AI"],
        "startups": ["AI4Bharat", "Masakhane (research collective)"],
        "government_initiatives": ["National language-technology funding programs supporting indigenous and regional languages"],
        "risks": ["Continued underrepresentation of languages with very small digital text corpora"],
        "opportunities": ["Growing research and product demand for language technology that genuinely serves non-English-first users"],
    },
    "trend_climate_adaptation_engineering": {
        "key_milestones": ["Increased adoption of climate-resilience standards in national building codes", "Growth of climate-risk modeling as a standard part of infrastructure planning"],
        "countries_leading": ["Netherlands", "Sweden", "Singapore", "Japan"],
        "affected_careers": ["Civil Engineer", "Municipal Urban Planner", "Corporate Sustainability Analyst"],
        "research_papers": ["Illustrative research direction: comparative studies of climate-resilient infrastructure standards across regions"],
        "companies": ["Arup", "AECOM", "Ørsted"],
        "startups": ["ClimateAi", "One Concern"],
        "government_initiatives": ["National climate adaptation infrastructure funding programs (e.g. EU Green Deal infrastructure provisions)"],
        "risks": ["Underinvestment in adaptation relative to the pace of climate-related infrastructure stress"],
        "opportunities": ["Growing demand for engineers who combine traditional structural expertise with climate-resilience planning"],
    },
    "trend_genomics_cost_decline": {
        "key_milestones": ["Human Genome Project completion (2003)", "Sequencing cost per genome falling from ~$100M (2001) to under $1,000 (early 2020s)"],
        "countries_leading": ["United States", "United Kingdom", "China"],
        "affected_careers": ["Genomics Data Scientist", "Bioinformatics Scientist", "Health Informatics Specialist"],
        "research_papers": ["National Human Genome Research Institute's published sequencing cost tracking data (genome.gov)"],
        "companies": ["Illumina", "23andMe", "BGI Genomics"],
        "startups": ["Nebula Genomics", "Color Health"],
        "government_initiatives": ["National genomic sequencing initiatives (e.g. UK's 100,000 Genomes Project)"],
        "risks": ["Genetic privacy and data-security concerns as sequencing becomes more widespread"],
        "opportunities": ["Widening real access to genomic data is expanding demand for people who can analyze and interpret it responsibly"],
    },
    "trend_devrel_ai_shift": {
        "key_milestones": ["Growth of AI-coding-assistant-specific developer relations roles", "Rise of AI API documentation and onboarding as a distinct DevRel specialty"],
        "countries_leading": ["United States", "United Kingdom", "India"],
        "affected_careers": ["Developer Relations Engineer", "AI Operations Specialist"],
        "research_papers": ["Illustrative research direction: surveys of developer experience with AI-assisted coding tools"],
        "companies": ["GitHub", "Stripe", "Anthropic"],
        "startups": ["Vercel", "Replit"],
        "government_initiatives": [],
        "risks": ["Rapid tool churn making specific-tool expertise less durable than general communication skill"],
        "opportunities": ["New DevRel specialization focused specifically on helping developers adopt AI-assisted tooling well"],
    },
    "trend_public_health_data_systems": {
        "key_milestones": ["Post-2020 investment surge in public health data infrastructure modernization", "Growth of real-time disease surveillance dashboards adopted by national health agencies"],
        "countries_leading": ["United States", "United Kingdom", "Singapore", "South Korea"],
        "affected_careers": ["Public Health Policy Analyst", "Health Informatics Specialist"],
        "research_papers": ["Illustrative research direction: evaluations of real-time public health surveillance system effectiveness post-2020"],
        "companies": ["Palantir (public health contracts)", "Epic Systems"],
        "startups": ["Truveta"],
        "government_initiatives": ["CDC Data Modernization Initiative (United States)", "WHO Hub for Pandemic and Epidemic Intelligence"],
        "risks": ["Data privacy concerns balanced against public health surveillance needs"],
        "opportunities": ["Growing demand for people who can bridge public health domain knowledge and data systems engineering"],
    },
    "trend_declining_routine_bookkeeping": {
        "key_milestones": ["Widespread adoption of automated bank-feed reconciliation in accounting software", "Growth of AI-assisted anomaly detection in transaction review"],
        "countries_leading": ["United States", "United Kingdom", "Australia"],
        "affected_careers": ["Accountant (Corporate Finance)"],
        "research_papers": ["Illustrative research direction: studies tracking time-allocation shifts within accounting roles as reconciliation automates"],
        "companies": ["Intuit (QuickBooks)", "Xero", "Sage"],
        "startups": ["Puzzle", "Campfire"],
        "government_initiatives": [],
        "risks": ["Entry-level bookkeeping roles shrinking faster than new entry points are created"],
        "opportunities": ["Accountant time shifting toward interpretation, advisory, and exception-handling rather than manual reconciliation"],
    },
    "trend_space_commercialization": {
        "key_milestones": ["Reusable rocket technology substantially lowering launch costs (2015+)", "Growth of commercial small-satellite constellations for communications and imaging"],
        "countries_leading": ["United States", "India", "United Kingdom"],
        "affected_careers": ["Space Systems Engineer"],
        "research_papers": ["Illustrative research direction: economic analyses of launch cost trends and their effect on commercial space market entry"],
        "companies": ["SpaceX", "Rocket Lab", "ISRO"],
        "startups": ["Relativity Space", "Astra"],
        "government_initiatives": ["NASA Commercial Orbital Transportation Services program", "ISRO's private-sector space policy reforms"],
        "risks": ["Growing orbital debris and space-traffic management challenges as launch frequency rises"],
        "opportunities": ["Space engineering careers increasingly open beyond a small number of national space agencies"],
    },
    "trend_ai_incident_response_skills": {
        "key_milestones": ["Rise of documented production AI-model failure incidents at scale", "Growth of dedicated AI monitoring and observability tooling"],
        "countries_leading": ["United States", "United Kingdom"],
        "affected_careers": ["AI Operations Specialist"],
        "research_papers": ["Illustrative research direction: case-study collections of production machine-learning system failures and root-cause patterns"],
        "companies": ["Google", "Amazon Web Services", "Arize AI"],
        "startups": ["Fiddler AI", "WhyLabs"],
        "government_initiatives": ["Emerging AI incident reporting frameworks under discussion in several national AI governance proposals"],
        "risks": ["Shortage of practitioners with real experience diagnosing AI-specific production failures"],
        "opportunities": ["New, well-compensated specialization at the intersection of site reliability engineering and applied ML"],
    },
    "trend_decentralized_clinical_trials": {
        "key_milestones": ["Growth of remote patient monitoring adoption in clinical trials (accelerated post-2020)", "FDA guidance updates supporting decentralized trial designs"],
        "countries_leading": ["United States", "United Kingdom", "Germany"],
        "affected_careers": ["Clinical Research Coordinator"],
        "research_papers": ["Illustrative research direction: comparative studies of participant retention in decentralized versus traditional site-based trials"],
        "companies": ["IQVIA", "Medable"],
        "startups": ["Science 37", "Curebase"],
        "government_initiatives": ["FDA guidance on decentralized clinical trial design (United States)"],
        "risks": ["Digital-access disparities potentially skewing decentralized trial participant populations"],
        "opportunities": ["Growing demand for coordinators comfortable with remote/digital patient engagement, not just site-based work"],
    },
    "trend_ai_safety_research_growth": {
        "key_milestones": ["Establishment of dedicated AI safety research teams at major AI labs", "Growth of independent AI safety research organizations and funding bodies"],
        "countries_leading": ["United States", "United Kingdom"],
        "affected_careers": ["AI Operations Specialist", "Computational Linguist"],
        "research_papers": ["Illustrative research direction: published research agendas from dedicated AI alignment and safety research groups"],
        "companies": ["Anthropic", "Google DeepMind", "OpenAI"],
        "startups": ["Redwood Research"],
        "government_initiatives": ["UK AI Safety Institute", "US AI Safety Institute (NIST)"],
        "risks": ["Talent shortage relative to the growing scope of safety research needs"],
        "opportunities": ["Emerging, well-funded research career track distinct from general ML engineering or research"],
    },
}


async def enrich() -> None:
    client = get_supabase_client()
    missing = []
    for trend_id, fields in ENRICHMENTS.items():

        def _update(tid: str = trend_id, payload: dict = fields) -> None:
            result = client.table("trends").update(payload).eq("id", tid).execute()
            if not result.data:
                missing.append(tid)

        await asyncio.to_thread(_update)

    if missing:
        print(f"WARNING — no matching row updated for: {missing}")
    print(f"Enriched {len(ENRICHMENTS) - len(missing)} of {len(ENRICHMENTS)} trends.")


if __name__ == "__main__":
    asyncio.run(enrich())

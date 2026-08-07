"""One-time seed script for Sprint 2's Company Knowledge Base
(docs/SPRINT_2.md). Run via: python -m aureon.scripts.seed_companies

Every company below is derived directly from the real `companies` text
already sitting in the 27 seeded Career rows — not invented in parallel.
Depth over breadth, per Sprint 1's established precedent: 30 real,
well-known organizations across `company`/`nonprofit`/`government`
(the real data includes genuine governments and NGOs, not only
for-profit companies), not all 84 raw strings found. Two genuine
near-duplicates in the raw data are canonicalized to one row each
(Apollo Hospitals, Deloitte); everything else is kept as its own
distinct entity rather than guessing at corporate-structure
relationships that can't be verified (e.g. Google vs. Google DeepMind).
Idempotent: upserts by id, safe to re-run.
"""

import asyncio

from aureon.domain.models.company import Company
from aureon.services.supabase.client import get_supabase_client

COMPANIES: list[dict] = [
    {
        "id": "google", "name": "Google", "organization_kind": "company", "industry": "technology",
        "size_category": "enterprise",
        "what_they_do": "A technology company best known for web search, and now a major provider of cloud computing, mobile software, and consumer products.",
        "logo_url": "https://logo.clearbit.com/google.com",
        "hiring_focus_areas": ["software engineering", "data science", "product management"],
    },
    {
        "id": "microsoft", "name": "Microsoft", "organization_kind": "company", "industry": "technology",
        "size_category": "enterprise",
        "what_they_do": "A technology company known for the Windows operating system, Office productivity software, and the Azure cloud platform.",
        "logo_url": "https://logo.clearbit.com/microsoft.com",
        "hiring_focus_areas": ["software engineering", "cloud infrastructure"],
    },
    {
        "id": "amazon_web_services", "name": "Amazon Web Services", "organization_kind": "company", "industry": "technology",
        "size_category": "enterprise",
        "what_they_do": "Amazon's cloud computing division, providing on-demand infrastructure and platform services to businesses worldwide.",
        "logo_url": "https://logo.clearbit.com/aws.amazon.com",
        "hiring_focus_areas": ["cloud infrastructure", "software engineering"],
    },
    {
        "id": "github", "name": "GitHub", "organization_kind": "company", "industry": "technology",
        "size_category": "enterprise",
        "what_they_do": "A code hosting and collaboration platform used by millions of developers and open-source projects; owned by Microsoft.",
        "logo_url": "https://logo.clearbit.com/github.com",
        "hiring_focus_areas": ["software engineering", "developer relations"],
    },
    {
        "id": "figma", "name": "Figma", "organization_kind": "company", "industry": "technology & design",
        "size_category": "mid_size",
        "what_they_do": "A collaborative interface design tool used widely by product design teams for real-time, browser-based design work.",
        "logo_url": "https://logo.clearbit.com/figma.com",
        "hiring_focus_areas": ["product design", "software engineering"],
    },
    {
        "id": "notion", "name": "Notion", "organization_kind": "company", "industry": "technology",
        "size_category": "mid_size",
        "what_they_do": "A workspace and productivity software company combining notes, documents, and project tracking in one connected tool.",
        "logo_url": "https://logo.clearbit.com/notion.so",
        "hiring_focus_areas": ["product design", "software engineering"],
    },
    {
        "id": "stripe", "name": "Stripe", "organization_kind": "company", "industry": "technology",
        "size_category": "enterprise",
        "what_they_do": "A financial infrastructure company providing payment processing and related tools for businesses online.",
        "logo_url": "https://logo.clearbit.com/stripe.com",
        "hiring_focus_areas": ["software engineering", "financial infrastructure"],
    },
    {
        "id": "hugging_face", "name": "Hugging Face", "organization_kind": "company", "industry": "technology & language",
        "size_category": "mid_size",
        "what_they_do": "A company building open-source tools and a hosting platform for machine learning models, especially natural language processing.",
        "logo_url": "https://logo.clearbit.com/huggingface.co",
        "hiring_focus_areas": ["machine learning engineering", "open source"],
    },
    {
        "id": "google_deepmind", "name": "Google DeepMind", "organization_kind": "company", "industry": "technology & language",
        "size_category": "enterprise",
        "what_they_do": "Google's AI research lab, known for landmark work in reinforcement learning, protein structure prediction, and large language models.",
        "logo_url": "https://logo.clearbit.com/deepmind.google",
        "hiring_focus_areas": ["AI research", "machine learning engineering"],
    },
    {
        "id": "zerodha", "name": "Zerodha", "organization_kind": "company", "industry": "technology",
        "size_category": "mid_size",
        "what_they_do": "An Indian financial services company offering a widely-used discount brokerage and trading platform.",
        "logo_url": "https://logo.clearbit.com/zerodha.com",
        "hiring_focus_areas": ["software engineering", "fintech"],
    },
    {
        "id": "spacex", "name": "SpaceX", "organization_kind": "company", "industry": "aerospace",
        "size_category": "enterprise",
        "what_they_do": "An aerospace manufacturer and space transport company known for reusable rockets and the Starlink satellite network.",
        "logo_url": "https://logo.clearbit.com/spacex.com",
        "hiring_focus_areas": ["aerospace engineering", "software engineering"],
    },
    {
        "id": "rocket_lab", "name": "Rocket Lab", "organization_kind": "company", "industry": "aerospace",
        "size_category": "mid_size",
        "what_they_do": "An aerospace company providing small satellite launch services and spacecraft components.",
        "logo_url": "https://logo.clearbit.com/rocketlabusa.com",
        "hiring_focus_areas": ["aerospace engineering", "manufacturing"],
    },
    {
        "id": "illumina", "name": "Illumina", "organization_kind": "company", "industry": "biotechnology",
        "size_category": "enterprise",
        "what_they_do": "A biotechnology company that manufactures gene sequencing systems used across genomics research and clinical diagnostics.",
        "logo_url": "https://logo.clearbit.com/illumina.com",
        "hiring_focus_areas": ["genomics", "bioinformatics"],
    },
    {
        "id": "23andme", "name": "23andMe", "organization_kind": "company", "industry": "biotechnology",
        "size_category": "mid_size",
        "what_they_do": "A personal genomics company offering direct-to-consumer DNA testing for ancestry and health insights.",
        "logo_url": "https://logo.clearbit.com/23andme.com",
        "hiring_focus_areas": ["genomics", "data science"],
    },
    {
        "id": "biocon", "name": "Biocon", "organization_kind": "company", "industry": "biotechnology",
        "size_category": "enterprise",
        "what_they_do": "An Indian biopharmaceutical company developing affordable biologic medicines, including insulin and biosimilars.",
        "logo_url": "https://logo.clearbit.com/biocon.com",
        "hiring_focus_areas": ["biotechnology research", "manufacturing"],
    },
    {
        "id": "genentech", "name": "Genentech", "organization_kind": "company", "industry": "biotechnology",
        "size_category": "enterprise",
        "what_they_do": "A biotechnology pioneer, now part of Roche, known for developing biologic medicines from recombinant DNA technology.",
        "logo_url": "https://logo.clearbit.com/gene.com",
        "hiring_focus_areas": ["biotechnology research"],
    },
    {
        "id": "ginkgo_bioworks", "name": "Ginkgo Bioworks", "organization_kind": "company", "industry": "biotechnology",
        "size_category": "mid_size",
        "what_they_do": "A biotech company that designs custom organisms for use in industries like agriculture, pharmaceuticals, and manufacturing.",
        "logo_url": "https://logo.clearbit.com/ginkgobioworks.com",
        "hiring_focus_areas": ["synthetic biology", "bioinformatics"],
    },
    {
        # Canonicalizes both "Apollo Hospitals" and "Apollo Hospitals
        # (clinical trials division)" from the raw seeded data — the
        # same real organization.
        "id": "apollo_hospitals", "name": "Apollo Hospitals", "organization_kind": "company", "industry": "healthcare",
        "size_category": "enterprise",
        "what_they_do": "One of India's largest private hospital networks, providing clinical care alongside a dedicated clinical trials and research division.",
        "logo_url": "https://logo.clearbit.com/apollohospitals.com",
        "hiring_focus_areas": ["clinical care", "clinical research"],
    },
    {
        "id": "mayo_clinic", "name": "Mayo Clinic", "organization_kind": "company", "industry": "healthcare",
        "size_category": "enterprise",
        "what_they_do": "A nonprofit academic medical center in the U.S. widely regarded for clinical care, medical research, and education.",
        "logo_url": "https://logo.clearbit.com/mayoclinic.org",
        "hiring_focus_areas": ["clinical care", "medical research"],
    },
    {
        "id": "kaiser_permanente", "name": "Kaiser Permanente", "organization_kind": "company", "industry": "healthcare",
        "size_category": "enterprise",
        "what_they_do": "An integrated American healthcare consortium combining a health plan with hospitals and physician groups.",
        "logo_url": "https://logo.clearbit.com/kaiserpermanente.org",
        "hiring_focus_areas": ["clinical care", "healthcare administration"],
    },
    {
        # Real raw data says "Cerner (Oracle Health)" — Cerner was
        # acquired by Oracle and rebranded Oracle Health; this is that
        # same real organization under its current name, not a
        # different EHR company.
        "id": "oracle_health", "name": "Oracle Health (Cerner)", "organization_kind": "company", "industry": "healthcare & technology",
        "size_category": "enterprise",
        "what_they_do": "A major provider of electronic health record software, formerly known as Cerner before its acquisition by Oracle.",
        "logo_url": "https://logo.clearbit.com/oracle.com",
        "hiring_focus_areas": ["software engineering", "health informatics"],
    },
    {
        # Canonicalizes both "Deloitte" and "Deloitte Sustainability"
        # from the raw seeded data — the same real organization.
        "id": "deloitte", "name": "Deloitte", "organization_kind": "company", "industry": "finance",
        "size_category": "enterprise",
        "what_they_do": "One of the largest professional services networks globally, spanning audit, consulting, tax, and dedicated sustainability advisory work.",
        "logo_url": "https://logo.clearbit.com/deloitte.com",
        "hiring_focus_areas": ["consulting", "audit", "sustainability advisory"],
    },
    {
        "id": "patagonia", "name": "Patagonia", "organization_kind": "company", "industry": "corporate sustainability",
        "size_category": "mid_size",
        "what_they_do": "An outdoor apparel company widely recognized for environmental activism and sustainable manufacturing practices.",
        "logo_url": "https://logo.clearbit.com/patagonia.com",
        "hiring_focus_areas": ["sustainability", "supply chain"],
    },
    {
        "id": "arup", "name": "Arup", "organization_kind": "company", "industry": "engineering & construction",
        "size_category": "enterprise",
        "what_they_do": "A global engineering and design consultancy involved in major infrastructure, building, and urban development projects.",
        "logo_url": "https://logo.clearbit.com/arup.com",
        "hiring_focus_areas": ["structural engineering", "urban planning"],
    },
    {
        "id": "world_health_organization", "name": "World Health Organization", "organization_kind": "nonprofit",
        "industry": "public health & policy",
        "what_they_do": "A United Nations agency responsible for international public health, disease response, and global health policy guidance.",
        "logo_url": "https://logo.clearbit.com/who.int",
        "hiring_focus_areas": ["public health", "policy analysis"],
    },
    {
        "id": "human_rights_watch", "name": "Human Rights Watch", "organization_kind": "nonprofit",
        "industry": "human rights advocacy",
        "what_they_do": "An international NGO that investigates and reports on human rights abuses worldwide to support advocacy and accountability.",
        "logo_url": "https://logo.clearbit.com/hrw.org",
        "hiring_focus_areas": ["investigative research", "advocacy"],
    },
    {
        "id": "oxfam", "name": "Oxfam", "organization_kind": "nonprofit", "industry": "international development",
        "what_they_do": "A global confederation of NGOs working on poverty relief, humanitarian response, and development programs.",
        "logo_url": "https://logo.clearbit.com/oxfam.org",
        "hiring_focus_areas": ["program management", "humanitarian response"],
    },
    {
        "id": "nature_conservancy", "name": "The Nature Conservancy", "organization_kind": "nonprofit",
        "industry": "environmental conservation",
        "what_they_do": "A global environmental nonprofit working to protect land and water through science-based conservation projects.",
        "logo_url": "https://logo.clearbit.com/nature.org",
        "hiring_focus_areas": ["conservation science", "field research"],
    },
    {
        "id": "khan_academy", "name": "Khan Academy", "organization_kind": "nonprofit", "industry": "education",
        "what_they_do": "A nonprofit educational organization providing free online courses and practice tools across many subjects.",
        "logo_url": "https://logo.clearbit.com/khanacademy.org",
        "hiring_focus_areas": ["curriculum design", "software engineering"],
    },
    {
        "id": "isro", "name": "ISRO", "organization_kind": "government", "industry": "aerospace",
        "what_they_do": "India's national space agency, responsible for the country's satellite, launch vehicle, and space exploration programs.",
        "logo_url": "https://logo.clearbit.com/isro.gov.in",
        "hiring_focus_areas": ["aerospace engineering", "satellite systems"],
    },
    {
        "id": "nhs_uk", "name": "NHS (UK)", "organization_kind": "government", "industry": "healthcare",
        "what_they_do": "The United Kingdom's publicly funded healthcare system, providing free-at-point-of-use medical care to residents.",
        "logo_url": "https://logo.clearbit.com/nhs.uk",
        "hiring_focus_areas": ["clinical care", "healthcare administration"],
    },
]

# Real free-text strings already sitting in careers.companies, mapped to
# the canonical company id above that genuinely represents them. Built
# directly from the actual seeded data, not guessed. Deliberately
# partial — not every raw company string in the real data maps to a
# seeded row this sprint (e.g. "Y Combinator-backed startups broadly"
# isn't a specific, real, promotable organization) — depth over forced
# completeness, same discipline as Sprint 1's skill aliases.
COMPANY_ALIASES: dict[str, str] = {
    "Google": "google",
    "Microsoft": "microsoft",
    "Amazon Web Services": "amazon_web_services",
    "GitHub": "github",
    "Figma": "figma",
    "Notion": "notion",
    "Stripe": "stripe",
    "Hugging Face": "hugging_face",
    "Google DeepMind": "google_deepmind",
    "Zerodha": "zerodha",
    "SpaceX": "spacex",
    "Rocket Lab": "rocket_lab",
    "Illumina": "illumina",
    "23andMe": "23andme",
    "Biocon": "biocon",
    "Genentech": "genentech",
    "Ginkgo Bioworks": "ginkgo_bioworks",
    "Apollo Hospitals": "apollo_hospitals",
    "Apollo Hospitals (clinical trials division)": "apollo_hospitals",
    "Mayo Clinic": "mayo_clinic",
    "Kaiser Permanente": "kaiser_permanente",
    "Cerner (Oracle Health)": "oracle_health",
    "Deloitte": "deloitte",
    "Deloitte Sustainability": "deloitte",
    "Patagonia": "patagonia",
    "Arup": "arup",
    "World Health Organization": "world_health_organization",
    "Human Rights Watch": "human_rights_watch",
    "Oxfam": "oxfam",
    "The Nature Conservancy": "nature_conservancy",
    "Khan Academy": "khan_academy",
    "ISRO": "isro",
    "NHS (UK)": "nhs_uk",
}


async def seed() -> None:
    client = get_supabase_client()
    companies = [Company.model_validate(c) for c in COMPANIES]

    def _upsert() -> None:
        client.table("companies").upsert([c.model_dump(mode="json") for c in companies]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(companies)} companies.")


if __name__ == "__main__":
    asyncio.run(seed())

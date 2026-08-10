"""Sprint 4 — Data Quality regression guard.

Two checks, both scanning every catalog seed script's top-level data
list generically (nested dicts/lists included) rather than hard-coding
known-bad records:

1. No reserved/placeholder domains (example.com/.org/.net, RFC 2606)
   anywhere — a reserved domain always means "no real destination was
   found," and the honest response is to omit the field, never
   fabricate or leave a placeholder one. Guards the incident this
   sprint's Phase 2 fixed (Opportunity.official_link, Mentor
   portfolio/social links).
2. Every value at a known URL-bearing key (logo_url/official_link/
   photo_url/url/website) is a well-formed https:// URL when present —
   guards against a different, equally real failure mode (a malformed
   or non-https URL slipping into seed data undetected).
"""

import re

from aureon.scripts import (
    seed_career_worlds,
    seed_careers,
    seed_companies,
    seed_experiments,
    seed_experts_arts_and_public_life,
    seed_experts_batch2,
    seed_experts_batch3,
    seed_experts_batch4,
    seed_experts_batch5,
    seed_experts_batch6,
    seed_experts_batch7,
    seed_experts_batch8,
    seed_experts_batch9,
    seed_experts_batch10,
    seed_experts_batch11,
    seed_experts_batch12,
    seed_experts_batch13,
    seed_experts_batch14,
    seed_experts_batch15,
    seed_experts_batch16,
    seed_experts_business_and_government,
    seed_experts_medicine_and_biotech,
    seed_experts_other_domains,
    seed_experts_tech_and_science,
    seed_journey_stories_business_and_education,
    seed_journey_stories_healthcare_environment_and_trades,
    seed_journey_stories_public_service_and_policy,
    seed_journey_stories_science_and_research,
    seed_journey_stories_technology_and_product,
    seed_knowledge_circles,
    seed_learning_styles,
    seed_life_missions,
    seed_mentors_institutions,
    seed_mission_experiences,
    seed_opportunities,
    seed_parent_connect,
    seed_parent_questions,
    seed_projects,
    seed_skills,
    seed_student_discovery_stories,
    seed_student_discovery_stories_batch2,
    seed_topic_resources,
    seed_trends,
)

RESERVED_DOMAIN_RE = re.compile(r"\bexample\.(com|org|net)\b", re.IGNORECASE)

#: Known URL-bearing field names across every seed data shape in this
#: codebase — logo_url (Company), official_link (Opportunity), photo_url
#: (Mentor), url (the `url` key inside a Mentor LinkRef dict, e.g.
#: portfolio_links/social_links entries). Checked only at these exact
#: keys, not every string, so a description that happens to mention
#: "https" in prose is never a false positive.
URL_FIELD_KEYS = {"logo_url", "official_link", "photo_url", "url", "website"}
WELL_FORMED_HTTPS_URL_RE = re.compile(r"^https://[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}(/\S*)?$")

#: (label, data) pairs — every real catalog data list in the codebase as
#: of Sprint 4. A module with more than one top-level list (e.g.
#: mentors + institutions) contributes one entry per list.
SEED_DATA_SOURCES: list[tuple[str, list[dict]]] = [
    ("seed_career_worlds.WORLDS", seed_career_worlds.WORLDS),
    ("seed_careers.CAREERS", seed_careers.CAREERS),
    ("seed_companies.COMPANIES", seed_companies.COMPANIES),
    ("seed_experiments.EXPERIMENTS", seed_experiments.EXPERIMENTS),
    ("seed_experts_arts_and_public_life.EXPERTS", seed_experts_arts_and_public_life.EXPERTS),
    ("seed_experts_batch2.EXPERTS", seed_experts_batch2.EXPERTS),
    ("seed_experts_batch3.EXPERTS", seed_experts_batch3.EXPERTS),
    ("seed_experts_batch4.EXPERTS", seed_experts_batch4.EXPERTS),
    ("seed_experts_batch5.EXPERTS", seed_experts_batch5.EXPERTS),
    ("seed_experts_batch6.EXPERTS", seed_experts_batch6.EXPERTS),
    ("seed_experts_batch7.EXPERTS", seed_experts_batch7.EXPERTS),
    ("seed_experts_batch8.EXPERTS", seed_experts_batch8.EXPERTS),
    ("seed_experts_batch9.EXPERTS", seed_experts_batch9.EXPERTS),
    ("seed_experts_batch10.EXPERTS", seed_experts_batch10.EXPERTS),
    ("seed_experts_batch11.EXPERTS", seed_experts_batch11.EXPERTS),
    ("seed_experts_batch12.EXPERTS", seed_experts_batch12.EXPERTS),
    ("seed_experts_batch13.EXPERTS", seed_experts_batch13.EXPERTS),
    ("seed_experts_batch14.EXPERTS", seed_experts_batch14.EXPERTS),
    ("seed_experts_batch15.EXPERTS", seed_experts_batch15.EXPERTS),
    ("seed_experts_batch16.EXPERTS", seed_experts_batch16.EXPERTS),
    ("seed_experts_business_and_government.EXPERTS", seed_experts_business_and_government.EXPERTS),
    ("seed_experts_medicine_and_biotech.EXPERTS", seed_experts_medicine_and_biotech.EXPERTS),
    ("seed_experts_other_domains.EXPERTS", seed_experts_other_domains.EXPERTS),
    ("seed_experts_tech_and_science.EXPERTS", seed_experts_tech_and_science.EXPERTS),
    ("seed_journey_stories_business_and_education.STORIES", seed_journey_stories_business_and_education.STORIES),
    ("seed_journey_stories_healthcare_environment_and_trades.STORIES", seed_journey_stories_healthcare_environment_and_trades.STORIES),
    ("seed_journey_stories_public_service_and_policy.STORIES", seed_journey_stories_public_service_and_policy.STORIES),
    ("seed_journey_stories_science_and_research.STORIES", seed_journey_stories_science_and_research.STORIES),
    ("seed_journey_stories_technology_and_product.STORIES", seed_journey_stories_technology_and_product.STORIES),
    ("seed_knowledge_circles.CIRCLES", seed_knowledge_circles.CIRCLES),
    ("seed_learning_styles.STYLES", seed_learning_styles.STYLES),
    ("seed_life_missions.MISSIONS", seed_life_missions.MISSIONS),
    ("seed_mentors_institutions.MENTORS", seed_mentors_institutions.MENTORS),
    ("seed_mentors_institutions.INSTITUTIONS", seed_mentors_institutions.INSTITUTIONS),
    ("seed_mentors_institutions.CAREER_EVENTS", seed_mentors_institutions.CAREER_EVENTS),
    ("seed_mentors_institutions.ENTRANCE_EXAMS", seed_mentors_institutions.ENTRANCE_EXAMS),
    ("seed_mission_experiences.MISSION_EXPERIENCES", seed_mission_experiences.MISSION_EXPERIENCES),
    ("seed_opportunities.OPPORTUNITIES", seed_opportunities.OPPORTUNITIES),
    ("seed_parent_connect.GUIDES", seed_parent_connect.GUIDES),
    ("seed_parent_questions.QUESTIONS", seed_parent_questions.QUESTIONS),
    ("seed_projects.PROJECTS", seed_projects.PROJECTS),
    ("seed_skills.SKILLS", seed_skills.SKILLS),
    ("seed_student_discovery_stories.STORIES", seed_student_discovery_stories.STORIES),
    ("seed_student_discovery_stories_batch2.STORIES", seed_student_discovery_stories_batch2.STORIES),
    ("seed_topic_resources.DOMAINS", seed_topic_resources.DOMAINS),
    ("seed_trends.TRENDS", seed_trends.TRENDS),
]


def _find_reserved_domains(value, path: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    if isinstance(value, str):
        if RESERVED_DOMAIN_RE.search(value):
            hits.append((path, value))
    elif isinstance(value, dict):
        for key, sub in value.items():
            hits.extend(_find_reserved_domains(sub, f"{path}.{key}"))
    elif isinstance(value, list):
        for i, sub in enumerate(value):
            hits.extend(_find_reserved_domains(sub, f"{path}[{i}]"))
    return hits


def test_no_reserved_example_domains_in_any_seed_data():
    all_hits: list[str] = []
    for label, data in SEED_DATA_SOURCES:
        for path, value in _find_reserved_domains(data, label):
            all_hits.append(f"{path} = {value!r}")

    assert not all_hits, (
        "Reserved/placeholder domain(s) found in seed data — a fake "
        "example.com/.org/.net URL is worse than an honest absence "
        "(see this file's module docstring):\n" + "\n".join(all_hits)
    )


def _find_malformed_urls(value, path: str) -> list[tuple[str, str]]:
    """Only inspects values sitting at a known URL-bearing key (see
    URL_FIELD_KEYS) — never treats an arbitrary string as a URL just
    because it contains 'http', which would false-positive on prose."""
    hits: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, sub in value.items():
            if key in URL_FIELD_KEYS:
                if isinstance(sub, str) and sub and not WELL_FORMED_HTTPS_URL_RE.match(sub):
                    hits.append((f"{path}.{key}", sub))
            else:
                hits.extend(_find_malformed_urls(sub, f"{path}.{key}"))
    elif isinstance(value, list):
        for i, sub in enumerate(value):
            hits.extend(_find_malformed_urls(sub, f"{path}[{i}]"))
    return hits


def test_url_shaped_fields_are_well_formed_https_urls():
    all_hits: list[str] = []
    for label, data in SEED_DATA_SOURCES:
        for path, value in _find_malformed_urls(data, label):
            all_hits.append(f"{path} = {value!r}")

    assert not all_hits, (
        "Malformed or non-https URL(s) found in seed data's URL-bearing "
        "fields (logo_url/official_link/photo_url/url/website):\n" + "\n".join(all_hits)
    )


def test_seed_data_sources_cover_every_catalog_seed_script():
    """Guards the guard: fails loudly if a future seed script is added
    without also being added to SEED_DATA_SOURCES above, rather than
    silently going unchecked."""
    import pathlib

    scripts_dir = pathlib.Path(seed_careers.__file__).parent
    catalog_prefixes = (
        "seed_career_worlds", "seed_careers", "seed_companies", "seed_experiments",
        "seed_experts_", "seed_journey_stories_", "seed_knowledge_circles",
        "seed_learning_styles", "seed_life_missions", "seed_mentors_institutions",
        "seed_mission_experiences", "seed_opportunities", "seed_parent_connect",
        "seed_parent_questions", "seed_projects", "seed_skills",
        "seed_student_discovery_stories", "seed_topic_resources", "seed_trends",
    )
    real_files = {
        p.stem for p in scripts_dir.glob("seed_*.py") if p.stem.startswith(catalog_prefixes)
    }
    covered_modules = {label.split(".")[0] for label, _ in SEED_DATA_SOURCES}
    missing = real_files - covered_modules
    assert not missing, f"Seed script(s) not covered by the reserved-domain scan: {sorted(missing)}"

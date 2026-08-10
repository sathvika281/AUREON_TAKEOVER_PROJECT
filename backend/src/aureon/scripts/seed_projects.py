"""One-time seed script for Sprint 3's Project Knowledge Base
(docs/SPRINT_3.md). Run via: python -m aureon.scripts.seed_projects

Unlike seed_skills.py/seed_companies.py, this seeds no alias/backfill
pair — Project carries its own outgoing edges natively (target_skill_ids,
related_career_ids, related_company_ids), so there's no free-text field
on Career to promote from. Every skill_id/career_id/company_id below is a
real id already sitting in seed_skills.py/seed_careers.py/
seed_companies.py — cross-checked against those files, not invented.
company_ids are set only where a project genuinely resembles real work
at that company; most projects carry none. Depth over forced coverage:
20 real, attemptable projects across 20 of the 27 seeded careers, not
every career forced to have one. Idempotent: upserts by id, safe to
re-run.
"""

import asyncio

from aureon.domain.models.project import Project
from aureon.services.supabase.client import get_supabase_client

PROJECTS: list[dict] = [
    {
        "id": "genomics_dataset_explorer",
        "title": "Genomics Dataset Explorer",
        "brief": "Take a real public genomics dataset and write code that explores it — find a genuine pattern (a variant frequency, an expression trend) and explain what it actually shows.",
        "difficulty_level": "intermediate",
        "estimated_hours": 8,
        "target_skill_ids": ["programming", "statistical_analysis", "genomics_molecular_biology"],
        "related_career_ids": ["genomics_data_scientist"],
        "related_company_ids": ["illumina"],
        "submission_type": "github_repo",
    },
    {
        "id": "public_health_dashboard",
        "title": "Public Health Dashboard",
        "brief": "Build a small dashboard from a real public-health dataset (case counts, vaccination rates, or similar) that a policymaker could actually read and act on.",
        "difficulty_level": "intermediate",
        "estimated_hours": 6,
        "target_skill_ids": ["data_visualization", "public_health_data_literacy", "statistical_analysis"],
        "related_career_ids": ["public_health_policy_analyst"],
        "related_company_ids": ["world_health_organization"],
        "submission_type": "demo_link",
    },
    {
        "id": "bridge_load_simulation",
        "title": "Bridge Load Simulation",
        "brief": "Model a simple bridge or beam structure and simulate how it behaves under different real load conditions, documenting where it would genuinely fail.",
        "difficulty_level": "advanced",
        "estimated_hours": 10,
        "target_skill_ids": ["simulation_modeling", "attention_to_detail"],
        "related_career_ids": ["civil_engineer"],
        "related_company_ids": ["arup"],
        "submission_type": "writeup",
    },
    {
        "id": "personal_budget_financial_report",
        "title": "Personal Budget Tracker & Financial Report",
        "brief": "Build a real spreadsheet-based budget tracker for a genuine scenario (a household, a small club, a fundraiser) and produce an honest financial report from it.",
        "difficulty_level": "beginner",
        "estimated_hours": 4,
        "target_skill_ids": ["financial_reporting", "spreadsheet_erp_tools", "attention_to_detail"],
        "related_career_ids": ["accountant"],
        "related_company_ids": [],
        "submission_type": "writeup",
    },
    {
        "id": "lesson_plan_assessment_design",
        "title": "Lesson Plan & Learning Assessment Design",
        "brief": "Design a real lesson plan for a specific age group and topic, plus an assessment that genuinely checks whether the lesson's goal was actually learned.",
        "difficulty_level": "beginner",
        "estimated_hours": 5,
        "target_skill_ids": ["public_speaking_writing", "project_management"],
        "related_career_ids": ["teacher_k12"],
        "related_company_ids": [],
        "submission_type": "reflection_only",
    },
    {
        "id": "uptime_monitoring_dashboard",
        "title": "System Uptime Monitoring Dashboard",
        "brief": "Stand up a real monitoring setup for a small app or service you control, tracking genuine uptime/error signals rather than a mock feed.",
        "difficulty_level": "intermediate",
        "estimated_hours": 7,
        "target_skill_ids": ["programming", "monitoring_observability_tools", "simulation_modeling"],
        "related_career_ids": ["ai_ops_specialist"],
        "related_company_ids": ["amazon_web_services"],
        "submission_type": "github_repo",
    },
    {
        "id": "carbon_footprint_local_business",
        "title": "Carbon Footprint Analysis for a Local Business",
        "brief": "Estimate the real carbon footprint of an actual local business or organization using its genuine energy/resource data, and propose one honest, specific reduction.",
        "difficulty_level": "intermediate",
        "estimated_hours": 6,
        "target_skill_ids": ["statistical_analysis", "data_visualization", "policy_analysis"],
        "related_career_ids": ["sustainability_analyst"],
        "related_company_ids": ["patagonia"],
        "submission_type": "writeup",
    },
    {
        "id": "small_satellite_orbit_simulation",
        "title": "Small Satellite Orbit Simulation",
        "brief": "Simulate a real orbital scenario for a small satellite (orbit decay, coverage window, or similar) using real orbital-mechanics equations, not a black-box tool.",
        "difficulty_level": "advanced",
        "estimated_hours": 12,
        "target_skill_ids": ["simulation_modeling", "experimental_design"],
        "related_career_ids": ["space_systems_engineer"],
        "related_company_ids": ["spacex", "rocket_lab", "isro"],
        "submission_type": "github_repo",
    },
    {
        "id": "dna_sequence_alignment_tool",
        "title": "DNA Sequence Alignment Tool",
        "brief": "Implement a real sequence-alignment algorithm (even a simplified one) against genuine DNA sequence data and explain what the alignment actually reveals.",
        "difficulty_level": "advanced",
        "estimated_hours": 10,
        "target_skill_ids": ["programming", "genomics_molecular_biology", "statistical_analysis"],
        "related_career_ids": ["bioinformatics_scientist"],
        "related_company_ids": ["illumina", "ginkgo_bioworks"],
        "submission_type": "github_repo",
    },
    {
        "id": "user_interview_usability_report",
        "title": "User Interview Study & Usability Report",
        "brief": "Run real interviews or usability sessions with a handful of actual people testing a real product or prototype, and write up genuine, specific findings.",
        "difficulty_level": "intermediate",
        "estimated_hours": 6,
        "target_skill_ids": ["interviewing_research", "public_speaking_writing", "attention_to_detail"],
        "related_career_ids": ["ux_researcher"],
        "related_company_ids": ["figma"],
        "submission_type": "writeup",
    },
    {
        "id": "language_model_evaluation_study",
        "title": "Language Model Evaluation Study",
        "brief": "Design and run a real evaluation of a language model's output on a genuine linguistic task, documenting honest strengths and failure cases rather than a marketing summary.",
        "difficulty_level": "advanced",
        "estimated_hours": 9,
        "target_skill_ids": ["linguistics_fundamentals", "programming", "experimental_design"],
        "related_career_ids": ["computational_linguist"],
        "related_company_ids": ["hugging_face", "google_deepmind"],
        "submission_type": "github_repo",
    },
    {
        "id": "patient_data_interoperability_case_study",
        "title": "Patient Data Interoperability Case Study",
        "brief": "Research a real health-data interoperability standard (like FHIR) and write a case study of a genuine scenario where it succeeds or fails to connect two real systems.",
        "difficulty_level": "intermediate",
        "estimated_hours": 7,
        "target_skill_ids": ["regulatory_knowledge", "public_health_data_literacy", "attention_to_detail"],
        "related_career_ids": ["health_informatics_specialist"],
        "related_company_ids": ["oracle_health"],
        "submission_type": "writeup",
    },
    {
        "id": "materials_stress_test_experiment_design",
        "title": "Materials Stress-Test Experiment Design",
        "brief": "Design a genuine experiment to test a real material's behavior under stress (even household materials count), with real controls and an honest account of its limitations.",
        "difficulty_level": "advanced",
        "estimated_hours": 10,
        "target_skill_ids": ["experimental_design", "simulation_modeling"],
        "related_career_ids": ["materials_research_scientist"],
        "related_company_ids": [],
        "submission_type": "writeup",
    },
    {
        "id": "cognitive_task_behavioral_experiment",
        "title": "Cognitive Task Behavioral Experiment",
        "brief": "Design and run a small, real behavioral experiment (a reaction-time or memory task with real participants) and analyze the genuine results statistically.",
        "difficulty_level": "advanced",
        "estimated_hours": 9,
        "target_skill_ids": ["experimental_design", "statistical_analysis"],
        "related_career_ids": ["neuroscience_postdoc"],
        "related_company_ids": [],
        "submission_type": "writeup",
    },
    {
        "id": "clinical_trial_recruitment_protocol",
        "title": "Clinical Trial Recruitment Protocol Design",
        "brief": "Draft a real, detailed recruitment protocol for a plausible clinical trial, including genuine eligibility criteria and the real regulatory considerations it would need to satisfy.",
        "difficulty_level": "intermediate",
        "estimated_hours": 6,
        "target_skill_ids": ["clinical_reasoning", "regulatory_knowledge", "project_management"],
        "related_career_ids": ["clinical_research_coordinator"],
        "related_company_ids": ["mayo_clinic"],
        "submission_type": "writeup",
    },
    {
        "id": "mvp_pitch_deck_landing_page",
        "title": "MVP Pitch Deck & Landing Page",
        "brief": "Build a real landing page and pitch deck for a genuine startup idea of your own, honestly stating what's validated so far and what isn't yet.",
        "difficulty_level": "beginner",
        "estimated_hours": 6,
        "target_skill_ids": ["public_speaking_writing", "negotiation", "project_management"],
        "related_career_ids": ["startup_founder"],
        "related_company_ids": ["stripe", "notion"],
        "submission_type": "demo_link",
    },
    {
        "id": "developer_onboarding_guide",
        "title": "Developer Onboarding Guide & Sample Integration",
        "brief": "Write a real onboarding guide plus a working sample integration for an actual public API or SDK, tested against the real thing, not described from memory.",
        "difficulty_level": "intermediate",
        "estimated_hours": 5,
        "target_skill_ids": ["programming", "public_speaking_writing"],
        "related_career_ids": ["developer_relations_engineer"],
        "related_company_ids": ["github", "stripe"],
        "submission_type": "github_repo",
    },
    {
        "id": "community_needs_assessment_grant_proposal",
        "title": "Community Needs Assessment & Grant Proposal",
        "brief": "Conduct a real needs assessment for an actual community or cause (even a small local one) and write a genuine grant proposal grounded in what you actually found.",
        "difficulty_level": "intermediate",
        "estimated_hours": 7,
        "target_skill_ids": ["interviewing_research", "public_speaking_writing", "financial_reporting"],
        "related_career_ids": ["ngo_program_manager"],
        "related_company_ids": ["oxfam"],
        "submission_type": "writeup",
    },
    {
        "id": "urban_green_space_proposal",
        "title": "Urban Green Space Proposal",
        "brief": "Use real mapping data to propose a genuine new green space or park for an actual neighborhood, with a real case for why that specific location makes sense.",
        "difficulty_level": "intermediate",
        "estimated_hours": 7,
        "target_skill_ids": ["gis_mapping", "policy_analysis", "stakeholder_communication"],
        "related_career_ids": ["urban_planner"],
        "related_company_ids": [],
        "submission_type": "writeup",
    },
    {
        "id": "species_population_survey_design",
        "title": "Species Population Survey Design",
        "brief": "Design a real field survey method for estimating a local species' population, and if possible, run a small genuine version of it and report honest results.",
        "difficulty_level": "intermediate",
        "estimated_hours": 8,
        "target_skill_ids": ["experimental_design", "gis_mapping", "statistical_analysis"],
        "related_career_ids": ["conservation_biologist"],
        "related_company_ids": ["nature_conservancy"],
        "submission_type": "writeup",
    },
]


async def seed() -> None:
    client = get_supabase_client()
    projects = [Project.model_validate(p) for p in PROJECTS]

    def _upsert() -> None:
        client.table("projects").upsert([p.model_dump(mode="json") for p in projects]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(projects)} projects.")


if __name__ == "__main__":
    asyncio.run(seed())

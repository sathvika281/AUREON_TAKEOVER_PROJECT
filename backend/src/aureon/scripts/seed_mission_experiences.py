"""One-time seed script for the Experience Lab / Life Missions merge's
"Mission Experiences" catalog.

Run via: python -m aureon.scripts.seed_mission_experiences

One real, specific, achievable experience per existing Life Mission (22
entries — see seed_life_missions.py for the catalog these reference by
id). Every entry sets `related_life_mission_ids` — the deliberate,
curated editorial link this merge adds (domain/models/experiment.py) —
distinct from the generous related_tags substring matching
life_mission_engine.py already does for evidence gathering. Same
honesty/quality bar as seed_experiments.py: concrete, achievable, safe,
low-cost activities, never generic ("Research climate change"). Purely
additive — does not touch the 14 existing career-oriented experiments.
Idempotent: upserts by id, safe to re-run. Requires migration
0022_experience_lab_mission_links.sql applied first (adds the
related_life_mission_ids column).
"""

import asyncio

from aureon.domain.models.experiment import Experiment
from aureon.services.supabase.client import get_supabase_client

MISSION_EXPERIENCES: list[dict] = [
    {
        "id": "exp_mission_build_technology",
        "title": "Design a Tiny Tool for a Real Annoyance",
        "category": "analyze_problem",
        "description": "Design the logic for a small tool that would fix something that mildly annoys you.",
        "instructions": (
            "Pick something that mildly annoys you in daily life — forgetting to drink water, losing track of "
            "homework deadlines, always misplacing your keys. On paper or in a notes app, design exactly what a "
            "simple tool would need to do to fix it: what triggers it, what it shows you, what action it "
            "suggests. You're not coding it yet — you're designing its logic, step by step."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up — no coding required.",
        "related_world": "AI",
        "target_traits": ["analytical_thinking", "creativity"],
        "related_life_mission_ids": ["mission_build_technology"],
        "reflection_prompt": "Did figuring out the logic feel like solving a puzzle, or like a chore?",
    },
    {
        "id": "exp_mission_solve_climate_problems",
        "title": "Audit Your Household's Energy Use",
        "category": "analyze_problem",
        "description": "Track a day of real energy use and propose one realistic reduction.",
        "instructions": (
            "Track your household's electricity use for one day — note every major appliance or device used and "
            "roughly how long (lights, AC or heater, fridge, TV, chargers). Identify the three activities that "
            "consume the most energy. Propose one realistic, specific reduction — not 'use less energy,' but "
            "something concrete like 'unplug the router at night' or 'run the AC one degree warmer.'"
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Business",
        "target_traits": ["analytical_thinking", "systems_thinking"],
        "related_life_mission_ids": ["mission_solve_climate_problems"],
        "reflection_prompt": "Did solving this problem feel meaningful, or just like an exercise?",
    },
    {
        "id": "exp_mission_improve_healthcare",
        "title": "Map a Real Healthcare Access Barrier",
        "category": "analyze_problem",
        "description": "Identify concrete barriers a patient faces getting real care, and propose one fix.",
        "instructions": (
            "Think of a real healthcare access problem in your community — long wait times, cost, distance to a "
            "clinic, lack of specialists. Write down three concrete barriers a patient would face getting the "
            "care they need, ordered from most to least difficult to solve. Propose one small, realistic idea "
            "for reducing just one of those barriers."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Healthcare",
        "target_traits": ["empathy", "analytical_thinking"],
        "related_life_mission_ids": ["mission_improve_healthcare"],
        "reflection_prompt": "Which barrier surprised you the most once you thought it through?",
    },
    {
        "id": "exp_mission_educate_people",
        "title": "Teach a Concept, Then Redesign the Explanation",
        "category": "observe_design",
        "description": "Teach something real, watch where the other person gets stuck, and redesign it.",
        "instructions": (
            "Pick something you understand well and explain it to a younger student, sibling, or friend who "
            "doesn't. Watch closely for the exact moment they look confused. Afterward, redesign your "
            "explanation — what would you say differently the second time, and why?"
        ),
        "estimated_minutes": 25,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Psychology",
        "target_traits": ["communication", "empathy"],
        "related_life_mission_ids": ["mission_educate_people"],
        "reflection_prompt": "Did helping someone understand something energize you, or drain you?",
    },
    {
        "id": "exp_mission_discover_knowledge",
        "title": "Chase One Real Question to Its Source",
        "category": "read_abstract",
        "description": "Actually research one genuine question, using a real source, not just a search snippet.",
        "instructions": (
            "Pick one 'why' or 'how' question you've genuinely wondered about recently. Spend 20 minutes "
            "actually researching it using a real source — an article, a documentary clip, a textbook — not "
            "just the first search snippet. Write down what you learned and one new question it raised."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "AI",
        "target_traits": ["curiosity", "analytical_thinking"],
        "related_life_mission_ids": ["mission_discover_knowledge"],
        "reflection_prompt": "Did the new question you found feel exciting or exhausting?",
    },
    {
        "id": "exp_mission_create_art",
        "title": "Make Something From a Constraint",
        "category": "observe_design",
        "description": "Create something real using one deliberate creative constraint.",
        "instructions": (
            "Create something — a drawing, a short piece of writing, a piece of music, a photo series — using "
            "one deliberate constraint: only three colors, only 50 words, only sounds recorded from your house. "
            "Notice how the constraint shapes what you end up making."
        ),
        "estimated_minutes": 30,
        "age_appropriate_note": "Suitable for all ages.",
        "related_world": "Arts",
        "target_traits": ["creativity"],
        "related_life_mission_ids": ["mission_create_art"],
        "reflection_prompt": "Did the constraint make it harder to create, or did it help?",
    },
    {
        "id": "exp_mission_entertain_millions",
        "title": "Storyboard Three Seconds That Hook Someone",
        "category": "observe_design",
        "description": "Design the exact opening moment of something meant to grab attention instantly.",
        "instructions": (
            "Pick a story, joke, or idea you find genuinely entertaining. Storyboard — sketch or write, moment "
            "by moment — the first three seconds of how you'd present it to grab someone's attention "
            "immediately. No slow build-up allowed: what's the very first thing they see or hear?"
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Arts",
        "target_traits": ["creativity", "communication"],
        "related_life_mission_ids": ["mission_entertain_millions"],
        "reflection_prompt": "What did you cut to make those three seconds work?",
    },
    {
        "id": "exp_mission_protect_nature",
        "title": "Track One Species or Habitat Near You",
        "category": "read_abstract",
        "description": "Research one specific real threat facing a species or habitat near you.",
        "instructions": (
            "Identify one plant, animal, or natural habitat near where you live that seems under some kind of "
            "pressure — development, pollution, changing weather patterns. Spend 20 minutes researching what's "
            "actually threatening it and one real organization already working to protect it."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Business",
        "target_traits": ["curiosity", "analytical_thinking"],
        "related_life_mission_ids": ["mission_protect_nature"],
        "reflection_prompt": "Did learning the specifics make you feel more or less hopeful?",
    },
    {
        "id": "exp_mission_build_businesses",
        "title": "Find a Real, Small, Solvable Problem to Pitch a Fix For",
        "category": "analyze_problem",
        "description": "Notice a genuinely small real-world problem and sketch a one-paragraph pitch to fix it.",
        "instructions": (
            "Spend a day noticing small problems people around you complain about. Pick one that's genuinely "
            "small enough to imagine solving. Sketch a one-paragraph pitch: who has this problem, what you'd "
            "offer them, and why they'd actually pay for it."
        ),
        "estimated_minutes": 25,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Business",
        "target_traits": ["analytical_thinking", "leadership"],
        "related_life_mission_ids": ["mission_build_businesses"],
        "reflection_prompt": "Did pitching the idea feel natural, or forced?",
    },
    {
        "id": "exp_mission_explore_space",
        "title": "Follow One Real Space Mission's Actual Data",
        "category": "read_abstract",
        "description": "Read a real, currently active space mission's actual recent findings.",
        "instructions": (
            "Pick one real, currently active space mission — a rover, a telescope, a probe. Spend 20 minutes "
            "reading its most recent real findings or images, not just headlines. Write down one specific thing "
            "it discovered and one question its findings leave unanswered."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Space",
        "target_traits": ["curiosity", "analytical_thinking"],
        "related_life_mission_ids": ["mission_explore_space"],
        "reflection_prompt": "What's one question this mission's findings leave unanswered for you?",
    },
    {
        "id": "exp_mission_improve_government",
        "title": "Trace How One Local Decision Actually Gets Made",
        "category": "analyze_problem",
        "description": "Research the real process behind one local civic decision and its real obstacles.",
        "instructions": (
            "Pick one real local issue — a new bus route, a park, a school policy. Research who is actually "
            "responsible for deciding it and what steps are involved. Write down the three biggest obstacles to "
            "getting it decided quickly and fairly."
        ),
        "estimated_minutes": 25,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Business",
        "target_traits": ["analytical_thinking", "systems_thinking"],
        "related_life_mission_ids": ["mission_improve_government"],
        "reflection_prompt": "Did tracing the process make the system feel more or less trustworthy to you?",
    },
    {
        "id": "exp_mission_help_communities",
        "title": "Spend an Hour Actually Listening",
        "category": "reflect_on_workflow",
        "description": "Have a real conversation focused entirely on listening, not solving.",
        "instructions": (
            "Spend an hour volunteering, or simply having a real conversation, with someone from a different "
            "background or generation than you. Don't try to solve anything — just listen for what they say "
            "matters most to them."
        ),
        "estimated_minutes": 60,
        "age_appropriate_note": "Suitable for middle school and up, with a trusted adult's guidance if needed.",
        "related_world": "Psychology",
        "target_traits": ["empathy", "communication"],
        "related_life_mission_ids": ["mission_help_communities"],
        "reflection_prompt": "What surprised you most about what mattered to them?",
    },
    {
        "id": "exp_mission_advance_science",
        "title": "Design (Not Run) a Real Experiment",
        "category": "analyze_problem",
        "description": "Design a fair, testable experiment for a question you're genuinely curious about.",
        "instructions": (
            "Pick a question you're curious about that you could actually test — for example, 'does background "
            "noise affect how fast I do homework?' Design a simple experiment: what you'd change, what you'd "
            "measure, and what would count as a real result. Don't run it — just design it rigorously enough "
            "that someone else could."
        ),
        "estimated_minutes": 25,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "AI",
        "target_traits": ["analytical_thinking", "persistence"],
        "related_life_mission_ids": ["mission_advance_science"],
        "reflection_prompt": "What was the hardest part of designing it fairly?",
    },
    {
        "id": "exp_mission_fight_poverty",
        "title": "Map One Real Economic Barrier",
        "category": "analyze_problem",
        "description": "Research one specific, real mechanism by which poverty limits opportunity.",
        "instructions": (
            "Research one specific way poverty limits opportunity in a community you know — transportation "
            "cost blocking job access, lack of affordable childcare, unreliable internet for schoolwork. "
            "Identify the actual mechanism, not just 'poverty is hard,' and propose one small, realistic "
            "intervention."
        ),
        "estimated_minutes": 25,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Business",
        "target_traits": ["empathy", "analytical_thinking"],
        "related_life_mission_ids": ["mission_fight_poverty"],
        "reflection_prompt": "Did the mechanism you found feel fixable, or deeply structural?",
    },
    {
        "id": "exp_mission_build_better_cities",
        "title": "Redesign One Uncomfortable Public Space",
        "category": "observe_design",
        "description": "Redesign a real, poorly-designed public space near you.",
        "instructions": (
            "Pick a public space near you that feels poorly designed — a bus stop with no shade, a crosswalk "
            "that feels unsafe, a park with nowhere to sit. Sketch what you'd change and why, thinking "
            "specifically about who actually uses that space."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Design",
        "target_traits": ["systems_thinking", "creativity"],
        "related_life_mission_ids": ["mission_build_better_cities"],
        "reflection_prompt": "What problem do you think the original design was trying to solve, even if it failed?",
    },
    {
        "id": "exp_mission_improve_mental_health",
        "title": "Track Your Own Mental Load for a Day",
        "category": "reflect_on_workflow",
        "description": "Notice and log your own stress, focus, and calm across one real day.",
        "instructions": (
            "For one full day, jot down every moment you noticed stress, focus, or calm — and what caused it. "
            "At the end of the day, look back for one real pattern in what helped and what didn't."
        ),
        "estimated_minutes": 15,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Psychology",
        "target_traits": ["empathy", "curiosity"],
        "related_life_mission_ids": ["mission_improve_mental_health"],
        "reflection_prompt": "Did tracking it change how you experienced the day itself?",
    },
    {
        "id": "exp_mission_design_better_products",
        "title": "Redesign a Confusing Interface",
        "category": "observe_design",
        "description": "Find a real confusing interface and redesign the exact screen that confused you.",
        "instructions": (
            "Find an app, website, or physical product interface that confused you recently. Sketch exactly "
            "where you got stuck, then redesign that one screen or control to be clearer — explain what you "
            "changed and why."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Design",
        "target_traits": ["creativity", "systems_thinking"],
        "related_life_mission_ids": ["mission_design_better_products"],
        "reflection_prompt": "What assumption do you think the original designer got wrong?",
    },
    {
        "id": "exp_mission_protect_wildlife",
        "title": "Research One Real Conservation Success Story",
        "category": "read_abstract",
        "description": "Read about a real, documented case of a species or habitat being successfully protected.",
        "instructions": (
            "Find one real, documented case where a species or habitat was successfully protected or recovered. "
            "Read about what specifically worked. Write down the one intervention that mattered most, and one "
            "thing that surprised you about how long it took."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Business",
        "target_traits": ["curiosity", "persistence"],
        "related_life_mission_ids": ["mission_protect_wildlife"],
        "reflection_prompt": "What made you believe, or doubt, that this kind of success is repeatable?",
    },
    {
        "id": "exp_mission_improve_agriculture",
        "title": "Trace Your Food's Real Journey",
        "category": "analyze_problem",
        "description": "Research where one real food item actually came from and find a real inefficiency.",
        "instructions": (
            "Pick one food item you ate this week. Research where it was actually grown, how it got to you, "
            "and one real inefficiency or waste point along that journey. Propose one realistic improvement."
        ),
        "estimated_minutes": 20,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Business",
        "target_traits": ["analytical_thinking", "systems_thinking"],
        "related_life_mission_ids": ["mission_improve_agriculture"],
        "reflection_prompt": "Did tracing it change how you think about that food?",
    },
    {
        "id": "exp_mission_preserve_culture_and_heritage",
        "title": "Record One Real Story Before It's Forgotten",
        "category": "read_abstract",
        "description": "Interview a real person and preserve one real story in their own words.",
        "instructions": (
            "Ask an older family member or community member to tell you one real story from their life or your "
            "shared history that you've never heard in detail. Write it down as faithfully as you can, in "
            "their own words where possible."
        ),
        "estimated_minutes": 30,
        "age_appropriate_note": "Suitable for all ages, with a family member's involvement.",
        "related_world": "Arts",
        "target_traits": ["communication", "empathy"],
        "related_life_mission_ids": ["mission_preserve_culture_and_heritage"],
        "reflection_prompt": "What part of their story do you think would be lost if no one wrote it down?",
    },
    {
        "id": "exp_mission_advance_human_rights",
        "title": "Research One Real, Specific Rights Issue",
        "category": "analyze_problem",
        "description": "Research one concrete, specific human-rights issue and who is working on it.",
        "instructions": (
            "Pick one specific, real human-rights issue — not a broad topic, but something concrete, like "
            "access to clean water in a specific region, or a specific group's voting access. Research the "
            "actual current state of that issue and one organization working directly on it."
        ),
        "estimated_minutes": 25,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Psychology",
        "target_traits": ["empathy", "analytical_thinking"],
        "related_life_mission_ids": ["mission_advance_human_rights"],
        "reflection_prompt": "What made this issue feel more real to you once you looked at the specifics?",
    },
    {
        "id": "exp_mission_improve_financial_literacy",
        "title": "Build a Real One-Month Budget",
        "category": "analyze_problem",
        "description": "Build an actual budget with real trade-offs, not a hypothetical exercise.",
        "instructions": (
            "Using real or realistic numbers — an allowance, part-time job income, or a hypothetical "
            "entry-level salary — build an actual one-month budget covering needs, savings, and one goal. "
            "Identify the one trade-off that was hardest to make."
        ),
        "estimated_minutes": 25,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Business",
        "target_traits": ["analytical_thinking", "decision_style"],
        "related_life_mission_ids": ["mission_improve_financial_literacy"],
        "reflection_prompt": "What surprised you about where the money actually needed to go?",
    },
]


async def seed() -> None:
    client = get_supabase_client()
    experiments = [Experiment.model_validate(e) for e in MISSION_EXPERIENCES]

    def _upsert() -> None:
        client.table("experiments").upsert([e.model_dump(mode="json") for e in experiments]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(experiments)} mission experiences.")


if __name__ == "__main__":
    asyncio.run(seed())

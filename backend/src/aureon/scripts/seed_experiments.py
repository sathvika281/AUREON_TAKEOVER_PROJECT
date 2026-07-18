"""One-time seed script for Discover Batch 2's Career Experiments
catalog.

Run via: python -m aureon.scripts.seed_experiments

A modest (~14), honestly-labeled set of small, achievable,
age-appropriate activities spanning all 5 experiment categories and
several of the 7 onboarding Worlds. Every entry carries its own
`source_note` honesty disclaimer (see domain/models/experiment.py) —
never presented as a professionally-validated assessment. Idempotent:
upserts by id, safe to re-run.
"""

import asyncio

from aureon.domain.models.experiment import Experiment
from aureon.services.supabase.client import get_supabase_client

EXPERIMENTS: list[dict] = [
    {
        "id": "exp_read_ai_abstract",
        "title": "Read a Simplified AI Research Abstract",
        "category": "read_abstract",
        "description": "Read a short, simplified summary of a real AI research paper and jot down what you notice.",
        "instructions": (
            "Researchers recently tested whether a language model could explain its own reasoning step-by-step "
            "before giving an answer, instead of just giving the answer directly. They found the model made "
            "fewer mistakes on multi-step math problems when it explained its steps first — but it also took "
            "longer and sometimes explained its way into a wrong answer it wouldn't have made otherwise.\n\n"
            "Read this a couple of times. What questions does it raise for you? What would you want to test next?"
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for middle school and up — no technical background required.",
        "related_world": "AI",
        "target_traits": ["analytical_thinking", "curiosity"],
        "reflection_prompt": "What was the most interesting or confusing part of what you just read?",
    },
    {
        "id": "exp_read_space_abstract",
        "title": "Read a Simplified Space Research Abstract",
        "category": "read_abstract",
        "description": "Read a short, simplified summary of a real space-science finding.",
        "instructions": (
            "Scientists studying a distant moon found that its icy surface has cracks that open and close as "
            "the moon is stretched and squeezed by the planet it orbits. Water from below may be pushed up "
            "through these cracks. Some researchers think this makes the moon worth studying for signs of "
            "conditions that could support life — though no one has found any yet.\n\n"
            "What would you want to know next if you were the scientist reading this?"
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Space",
        "target_traits": ["analytical_thinking", "curiosity"],
        "reflection_prompt": "What's one question this finding leaves unanswered for you?",
    },
    {
        "id": "exp_debug_tiny_bug",
        "title": "Debug a Tiny Piece of Code",
        "category": "debug_code",
        "description": "A small, deliberately broken piece of code is waiting for you — find why it's wrong.",
        "instructions": (
            "Here's a short program meant to add up a list of numbers:\n\n"
            "total = 0\nfor number in [4, 8, 15, 16, 23]:\n    total = number\nprint(total)\n\n"
            "It's supposed to print the sum of all five numbers, but it doesn't. Read it carefully, line by "
            "line. What do you think it actually prints, and why? What single change would fix it?"
        ),
        "estimated_minutes": 15,
        "age_appropriate_note": "Suitable for high school and up — no prior coding experience assumed.",
        "related_world": "AI",
        "target_traits": ["analytical_thinking", "persistence", "systems_thinking"],
        "reflection_prompt": "Walk through how you figured out what was wrong — what did you try first?",
    },
    {
        "id": "exp_debug_logic_puzzle",
        "title": "Debug a Small Business Logic Puzzle",
        "category": "debug_code",
        "description": "A simple set of pricing rules is producing a wrong result — trace through why.",
        "instructions": (
            "A small shop's discount rule is: 'If you buy 3 or more items, you get 10% off your whole order. "
            "Otherwise, no discount.' A customer buys 2 items worth $50 total and is charged $45. Something's "
            "off. Work through the rule step by step against what actually happened, and figure out where the "
            "logic broke down."
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Business",
        "target_traits": ["analytical_thinking", "systems_thinking"],
        "reflection_prompt": "What was the actual mistake, and how did you track it down?",
    },
    {
        "id": "exp_analyze_traffic_problem",
        "title": "Analyze a Real-World Traffic Problem",
        "category": "analyze_problem",
        "description": "Think through a real city planning problem with no single right answer.",
        "instructions": (
            "A busy street near a school has frequent near-miss accidents right at drop-off/pickup time, but "
            "is calm the rest of the day. The city has a limited budget and can only pick one fix: a permanent "
            "traffic light, a crossing guard during school hours, or a speed bump. Think through the tradeoffs "
            "of each option — cost, effectiveness, side effects — before landing on a recommendation."
        ),
        "estimated_minutes": 15,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Business",
        "target_traits": ["analytical_thinking", "systems_thinking", "empathy"],
        "reflection_prompt": "What tradeoff was hardest to weigh, and what did you end up recommending?",
    },
    {
        "id": "exp_analyze_health_problem",
        "title": "Analyze a Real-World Public Health Problem",
        "category": "analyze_problem",
        "description": "Think through a real public-health tradeoff with competing real constraints.",
        "instructions": (
            "A small clinic has one nurse and 40 patients waiting on a busy day. Some patients have minor "
            "issues that will resolve on their own; a few have symptoms that could be serious but aren't "
            "obviously urgent yet. The nurse has to decide an order to see people in, with incomplete "
            "information about each case. What would you want the nurse to consider, and why?"
        ),
        "estimated_minutes": 15,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Healthcare",
        "target_traits": ["analytical_thinking", "empathy", "systems_thinking"],
        "reflection_prompt": "What would you have found hardest about making this call in the moment?",
    },
    {
        "id": "exp_observe_app_design",
        "title": "Observe a Design You Use Every Day",
        "category": "observe_design",
        "description": "Look closely at an app or object you already use, and notice its design choices.",
        "instructions": (
            "Pick any app on your phone that you open almost every day. Open it and spend two minutes just "
            "looking — not using it for its normal purpose, just noticing. What's the first thing your eye "
            "goes to? What's easy to find? What feels confusing or cluttered? Would you have designed any part "
            "of it differently?"
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for all ages — uses an app the student already has.",
        "related_world": "Design",
        "target_traits": ["creativity", "analytical_thinking"],
        "reflection_prompt": "What's one design choice you'd change, and what would you change it to?",
    },
    {
        "id": "exp_observe_poster_design",
        "title": "Observe a Poster or Album Cover's Design",
        "category": "observe_design",
        "description": "Look closely at a real piece of visual design and notice how it's put together.",
        "instructions": (
            "Find a movie poster, album cover, or ad you find visually striking — one you can look at for a "
            "minute. Notice: what draws your eye first? How are color and space being used? What's the poster "
            "trying to make you feel, and what specific choices create that feeling?"
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for all ages.",
        "related_world": "Arts",
        "target_traits": ["creativity", "communication"],
        "reflection_prompt": "What feeling do you think this design was going for, and did it work on you?",
    },
    {
        "id": "exp_reflect_scientist_workflow",
        "title": "Reflect After Watching a Scientist's Workflow",
        "category": "reflect_on_workflow",
        "description": "Watch a short description of how a researcher spends a real workday, then reflect.",
        "instructions": (
            "A genomics researcher's typical day: 2 hours reviewing overnight sequencing results, a meeting "
            "comparing notes with two colleagues on unexpected data, an hour writing up findings so far, and "
            "the rest of the day troubleshooting a lab instrument that's been giving inconsistent readings. "
            "Much of the day is problem-solving and waiting, not dramatic discovery moments."
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Healthcare",
        "target_traits": ["persistence", "analytical_thinking"],
        "reflection_prompt": "Which part of this day would energize you, and which part would drain you?",
    },
    {
        "id": "exp_reflect_designer_workflow",
        "title": "Reflect After Watching a Designer's Workflow",
        "category": "reflect_on_workflow",
        "description": "Watch a short description of how a product designer spends a real workday, then reflect.",
        "instructions": (
            "A product designer's typical day: an hour sketching five different versions of the same screen, "
            "a meeting where three of those five ideas get rejected by teammates, an afternoon rebuilding the "
            "two that survived based on that feedback, and a short user-testing session where someone gets "
            "confused by a button the designer thought was obvious."
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Design",
        "target_traits": ["creativity", "persistence", "communication"],
        "reflection_prompt": "How would you feel about having your ideas rejected in front of the team like that?",
    },
    {
        "id": "exp_reflect_founder_workflow",
        "title": "Reflect After Watching a Founder's Workflow",
        "category": "reflect_on_workflow",
        "description": "Watch a short description of how an early-stage founder spends a real workday, then reflect.",
        "instructions": (
            "A startup founder's typical day: a morning call with a customer who's unhappy about a bug, an "
            "hour reviewing whether the product is actually solving the problem it was built for, a difficult "
            "conversation with a co-founder about slowing down on a feature, and an evening spent replying to "
            "emails because there's no one else on the team to do it yet."
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Business",
        "target_traits": ["persistence", "communication", "systems_thinking"],
        "reflection_prompt": "What part of this day would be hardest for you to sit with, and why?",
    },
    {
        "id": "exp_analyze_conflict_scenario",
        "title": "Analyze a Real Peer Conflict Scenario",
        "category": "analyze_problem",
        "description": "Think through a realistic disagreement between two people with valid but different views.",
        "instructions": (
            "Two group project partners disagree: one wants to submit a solid, safe version of the project "
            "early; the other wants to keep improving it right up to the deadline, risking a late submission "
            "for a better result. Both have real, fair reasons for their position. If a friend asked you to "
            "help them think through this, what would you want to understand from each side first?"
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Psychology",
        "target_traits": ["empathy", "communication"],
        "reflection_prompt": "Which person's position did you personally relate to more, and why?",
    },
    {
        "id": "exp_read_psychology_abstract",
        "title": "Read a Simplified Psychology Research Abstract",
        "category": "read_abstract",
        "description": "Read a short, simplified summary of a real psychology finding.",
        "instructions": (
            "Researchers asked people to recall a stressful event either by writing about the facts of what "
            "happened, or by writing about how it made them feel. People who wrote about their feelings "
            "reported feeling somewhat better a week later than people who only wrote about the facts — "
            "though the effect was small and didn't hold for everyone.\n\n"
            "What would make you trust or doubt this finding more?"
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for high school and up.",
        "related_world": "Psychology",
        "target_traits": ["analytical_thinking", "empathy"],
        "reflection_prompt": "Does this finding match or contradict your own experience with stress? How?",
    },
    {
        "id": "exp_observe_lab_layout_design",
        "title": "Observe How a Science Lab Space Is Designed",
        "category": "observe_design",
        "description": "Look at a photo or description of a research lab and notice how the space is organized.",
        "instructions": (
            "Picture a genomics lab: sequencing machines along one wall, a sterile prep bench in the center "
            "with its own separate air filtering, computers for data analysis against the opposite wall, and "
            "a whiteboard covered in half-erased notes near the door. Every placement solves a real problem — "
            "keeping samples uncontaminated, keeping loud machines away from focused work, keeping the team's "
            "open questions visible."
        ),
        "estimated_minutes": 10,
        "age_appropriate_note": "Suitable for middle school and up.",
        "related_world": "Healthcare",
        "target_traits": ["systems_thinking", "analytical_thinking"],
        "reflection_prompt": "What problem do you think each part of this layout was trying to solve?",
    },
]


async def seed() -> None:
    client = get_supabase_client()
    experiments = [Experiment.model_validate(e) for e in EXPERIMENTS]

    def _upsert() -> None:
        client.table("experiments").upsert([e.model_dump(mode="json") for e in experiments]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(experiments)} experiments.")


if __name__ == "__main__":
    asyncio.run(seed())

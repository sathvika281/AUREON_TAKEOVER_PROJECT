"""One-time content-completion script — fills in real, multi-stage
`career_journey` (and `day_in_the_life`, where also empty) for the 15
real Mentor rows that were missing them, matching the quality bar the
other 101 mentors already have (school/early interest -> university ->
first job -> a real setback/transition -> turning point -> current
role). Expert Connect / Journey Stories purpose split — these become
each expert's canonical, single-source-of-truth career journey; no
`CareerStory` row is created or touched for any of them.

Uses targeted `.update()` per mentor id, never `.upsert()` — same
discipline as `enrich_career_stories.py`. Illustrative composite
personas, not real named individuals (same convention as every other
seeded Mentor row).

Run via: python -m aureon.scripts.complete_mentor_career_journeys

Idempotent: safe to re-run.
"""

import asyncio

from aureon.services.supabase.client import get_supabase_client

ENRICHMENTS: dict[str, dict] = {
    "mentor_elena_vasquez": {
        "career_journey": [
            {"stage": "school", "label": "Taking apart dead batteries", "description": "Grew up prying open household electronics just to see why the batteries inside always died first.", "year_label": "Year 0"},
            {"stage": "university", "label": "Chemistry, not physics", "description": "Started a chemistry degree, and nearly switched to pure physics after a discouraging first-year advisor questioned the choice.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "PhD in materials science", "description": "Chose a doctoral project on electrode degradation instead — the actual materials, not the abstract theory.", "year_label": "Year 4"},
            {"stage": "failure", "label": "Two years on a dead end", "description": "Spent two years on a research direction that ultimately produced no publishable result.", "year_label": "Year 7"},
            {"stage": "turning_point", "label": "An undergrad's overlooked insight", "description": "A student with unremarkable grades noticed a pattern in failed-experiment data that the whole lab had missed — it reshaped how she evaluates who's worth mentoring.", "year_label": "Year 9"},
            {"stage": "current_role", "label": "Professor, Aurora Institute of Technology", "description": "Runs a lab studying next-generation battery materials, known for taking on students with more curiosity than formal credentials.", "year_label": "Year 14"},
        ],
        "day_in_the_life": "Mornings are usually grant writing or reviewing a student's failed-experiment notebook for what it actually shows, not just what it was supposed to show. Afternoons are lab meetings, one-on-ones with students stuck on a problem, and the occasional hour actually at the bench when a result needs a second pair of trained hands.",
    },
    "mentor_priya_nair": {
        "career_journey": [
            {"stage": "school", "label": "Biology labs and a coding club", "description": "Enjoyed dissection labs as much as an after-school programming club most classmates saw as unrelated.", "year_label": "Year 0"},
            {"stage": "university", "label": "Biology degree, a 'throwaway' elective", "description": "Studied biology, then took a programming elective mostly to fill a schedule gap — it ended up mattering more than any core course.", "year_label": "Year 1"},
            {"stage": "career_transition", "label": "Bioinformatics master's", "description": "Realized pure wet-lab work wasn't where her strengths were and moved into a master's program merging biology with computation.", "year_label": "Year 4"},
            {"stage": "first_job", "label": "Research assistant, genomics + early ML", "description": "Joined a lab combining genomic datasets with early machine learning models, doing unglamorous data-cleaning work for over a year.", "year_label": "Year 6"},
            {"stage": "turning_point", "label": "A model finds what years of manual review missed", "description": "A model she built surfaced a real pattern in the data that a wet-lab colleague had been manually searching for, unsuccessfully, for years.", "year_label": "Year 7"},
            {"stage": "current_role", "label": "Computational Biology Researcher", "description": "Works at the intersection of genomics and machine learning, mentoring students moving between biology and computer science.", "year_label": "Year 9"},
        ],
        "day_in_the_life": "A mix of writing analysis code, meeting with wet-lab collaborators to translate between the two disciplines' assumptions, and reading papers from fields adjacent to her own. No two weeks look quite the same, which she considers the actual appeal of the work.",
    },
    "mentor_marcus_chen": {
        "career_journey": [
            {"stage": "school", "label": "Self-taught from tutorials", "description": "Learned programming from online tutorials since no formal computer science classes existed at his school.", "year_label": "Year 0"},
            {"stage": "university", "label": "Computer science degree", "description": "Studied computer science and seriously considered a PhD track through most of it.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Junior backend engineer", "description": "Chose industry over graduate school after an internship made the day-to-day of research feel less appealing than shipping real systems.", "year_label": "Year 4"},
            {"stage": "failure", "label": "A costly outage", "description": "A payments-adjacent system he built caused a multi-hour outage that cost the company real money and trust.", "year_label": "Year 6"},
            {"stage": "turning_point", "label": "Leading the rebuild", "description": "Leading the postmortem and the subsequent rebuild — not the original build — is what earned him lasting technical credibility on the team.", "year_label": "Year 7"},
            {"stage": "promotion", "label": "Senior Backend Engineer", "description": "Promoted after the rebuild, now mentors students weighing engineering against research paths.", "year_label": "Year 11"},
        ],
        "day_in_the_life": "Roughly half design reviews and mentoring junior engineers, half still writing code — mostly on the reliability-critical paths few people want to own. Meetings cluster in the mornings; the afternoons are protected for deep work whenever possible.",
    },
    "mentor_aisha_osei": {
        "career_journey": [
            {"stage": "school", "label": "Drawn to both art and people", "description": "Split time between art classes and an interest in why people behaved the way they did, without a clear sense of how those two things connected.", "year_label": "Year 0"},
            {"stage": "university", "label": "Psychology, not design", "description": "Studied psychology, not design — the connection to design only became obvious years later.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "Self-taught design portfolio", "description": "Built a design portfolio independently after graduating, without a formal design degree to point to.", "year_label": "Year 3"},
            {"stage": "first_job", "label": "Junior designer, proving credibility", "description": "Spent the first two years having to prove design credibility in every meeting, since her background didn't match the expected pattern.", "year_label": "Year 4"},
            {"stage": "turning_point", "label": "A usability study reverses a decision", "description": "A usability study she ran directly reversed a leadership decision that had already been greenlit — the first time her research changed a real outcome.", "year_label": "Year 6"},
            {"stage": "promotion", "label": "UX Design Lead", "description": "Leads design at a mid-size product company, bridging her original psychology background with visual design.", "year_label": "Year 10"},
        ],
        "day_in_the_life": "A blend of reviewing designs from her team, running or analyzing user research sessions, and defending research findings in meetings where the data contradicts what stakeholders expected to hear.",
    },
    "mentor_daniel_kim": {
        "career_journey": [
            {"stage": "university", "label": "Engineering degree", "description": "Studied engineering with no particular plan beyond a stable, well-regarded career.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Corporate energy role", "description": "Took a stable corporate energy job — secure, but increasingly unfulfilling over several years.", "year_label": "Year 2"},
            {"stage": "career_transition", "label": "Left corporate to found a startup", "description": "Left a stable role to found a climate-hardware startup, against the advice of most people around him.", "year_label": "Year 9"},
            {"stage": "failure", "label": "The first prototype fails", "description": "The first hardware prototype failed under real-world conditions, burning through most of the startup's early funding.", "year_label": "Year 10"},
            {"stage": "turning_point", "label": "A narrower pivot finds real customers", "description": "Pivoting to a much narrower product than originally envisioned finally found paying customers.", "year_label": "Year 11"},
            {"stage": "current_role", "label": "Founder, climate-hardware startup", "description": "Mentors aspiring founders on the realities of early-stage building, past the pitch-deck version of the story.", "year_label": "Year 13"},
        ],
        "day_in_the_life": "No fixed pattern — some days are entirely investor conversations and hiring, others are back on the hardware floor debugging a failed test run alongside the engineering team. The founder job is whatever the company needs that week.",
    },
    "mentor_sofia_marino": {
        "career_journey": [
            {"stage": "school", "label": "A camera before a plan", "description": "Loved photography years before having any real plan to make a career out of visual storytelling.", "year_label": "Year 0"},
            {"stage": "university", "label": "An unrelated degree, then a student film", "description": "Studied a subject unrelated to film, until a single student film project made clear what she actually wanted to do.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Crew work on other people's films", "description": "Took crew jobs on other people's productions for several years, learning the craft from the ground up.", "year_label": "Year 2"},
            {"stage": "failure", "label": "Years of unstable freelance work", "description": "Spent several unstable years piecing together freelance work with no funded project of her own in sight, seriously considering leaving filmmaking entirely during the leanest stretch.", "year_label": "Year 5"},
            {"stage": "turning_point", "label": "First festival acceptance", "description": "Her first self-funded documentary was accepted into a real festival, providing the first external validation that the work could sustain a career.", "year_label": "Year 8"},
            {"stage": "current_role", "label": "Independent Documentary Filmmaker", "description": "Self-funds and directs documentaries on social issues, mentoring students exploring creative, non-traditional paths.", "year_label": "Year 12"},
        ],
        "day_in_the_life": "Highly variable by project phase — grant and fundraising emails some weeks, long stretches of travel and filming during production, and solitary editing-room hours for months at a time once footage is in hand.",
    },
    "mentor_rajesh_gupta": {
        "career_journey": [
            {"stage": "school", "label": "Philosophy of mind, informally", "description": "Read philosophy and psychology outside of class, fascinated by questions about how decisions actually get made.", "year_label": "Year 0"},
            {"stage": "university", "label": "Pre-med, then neuroscience", "description": "Started on a pre-med track before switching into neuroscience once the actual research questions became more interesting than clinical practice.", "year_label": "Year 1"},
            {"stage": "career_transition", "label": "PhD on decision-making", "description": "Pursued doctoral research specifically on how the brain makes decisions under uncertainty.", "year_label": "Year 4"},
            {"stage": "failure", "label": "A key experiment fails to replicate", "description": "An early experiment central to his thesis direction failed to replicate on a second attempt.", "year_label": "Year 6"},
            {"stage": "turning_point", "label": "The failure becomes the real question", "description": "Reframing why the result failed to replicate led to a more interesting research question than the original hypothesis.", "year_label": "Year 7"},
            {"stage": "current_role", "label": "Professor, Meridian University", "description": "Studies decision-making in the brain, and says he enjoys mentoring students who ask why more than what.", "year_label": "Year 18"},
        ],
        "day_in_the_life": "Split between teaching, running the lab's ongoing experiments, and the slower work of writing — papers, grants, and detailed feedback on student thesis drafts.",
    },
    "mentor_naomi_osei_bonsu": {
        "career_journey": [
            {"stage": "school", "label": "Seeing the access gap firsthand", "description": "Grew up seeing firsthand how uneven access to basic healthcare was in her community.", "year_label": "Year 0"},
            {"stage": "university", "label": "Public health degree", "description": "Studied public health specifically, rather than clinical medicine, drawn to the scale of the problem over individual patient care.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Field health worker", "description": "Worked directly in field health programs in low-resource settings before moving into research.", "year_label": "Year 2"},
            {"stage": "turning_point", "label": "One project's data changes local policy", "description": "Data from a specific field project she led directly influenced a real local health policy change.", "year_label": "Year 5"},
            {"stage": "current_role", "label": "Public Health Researcher, Andes Global University", "description": "Researches health policy in low-resource settings, mentoring students interested in impact-driven, evidence-based careers.", "year_label": "Year 10"},
        ],
        "day_in_the_life": "A mix of data analysis, writing for both academic and policy audiences, and periods of field travel to the communities the research is actually about — she considers staying connected to the field non-negotiable.",
    },
    "mentor_liam_oconnor": {
        "career_journey": [
            {"stage": "school", "label": "Strong at math, unsure why", "description": "Was consistently strong at mathematics without a clear sense of what career that strength was actually for.", "year_label": "Year 0"},
            {"stage": "university", "label": "Statistics, despite engineering pressure", "description": "Studied statistics and mathematics despite being repeatedly encouraged toward a more conventional engineering path.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Data analyst", "description": "Took an analyst role and found that translating data into an actual business decision was much harder than the technical analysis itself.", "year_label": "Year 2"},
            {"stage": "turning_point", "label": "A model that saved real money", "description": "Built a routing analysis that measurably reduced costs for the company — the first project that made the business impact of the work undeniable.", "year_label": "Year 5"},
            {"stage": "promotion", "label": "Data Science Manager", "description": "Promoted to manage a data science team at a logistics company, mentoring students on translating analytical skill into business impact.", "year_label": "Year 9"},
        ],
        "day_in_the_life": "Fewer hours writing code than earlier in his career, more spent reviewing his team's models, translating technical findings for non-technical stakeholders, and defending the team's priorities in planning meetings.",
    },
    "mentor_fatima_al_sayed": {
        "career_journey": [
            {"stage": "university", "label": "Education degree", "description": "Studied education with a genuine intention to teach, not to eventually build a company.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Classroom teacher", "description": "Taught in a classroom for several years, running into the same specific tooling problem over and over.", "year_label": "Year 1"},
            {"stage": "turning_point", "label": "Building her own tool", "description": "Built a rough tool for her own classroom to solve a problem no existing product handled well, and other teachers started asking for it too.", "year_label": "Year 5"},
            {"stage": "career_transition", "label": "Leaving teaching to found a company", "description": "Left teaching to turn that classroom tool into a real education-technology company.", "year_label": "Year 7"},
            {"stage": "failure", "label": "The first product fails with real teachers", "description": "The first version of the product failed when tested with actual teachers outside her own classroom — assumptions that held for her didn't generalize.", "year_label": "Year 8"},
            {"stage": "current_role", "label": "Founder, education-technology company", "description": "Mentors students combining a specific domain passion with entrepreneurship.", "year_label": "Year 11"},
        ],
        "day_in_the_life": "Equal parts product decisions, talking directly to teachers using the product, and the unglamorous operational work of running a company — payroll, hiring, and fundraising updates.",
    },
    "mentor_chris_bello": {
        "career_journey": [
            {"stage": "school", "label": "Modding games as a teenager", "description": "Spent teenage years modifying existing games rather than just playing them, without realizing that was itself a real skill.", "year_label": "Year 0"},
            {"stage": "university", "label": "Self-taught, no formal degree", "description": "Skipped a formal degree in favor of self-teaching game development directly, building small projects the whole way.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Brief studio job", "description": "Worked at a game studio briefly, finding the large-team process a poor fit for the kind of work he wanted to do.", "year_label": "Year 2"},
            {"stage": "failure", "label": "First solo game fails commercially", "description": "His first solo-developed game was a commercial failure, selling only a handful of copies.", "year_label": "Year 4"},
            {"stage": "turning_point", "label": "A second, smaller game finds its audience", "description": "A much smaller, more focused second game found a real, if niche, audience — enough to keep going.", "year_label": "Year 6"},
            {"stage": "current_role", "label": "Independent Game Developer", "description": "Builds and ships small independent games solo, mentoring students exploring creative-technical hybrid careers.", "year_label": "Year 8"},
        ],
        "day_in_the_life": "Almost entirely self-directed — some days are pure coding, others are art or sound work, and release weeks are consumed by community support and bug fixes with no one else to hand tasks to.",
    },
    "mentor_wei_zhang": {
        "career_journey": [
            {"stage": "school", "label": "Building simple machines", "description": "Built simple robotics kits as a child, more interested in making things move correctly than in any single subject.", "year_label": "Year 0"},
            {"stage": "university", "label": "Mechanical engineering", "description": "Studied mechanical engineering, gradually specializing toward the control-systems side of the field.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "PhD in robotics", "description": "Pursued a doctorate specifically in robotics, focusing on manipulation and control.", "year_label": "Year 4"},
            {"stage": "failure", "label": "A competition robot fails publicly", "description": "A robot his team built failed publicly and completely at a major competition after months of preparation.", "year_label": "Year 6"},
            {"stage": "turning_point", "label": "The failure becomes a research question", "description": "Investigating exactly why the robot failed under real conditions became the seed of his actual research focus on robustness.", "year_label": "Year 7"},
            {"stage": "current_role", "label": "Professor, Kyoto Innovation University", "description": "Leads a robotics lab focused on manipulation and control, mentoring students weighing hardware versus software-only paths.", "year_label": "Year 16"},
        ],
        "day_in_the_life": "Lab oversight, teaching, and grant work fill most days, with hands-on time at the robotics bench reserved for when a student's project hits a problem the whole team needs to see solved firsthand.",
    },
    "mentor_amara_chukwu": {
        "career_journey": [
            {"stage": "school", "label": "Stargazing without a plan", "description": "Spent a lot of time stargazing as a child with no particular career plan attached to the curiosity.", "year_label": "Year 0"},
            {"stage": "university", "label": "Physics degree", "description": "Studied physics, drawn toward astrophysics specifically once exposed to the field's open questions.", "year_label": "Year 0"},
            {"stage": "career_transition", "label": "PhD in astrophysics", "description": "Began doctoral research on exoplanet formation — years of slow, unglamorous data work with no guaranteed result.", "year_label": "Year 4"},
            {"stage": "failure", "label": "Doubting the field's practicality", "description": "Seriously doubted, mid-PhD, whether such a long-horizon, curiosity-driven field would ever lead to a stable career.", "year_label": "Year 6"},
            {"stage": "turning_point", "label": "Contributing to a real discovery", "description": "Contributed directly to a genuine exoplanet discovery, providing the first concrete validation that the years of groundwork had been worth it.", "year_label": "Year 8"},
            {"stage": "current_role", "label": "Astrophysics Researcher", "description": "Studies exoplanet formation, mentoring students drawn to long-horizon, curiosity-driven basic research.", "year_label": "Year 10"},
        ],
        "day_in_the_life": "Long stretches of data analysis punctuated by observation runs, collaboration calls with researchers in other time zones, and writing — the actual discoveries are rare relative to the volume of routine analysis behind them.",
    },
    "mentor_isabella_rossi": {
        "career_journey": [
            {"stage": "university", "label": "International relations", "description": "Studied international relations with a general interest in global inequality, without a specific career target yet.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Entry-level NGO work", "description": "Took an entry-level NGO role — low pay and high turnover among peers were the norm, not the exception.", "year_label": "Year 1"},
            {"stage": "failure", "label": "Weighing a corporate path", "description": "Seriously considered leaving for a better-paid, more traditional corporate career during a particularly difficult field posting.", "year_label": "Year 4"},
            {"stage": "turning_point", "label": "A program's real, measurable impact", "description": "A specific field program she ran produced a measurable, undeniable improvement in the community it served — reaffirming why she'd stayed.", "year_label": "Year 6"},
            {"stage": "promotion", "label": "Program Director", "description": "Now runs field programs for an international NGO, mentoring students weighing mission-driven work against traditional career tracks.", "year_label": "Year 12"},
        ],
        "day_in_the_life": "Program oversight, donor reporting, and staff management from an office when not traveling — plus real time in the field, which she insists on keeping even now that her role could otherwise be entirely administrative.",
    },
    "mentor_jordan_park": {
        "career_journey": [
            {"stage": "university", "label": "An unrelated degree", "description": "Studied a subject with no direct connection to writing or content creation as a career.", "year_label": "Year 0"},
            {"stage": "first_job", "label": "Corporate communications role", "description": "Took a stable corporate communications job that paid well but left little room for the kind of writing they actually wanted to do.", "year_label": "Year 1"},
            {"stage": "failure", "label": "Burnout and reassessment", "description": "Reached a real burnout point in the corporate role, leading to months of uncertainty about what to do instead.", "year_label": "Year 3"},
            {"stage": "career_transition", "label": "Leaving to freelance", "description": "Left the corporate job to freelance full-time, with no guaranteed clients lined up.", "year_label": "Year 4"},
            {"stage": "failure", "label": "An unstable first year", "description": "The first year of freelancing had genuinely unstable, unpredictable income.", "year_label": "Year 4"},
            {"stage": "turning_point", "label": "A sustainable client base", "description": "Built a small, sustainable base of repeat clients that finally made the income predictable enough to commit to long-term.", "year_label": "Year 6"},
            {"stage": "current_role", "label": "Freelance Writer and Content Creator", "description": "Built a full-time freelance writing and content career, mentoring students exploring independent creative work.", "year_label": "Year 7"},
        ],
        "day_in_the_life": "Mornings for the actual writing, afternoons for client calls, invoicing, and the unglamorous business-development work that most people don't see behind a freelance career.",
    },
}


async def main() -> None:
    client = get_supabase_client()
    updated = 0
    for mentor_id, fields in ENRICHMENTS.items():
        client.table("mentors").update(fields).eq("id", mentor_id).execute()
        updated += 1
        print(f"updated {mentor_id}")
    print(f"\nDone. {updated} mentors updated.")


if __name__ == "__main__":
    asyncio.run(main())

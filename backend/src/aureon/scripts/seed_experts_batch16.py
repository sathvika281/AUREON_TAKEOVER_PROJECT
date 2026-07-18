"""Connect Batch 1 — Expert Connect seed data, sixteenth (closing) wave
— crosses the 100-expert floor with a buffer. See
seed_experts_tech_and_science.py for full module conventions.

Run via: python -m aureon.scripts.seed_experts_batch16
"""

import asyncio

from aureon.domain.models.mentor import Mentor
from aureon.services.supabase.client import get_supabase_client

EXPERTS: list[dict] = [
    {
        "id": "expert_industrial_designer_noah_bergman",
        "name": "Noah Bergman, Industrial Designer",
        "role_type": "industry_professional", "field": "industrial design", "bio": "Designs consumer electronics products at a design consultancy; his first mass-manufactured product design had a significant durability flaw discovered after launch.",
        "trait_tags": ["creativity", "analytical_thinking"], "learning_style_fit": "Students who like combining creative form with the practical constraints of manufacturing.",
        "organization": "A product design consultancy", "years_experience": 9, "journey_highlights": ["His first mass-manufactured product had a significant durability flaw discovered after launch", "Later designed a product that won an international design award"],
        "discussion_topics": ["A product flaw discovered after mass production", "Industrial design as engineering plus aesthetics", "Designing for manufacturing at scale"],
        "profession": "Senior Industrial Designer", "specialization": "Consumer electronics product design", "country": "Netherlands", "city": "Eindhoven",
        "industries": ["design", "manufacturing"], "education": ["BA Industrial Design, Design Academy Eindhoven"],
        "current_role": "Senior Industrial Designer", "languages": ["Dutch", "English", "German"],
        "accepts_mentorship": True, "max_students": 2,
        "who_should_talk_to_me": ["Students who like combining creative design with real manufacturing constraints", "Students who've had a design flaw discovered after a product shipped", "Students interested in consumer product design specifically"],
        "career_ids": [],
        "career_journey": [
            {"stage": "university", "label": "BA Industrial Design", "description": "Focused his thesis on sustainable materials for consumer electronics.", "year_label": "2010-2014"},
            {"stage": "first_job", "label": "Junior industrial designer", "description": "Contributed to smaller design elements before leading his own product design.", "year_label": "2014-2017"},
            {"stage": "failure", "label": "Led design on a mass-manufactured product with a durability flaw discovered after launch", "description": "A hinge mechanism failed under real-world use conditions that hadn't been adequately stress-tested before production.", "year_label": "2017"},
            {"stage": "turning_point", "label": "Advocated for much more rigorous physical stress-testing protocols before any future production commitment", "description": "The costly recall experience became the foundation of his now-thorough design validation process.", "year_label": "2018"},
            {"stage": "current_role", "label": "Senior Industrial Designer", "description": "Later designed a product that won an international design award.", "year_label": "2020-present"},
        ],
        "day_in_the_life": "A mix of concept sketching, 3D modeling, prototype testing, and coordination with manufacturing engineers.",
        "weekly_routine": "Creative design work early in a project, increasingly technical validation and manufacturing coordination as it progresses.",
        "biggest_challenges": ["Balancing creative vision against real manufacturing cost and durability constraints", "Predicting how a design will hold up under years of real-world use"],
        "favourite_part": "Holding a finished, mass-produced version of something that started as his own sketch.",
        "biggest_misconceptions": ["That industrial design is just making products look attractive", "That a post-launch product flaw ends a designer's credibility"],
        "what_surprised_them": "How much of industrial design is engineering validation, not just aesthetic decision-making.",
        "biggest_mistake": "I approved a hinge mechanism design based on standard testing that didn't adequately simulate years of real repeated use, prioritizing the aesthetic thinness of the design over more robust engineering. The resulting durability flaw led to a costly product recall, and I now insist on much more rigorous, realistic stress-testing before any design is finalized for production.",
        "one_regret": "I regret prioritizing the design's slim aesthetic profile over the engineering team's early concerns about the hinge's durability — I should have weighted their feedback more heavily.",
        "salary_reality": "Industrial design pays well in the Netherlands' strong design and manufacturing sector, reflecting genuine technical and creative expertise.",
        "work_life_balance": "Generally steady, with real intensity before major design deadlines or manufacturing handoffs.",
        "daily_skills": ["product design", "3D modeling", "manufacturing engineering coordination"],
        "daily_tools": ["CAD design software", "3D printing and prototyping equipment"],
        "recommended_books": ["The Design of Everyday Things by Don Norman"],
        "recommended_communities": ["Dutch industrial designers association"],
        "advice_for_beginners": "Never let aesthetic preference override engineering durability concerns without rigorous real-world testing — my costly product recall came from exactly that tradeoff.",
        "advice_for_parents": "A post-launch product flaw is a real, costly professional setback, but a recoverable one that often leads directly to much stronger design discipline, as it did for his career.",
        "faqs": [{"question": "Is industrial design just about how products look?", "answer": "No — real industrial design deeply integrates manufacturing engineering, durability, and cost constraints alongside aesthetics."}],
        "projects": ["Designed a product that won an international design award"], "research": [], "certifications": [],
        "conferences": ["Dutch Design Week"], "organizations": ["Dutch industrial designers association"],
        "volunteer_work": ["Mentors design students on manufacturing-aware design practice"],
        "portfolio_links": [{"label": "Portfolio", "url": "https://example.com/noahbergman"}], "social_links": [],
    },
    {
        "id": "expert_database_administrator_yara_haddad",
        "name": "Yara Haddad, Database Administrator",
        "role_type": "industry_professional", "field": "software engineering", "bio": "Manages database infrastructure for an e-commerce platform; caused a significant data outage early in her career through an unverified production database change.",
        "trait_tags": ["analytical_thinking", "persistence"], "learning_style_fit": "Students who like precise, systems-level technical work with real operational responsibility.",
        "organization": "An e-commerce platform company", "years_experience": 8, "journey_highlights": ["Caused a significant production database outage through an unverified change", "Now leads database reliability engineering for a platform handling millions of daily transactions"],
        "discussion_topics": ["Causing a major system outage and rebuilding trust afterward", "Database administration as a specialized, high-responsibility career", "What actually happens during a major system incident"],
        "profession": "Senior Database Administrator", "specialization": "E-commerce transaction database systems", "country": "Jordan", "city": "Amman",
        "industries": ["technology", "e-commerce"], "education": ["BSc Computer Science, University of Jordan"],
        "current_role": "Lead Database Reliability Engineer", "languages": ["Arabic", "English"],
        "accepts_mentorship": True, "max_students": 2,
        "who_should_talk_to_me": ["Students who like precise, systems-level technical work", "Students who've caused a real operational incident through a mistake", "Students interested in database and infrastructure engineering specifically"],
        "career_ids": [],
        "career_journey": [
            {"stage": "university", "label": "BSc Computer Science", "description": "Developed a specific interest in database systems during a database design course.", "year_label": "2012-2016"},
            {"stage": "first_job", "label": "Junior database administrator", "description": "Managed smaller database systems under senior oversight before handling production changes independently.", "year_label": "2016-2019"},
            {"stage": "failure", "label": "Caused a significant production outage by applying an unverified database schema change directly during peak traffic hours", "description": "The e-commerce platform went partially offline for nearly two hours, a genuinely costly and public incident.", "year_label": "2019"},
            {"stage": "turning_point", "label": "Championed a mandatory staged deployment and off-peak change process for all database modifications", "description": "The new process she helped design has prevented any similar incident since.", "year_label": "2020"},
            {"stage": "current_role", "label": "Lead Database Reliability Engineer", "description": "Now leads database reliability for a platform handling millions of daily transactions.", "year_label": "2022-present"},
        ],
        "day_in_the_life": "Monitoring database performance and health, planning and reviewing schema changes, and responding to any real-time issues.",
        "weekly_routine": "Proactive monitoring and improvement work most weeks, with rigorous change review processes for any production modifications.",
        "biggest_challenges": ["The real, immediate business impact of any database reliability issue", "Balancing the need for system changes against the risk they introduce"],
        "favourite_part": "A major system change deployed flawlessly, invisible to users, exactly as it should be.",
        "biggest_misconceptions": ["That database administration is a 'behind the scenes' role with low real impact", "That causing a major incident permanently damages your standing on a team"],
        "what_surprised_them": "How much of the role is about process discipline and risk management, not just technical database knowledge.",
        "biggest_mistake": "I applied a database schema change directly to the production system during peak business hours without adequately testing it in a staging environment first, trusting my own confidence in a change I believed was low-risk. It caused a significant outage affecting real customers and revenue. I now insist on staged deployment and off-peak timing for any production database change, without exception.",
        "one_regret": "I regret the overconfidence that led me to skip proper staging validation — the outage that resulted cost far more time and trust than the shortcut I was trying to take.",
        "salary_reality": "Database administration and reliability engineering pays well in Jordan's growing tech sector, especially with the increased remote work opportunities for international companies.",
        "work_life_balance": "Generally steady, with on-call responsibilities for genuine system emergencies.",
        "daily_skills": ["database systems management", "performance optimization", "incident response"],
        "daily_tools": ["Database management systems", "monitoring and alerting tools"],
        "recommended_books": ["Designing Data-Intensive Applications by Martin Kleppmann"],
        "recommended_communities": ["Amman database engineers meetup"],
        "advice_for_beginners": "Never apply an unverified change directly to a production system, no matter how confident you feel — my costly outage came from exactly that overconfidence.",
        "advice_for_parents": "Causing a major system incident is a genuinely costly, public professional mistake, but it's also survivable and often becomes the foundation of real process improvement, as it did for her career.",
        "faqs": [{"question": "How do engineers recover trust after causing a major system outage?", "answer": "Through transparency about what happened and visible, concrete process improvements — my outage led directly to safety processes now used company-wide."}],
        "projects": ["Leads database reliability for a platform handling millions of daily transactions"], "research": [],
        "certifications": [], "conferences": [], "organizations": [],
        "volunteer_work": ["Mentors junior engineers on production change safety practices"],
        "portfolio_links": [], "social_links": [],
    },
    {
        "id": "expert_sommelier_gabriel_costa",
        "name": "Gabriel Costa, Sommelier",
        "role_type": "industry_professional", "field": "food and beverage", "bio": "Curates wine programs for a high-end restaurant group; failed the advanced sommelier certification exam twice before passing on his third attempt.",
        "trait_tags": ["persistence", "communication"], "learning_style_fit": "Students interested in a sensory, hospitality-focused career combining expertise with genuine service.",
        "organization": "A restaurant group", "years_experience": 12, "journey_highlights": ["Failed the advanced sommelier certification exam twice", "Now oversees wine programs across five restaurants"],
        "discussion_topics": ["Failing a prestigious certification exam and trying again", "Sommelier work as a genuine hospitality career", "Building expertise in a highly competitive, sensory field"],
        "profession": "Head Sommelier", "specialization": "Restaurant wine program curation", "country": "Portugal", "city": "Porto",
        "industries": ["hospitality"], "education": ["Sommelier certification program, Advanced level"],
        "current_role": "Head Sommelier, Restaurant Group", "languages": ["Portuguese", "English", "French", "Spanish"],
        "accepts_mentorship": True, "max_students": 2,
        "who_should_talk_to_me": ["Students interested in wine and hospitality as a genuine expert career", "Students who've failed a prestigious certification exam multiple times", "Students weighing sommelier work against other hospitality paths"],
        "career_ids": [],
        "career_journey": [
            {"stage": "first_job", "label": "Server, then junior sommelier at a restaurant", "description": "Developed genuine passion for wine through daily restaurant exposure.", "year_label": "2011-2014"},
            {"stage": "failure", "label": "Failed the advanced sommelier certification exam on his first attempt", "description": "The exam's rigorous blind-tasting component proved far more difficult than his restaurant experience alone had prepared him for.", "year_label": "2015"},
            {"stage": "failure", "label": "Failed again on his second attempt", "description": "Began seriously questioning whether he had the palate sensitivity the certification actually required.", "year_label": "2016"},
            {"stage": "turning_point", "label": "Restructured his study around structured, deliberate blind-tasting practice with a study group", "description": "Passed on his third attempt after a full year of much more rigorous preparation.", "year_label": "2017"},
            {"stage": "current_role", "label": "Head Sommelier, Restaurant Group", "description": "Now oversees wine programs across five restaurants.", "year_label": "2019-present"},
        ],
        "day_in_the_life": "Wine list curation, staff training, and direct guest service pairing wine recommendations with meals.",
        "weekly_routine": "Restaurant service hours combined with ongoing wine tasting and education, plus supplier relationship management.",
        "biggest_challenges": ["The genuinely demanding sensory precision required at advanced certification levels", "Balancing guest budget constraints against genuinely excellent wine recommendations"],
        "favourite_part": "A perfect wine pairing that genuinely elevates a guest's meal experience.",
        "biggest_misconceptions": ["That sommelier work is just knowing wine names and prices", "That failing a certification exam means you lack a genuinely capable palate"],
        "what_surprised_them": "How much deliberate, structured practice blind-tasting requires — natural palate sensitivity alone isn't sufficient.",
        "biggest_mistake": "I approached my first two certification attempts by broadly tasting many wines casually, rather than following the structured, deliberate blind-tasting methodology the exam actually required. Both attempts failed on the same tasting component. Once I adopted a genuinely systematic practice approach with a study group, my third attempt succeeded.",
        "one_regret": "I regret not seeking out a structured study group before my first two attempts — casual tasting experience, however extensive, wasn't the right preparation for what the exam actually tested.",
        "salary_reality": "Head sommelier roles at high-end restaurants in Portugal can be genuinely well-compensated, though the certification path itself required real personal financial investment.",
        "work_life_balance": "Evening and weekend hours are standard given restaurant service schedules, a real tradeoff of the hospitality industry generally.",
        "daily_skills": ["wine tasting and evaluation", "wine list curation", "guest service"],
        "daily_tools": ["Wine cellar management systems", "tasting evaluation frameworks"],
        "recommended_books": ["The World Atlas of Wine by Hugh Johnson and Jancis Robinson"],
        "recommended_communities": ["Portuguese sommelier association"],
        "advice_for_beginners": "Practice blind-tasting with deliberate, structured methodology and a study group, not just casual wine exposure — my two failures came from skipping exactly this discipline.",
        "advice_for_parents": "Repeated failure on a prestigious certification exam like advanced sommelier level is genuinely common — persistence and a better study method, not raw natural talent alone, is usually what makes the difference.",
        "faqs": [{"question": "Is it common to fail advanced sommelier certification exams?", "answer": "Yes, pass rates at advanced levels are notably low — multiple attempts are common even among eventually highly successful sommeliers."}],
        "projects": ["Oversees wine programs across five restaurants"], "research": [], "certifications": ["Advanced Sommelier Certification"],
        "conferences": [], "organizations": ["Portuguese sommelier association"],
        "volunteer_work": ["Runs a study group for sommelier certification candidates"],
        "portfolio_links": [], "social_links": [],
    },
]


async def seed() -> None:
    client = get_supabase_client()
    experts = [Mentor.model_validate(e) for e in EXPERTS]

    def _upsert() -> None:
        client.table("mentors").upsert([e.model_dump(mode="json") for e in experts]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(experts)} experts (batch16, closing wave).")


if __name__ == "__main__":
    asyncio.run(seed())

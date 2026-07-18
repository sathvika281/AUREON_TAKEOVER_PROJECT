"""One-time enrichment script for the Explore Polish Batch — backfills
the 4 new embedded Institution fields (hostels/exchange_programs/
campus_facilities/student_reviews) onto all 9 institutions via targeted
`.update()`, AND backfills the 8 non-NIAT institutions' V13 child
tables (innovation_centers/faculty_highlights/student_ambassadors/
student_projects/internship_opportunities) — which today only exist for
`inst_niat` — up to the same real depth, via `.upsert()` of new rows
(safe here since each child row has its own unique id and upserting
never touches other institutions' rows).

Run via: python -m aureon.scripts.enrich_institutions

Idempotent: safe to re-run.
"""

import asyncio

from aureon.domain.models.institution import (
    FacultyHighlight,
    InnovationCenter,
    InstitutionReview,
    InternshipOpportunity,
    StudentAmbassador,
    StudentProject,
)
from aureon.services.supabase.client import get_supabase_client

# Main-row fields — id -> the 4 new Institution fields.
INSTITUTION_FIELDS: dict[str, dict] = {
    "inst_aurora_institute": {
        "hostels": ["Kendall Hall (first-year, all singles)", "Innovation House (upperclass, project-team suites)", "Graduate Commons (grad-student apartments)"],
        "exchange_programs": ["ETH Zurich engineering exchange (one semester)", "National University of Singapore research exchange", "Technical University of Munich robotics exchange"],
        "campus_facilities": ["24/7 makerspace with 3D printing and CNC", "High-performance computing cluster access for undergrads", "Robotics competition arena", "Startup incubator co-working space"],
        "student_reviews": [
            {"role_label": "Third-year, Materials Science", "quote": "The lab access from day one is real — I was running my own experiments in a materials lab by my second semester.", "sentiment": "positive"},
            {"role_label": "Graduate Student, Robotics", "quote": "The pace is genuinely intense; you need to be comfortable being self-directed almost immediately.", "sentiment": "mixed"},
        ],
    },
    "inst_meridian_university": {
        "hostels": ["Thames View Halls (first-year)", "Bloomsbury Residences (upperclass, shared flats)", "Postgraduate Court"],
        "exchange_programs": ["Sciences Po Paris policy exchange", "University of Toronto exchange", "Sorbonne semester exchange (humanities)"],
        "campus_facilities": ["Historic debate chamber (used by the Debate Society)", "Independent student film-production studio", "Policy analytics computer lab", "Central London library access consortium"],
        "student_reviews": [
            {"role_label": "Second-year, Politics, Philosophy and Economics", "quote": "The essay-heavy, tutorial-based teaching pushed my writing and argumentation further than I expected.", "sentiment": "positive"},
            {"role_label": "Master's Student, Public Health Policy", "quote": "It's a traditional structure — if you want a lot of hands-on project work rather than reading and discussion, it can feel slower-paced.", "sentiment": "mixed"},
        ],
    },
    "inst_kyoto_innovation_university": {
        "hostels": ["Sakura International Dormitory (mixed domestic/international)", "Graduate Research Housing"],
        "exchange_programs": ["RWTH Aachen robotics exchange", "Nanyang Technological University engineering exchange"],
        "campus_facilities": ["Precision manufacturing workshop", "Robotics testing arena shared with regional industry partners", "Traditional craft studio (woodworking, ceramics) for the Craft-Technology Society"],
        "student_reviews": [
            {"role_label": "Doctoral Candidate, Robotics", "quote": "The mentorship continuity here is unusual — I've worked with the same faculty advisor closely for three years.", "sentiment": "positive"},
            {"role_label": "Third-year, Mechanical and Robotics Engineering", "quote": "It's a demanding, precision-focused environment; students who prefer a faster or looser pace may find it rigid.", "sentiment": "mixed"},
        ],
    },
    "inst_iias_bengaluru": {
        "hostels": ["North Campus Hostel Block (first/second-year)", "Research Scholars' Residence"],
        "exchange_programs": ["National University of Singapore computational biology exchange", "University of Toronto exchange (engineering)"],
        "campus_facilities": ["Genomics computing cluster", "Astrophysics observatory access", "Entrepreneurship Cell co-working and pitch space"],
        "student_reviews": [
            {"role_label": "Final-year, Computer Science and Engineering", "quote": "Being inside India's biggest tech hub means real internship access is genuinely easy to find, not just theoretical.", "sentiment": "positive"},
            {"role_label": "Master's Student, Computational Biology", "quote": "The exam-and-project workload is heavy — you need strong time-management to keep up.", "sentiment": "mixed"},
        ],
    },
    "inst_nordholm_technical_university": {
        "hostels": ["Norrland Student Village", "Green Campus Apartments (energy-efficient student housing)"],
        "exchange_programs": ["TU Delft sustainable engineering exchange", "ETH Zurich clean-energy exchange"],
        "campus_facilities": ["Renewable-energy systems testing lab", "Climate materials pilot facility", "Bike-first campus with EV charging throughout"],
        "student_reviews": [
            {"role_label": "Second-year, Environmental Engineering", "quote": "Nearly every major project is done in a team with real industry sponsors — it feels closer to consulting work than coursework.", "sentiment": "positive"},
            {"role_label": "Master's Student, Sustainable Energy Engineering", "quote": "Group-heavy assessment means your grade depends a lot on teammates — not ideal if you prefer working solo.", "sentiment": "mixed"},
        ],
    },
    "inst_cape_town_design_school": {
        "hostels": ["Waterfront Student Residence", "Design Quarter Lofts (upperclass, studio-adjacent)"],
        "exchange_programs": ["Parsons School of Design exchange", "Politecnico di Milano design exchange"],
        "campus_facilities": ["Open-plan critique studios", "Print and physical-prototyping workshop", "Student film-production suite"],
        "student_reviews": [
            {"role_label": "Third-year, User Experience Design", "quote": "The critique culture is intense but it made my portfolio genuinely strong by graduation.", "sentiment": "positive"},
            {"role_label": "Master's Student, Design Innovation", "quote": "It's very portfolio- and studio-driven — if you want more traditional theory-heavy classes, this isn't that.", "sentiment": "mixed"},
        ],
    },
    "inst_andes_global_university": {
        "hostels": ["Residencia Los Andes (first-year)", "Casa Santiago (shared apartments, upperclass)"],
        "exchange_programs": ["Universidad Politécnica de Madrid engineering exchange", "University of São Paulo regional exchange"],
        "campus_facilities": ["Renewable resources and mining sustainability lab", "Public health community-outreach clinic space", "Regional innovation co-working center"],
        "student_reviews": [
            {"role_label": "Final-year, Environmental and Mining Engineering", "quote": "The regional industry ties are real — several of my classmates had internships lined up by third year through direct faculty connections.", "sentiment": "positive"},
            {"role_label": "Second-year, Public Health", "quote": "Research opportunities really pick up in later years — the first two years are fairly structured coursework.", "sentiment": "mixed"},
        ],
    },
    "inst_pacific_rim_media_arts": {
        "hostels": ["Harbourside Student Apartments", "Media Quarter Residences (studio-adjacent)"],
        "exchange_programs": ["University of Southern California (film) exchange", "Vancouver Film School partnership program"],
        "campus_facilities": ["Sound stage and post-production suite", "Game development lab with motion-capture rig", "Independent screening theater"],
        "student_reviews": [
            {"role_label": "Third-year, Game Design and Development", "quote": "Regular industry-judged showcases mean you're building a real portfolio the whole way through, not just at the end.", "sentiment": "positive"},
            {"role_label": "Final-year, Documentary Filmmaking", "quote": "The deadline-driven production schedule is demanding — burnout is a real risk if you don't pace yourself.", "sentiment": "mixed"},
        ],
    },
    "inst_niat": {
        "hostels": ["NIAT Residential Cohort Housing (Hyderabad campus)"],
        "exchange_programs": ["Short-term industry immersion exchanges with partner-company offices in other cities"],
        "campus_facilities": ["24/7 build lab with pair-programming stations", "Mentor office-hours lounge", "Demo Day presentation hall"],
        "student_reviews": [
            {"role_label": "Full-Stack Track, Cohort 3", "quote": "This felt less like a classroom and more like a real engineering team from week one.", "sentiment": "positive"},
            {"role_label": "AI/ML Track, Cohort 2", "quote": "The pace is fast and outcome-driven — if you need a slower, more traditional structure, it can feel like a lot at once.", "sentiment": "mixed"},
        ],
    },
}

# New V13-style child rows for the 8 non-NIAT institutions, keyed by
# the same {inst_id}_{table}_{i} id convention seed_mentors_institutions.py
# already uses for inst_niat.
CHILD_ENRICHMENTS: dict[str, dict] = {
    "inst_aurora_institute": {
        "innovation_centers": [
            {"name": "Aurora Venture Studio", "focus_area": "deep-tech startup incubation", "description": "Helps student and alumni teams turn lab research into fundable startups."},
        ],
        "faculty_highlights": [
            {"name": "Director, Autonomous Systems Lab", "title": "Professor of Robotics", "expertise_area": "robotic manipulation and control", "bio": "Leads a lab building next-generation robotic manipulation systems with undergraduates joining research within their first year."},
        ],
        "student_ambassadors": [
            {"student_label": "Third-year, Materials Science and Engineering", "program": "BSc Materials Science and Engineering", "message": "I joined a battery-materials research lab in my second semester and haven't left since."},
        ],
        "student_projects": [
            {"student_label": "Robotics Master's student team", "project_title": "Adaptive Grasping Robotic Arm", "description": "A robotic arm prototype that adjusts grip strategy in real time based on object shape, built as a lab research extension.", "skills_used": ["ROS", "Python", "Computer Vision"]},
        ],
        "internship_opportunities": [
            {"title": "Autonomous Systems Research Internship", "field": "robotics", "description": "A paid summer research internship embedded directly in the Autonomous Systems Lab."},
        ],
    },
    "inst_meridian_university": {
        "innovation_centers": [
            {"name": "Meridian Policy Innovation Lab", "focus_area": "public policy prototyping", "description": "Supports student-led policy research translated into real briefs for London policymakers."},
        ],
        "faculty_highlights": [
            {"name": "Head, Public Policy Analytics Lab", "title": "Professor of Health Policy", "expertise_area": "health policy analytics", "bio": "Directs research analyzing health policy outcomes using large public datasets, with students contributing to live analyses."},
        ],
        "student_ambassadors": [
            {"student_label": "Final-year, Politics, Philosophy and Economics", "program": "BA Politics, Philosophy and Economics", "message": "The Debate Society pushed my public-speaking skills more than any single class did."},
        ],
        "student_projects": [
            {"student_label": "Public Health Policy Master's student team", "project_title": "NHS Waiting-Time Policy Brief", "description": "A data-driven policy brief analyzing regional NHS waiting-time disparities, presented to a real policy audience.", "skills_used": ["R", "Policy Analysis", "Data Visualization"]},
        ],
        "internship_opportunities": [
            {"title": "Policy Research Internship", "field": "public policy", "description": "A structured internship with London-based policy think tanks partnered with the university."},
        ],
    },
    "inst_kyoto_innovation_university": {
        "innovation_centers": [
            {"name": "Kyoto Robotics Innovation Center", "focus_area": "precision manufacturing startups", "description": "Connects student robotics research to regional manufacturing partners for pilot deployment."},
        ],
        "faculty_highlights": [
            {"name": "Director, Precision Robotics Lab", "title": "Professor of Mechanical Engineering", "expertise_area": "industrial robotics", "bio": "Leads long-term research on precision manipulation systems with close, sustained student mentorship."},
        ],
        "student_ambassadors": [
            {"student_label": "PhD Candidate, Robotics", "program": "PhD Robotics", "message": "The mentorship continuity here means I've worked with the same advisor on one research thread for three years straight."},
        ],
        "student_projects": [
            {"student_label": "Mechanical and Robotics Engineering student team", "project_title": "Safe Human-Robot Handoff System", "description": "A collaborative robot arm designed to safely hand off small parts to a human worker on a mock assembly line.", "skills_used": ["Robot Operating System (ROS)", "Sensor Fusion", "CAD"]},
        ],
        "internship_opportunities": [
            {"title": "Precision Manufacturing Internship", "field": "robotics", "description": "An internship with regional manufacturing partners applying lab robotics research on the factory floor."},
        ],
    },
    "inst_iias_bengaluru": {
        "innovation_centers": [
            {"name": "IIAS Deep-Tech Incubator", "focus_area": "biotech and AI startups", "description": "Supports student teams building genomics and AI-driven startups, with connections to Bengaluru's dense R&D ecosystem."},
        ],
        "faculty_highlights": [
            {"name": "Director, Genomics and Computational Biology Lab", "title": "Professor of Computational Biology", "expertise_area": "computational genomics", "bio": "Leads applied machine-learning research on genomic data, with graduate students co-authoring published findings."},
        ],
        "student_ambassadors": [
            {"student_label": "Final-year, Computer Science and Engineering", "program": "BTech Computer Science and Engineering", "message": "Being minutes from major tech R&D centers made finding a strong internship straightforward."},
        ],
        "student_projects": [
            {"student_label": "Computational Biology Master's student team", "project_title": "Variant-Calling Pipeline for Rare Disease Research", "description": "A genomic variant-calling pipeline built and validated on public rare-disease datasets.", "skills_used": ["Python", "Bioinformatics", "High-Performance Computing"]},
        ],
        "internship_opportunities": [
            {"title": "Computational Biology Research Internship", "field": "biotechnology", "description": "A research internship embedded in the Genomics and Computational Biology Lab."},
        ],
    },
    "inst_nordholm_technical_university": {
        "innovation_centers": [
            {"name": "Nordholm Climate-Tech Accelerator", "focus_area": "clean-energy startups", "description": "Supports student ventures in renewable energy and sustainable materials, backed by national innovation funding."},
        ],
        "faculty_highlights": [
            {"name": "Director, Sustainable Energy Systems Lab", "title": "Professor of Energy Engineering", "expertise_area": "renewable grid integration", "bio": "Leads research on grid-scale renewable energy integration, with students contributing to industry-sponsored capstones."},
        ],
        "student_ambassadors": [
            {"student_label": "Master's Student, Sustainable Energy Engineering", "program": "MSc Sustainable Energy Engineering", "message": "Nearly every major project I've done has had a real industry sponsor attached to it."},
        ],
        "student_projects": [
            {"student_label": "Environmental Engineering student team", "project_title": "Community Microgrid Feasibility Study", "description": "A feasibility study and simulation for a small-scale renewable microgrid, developed with a regional energy partner.", "skills_used": ["MATLAB", "Energy Systems Modeling", "Sustainability Analysis"]},
        ],
        "internship_opportunities": [
            {"title": "Clean Energy Engineering Internship", "field": "renewable energy", "description": "An internship with Nordic energy companies partnered with the Sustainable Energy Systems Lab."},
        ],
    },
    "inst_cape_town_design_school": {
        "innovation_centers": [
            {"name": "Cape Town Creative-Tech Studio", "focus_area": "design-technology startups", "description": "Supports student design ventures with regional creative-industry mentorship."},
        ],
        "faculty_highlights": [
            {"name": "Director, Human-Centered Design Lab", "title": "Professor of User Experience", "expertise_area": "UX research methods", "bio": "Leads studies on user behavior across digital product design, with students running real usability studies each term."},
        ],
        "student_ambassadors": [
            {"student_label": "Third-year, User Experience Design", "program": "BA User Experience Design", "message": "The critique-driven studio culture pushed my portfolio further than I expected in just three years."},
        ],
        "student_projects": [
            {"student_label": "Design Collective student team", "project_title": "Local Business Wayfinding App Redesign", "description": "A redesigned wayfinding app for a local Cape Town business district, built with real user research.", "skills_used": ["Figma", "User Research", "Prototyping"]},
        ],
        "internship_opportunities": [
            {"title": "UX Design Internship", "field": "design", "description": "An internship with regional design studios and consumer brands partnered with the school."},
        ],
    },
    "inst_andes_global_university": {
        "innovation_centers": [
            {"name": "Andes Regional Innovation Center", "focus_area": "sustainability and public-health ventures", "description": "Supports student ventures addressing regional sustainability and health challenges."},
        ],
        "faculty_highlights": [
            {"name": "Director, Renewable Resources Lab", "title": "Professor of Environmental Engineering", "expertise_area": "sustainable resource extraction", "bio": "Leads research into sustainable practices for resource-intensive regional industries like mining and agriculture."},
        ],
        "student_ambassadors": [
            {"student_label": "Final-year, Environmental and Mining Engineering", "program": "BEng Environmental and Mining Engineering", "message": "Faculty connections here led directly to my internship placement in third year."},
        ],
        "student_projects": [
            {"student_label": "Public Health Student Association team", "project_title": "Community Water Quality Monitoring Program", "description": "A student-run water quality monitoring initiative for underserved communities near Santiago.", "skills_used": ["Public Health Research", "Data Collection", "Community Outreach"]},
        ],
        "internship_opportunities": [
            {"title": "Environmental Sustainability Internship", "field": "environmental engineering", "description": "An internship with regional mining and agriculture partners focused on sustainability practices."},
        ],
    },
    "inst_pacific_rim_media_arts": {
        "innovation_centers": [
            {"name": "Pacific Rim Media Innovation Hub", "focus_area": "game and interactive media startups", "description": "Supports student teams turning game jam prototypes into shippable indie titles."},
        ],
        "faculty_highlights": [
            {"name": "Director, Interactive Media Lab", "title": "Professor of Game Design", "expertise_area": "interactive storytelling", "bio": "Leads research into emerging interactive storytelling and game design techniques, with students shipping playable prototypes each term."},
        ],
        "student_ambassadors": [
            {"student_label": "Third-year, Game Design and Development", "program": "BA Game Design and Development", "message": "The regular industry-judged showcases meant I graduated with a portfolio, not just a transcript."},
        ],
        "student_projects": [
            {"student_label": "Independent Game Developers Guild team", "project_title": "Tidewatch (2D narrative puzzle game)", "description": "A short narrative puzzle game built during a campus game jam and later expanded into a full student project.", "skills_used": ["Unity", "Game Design", "Narrative Writing"]},
        ],
        "internship_opportunities": [
            {"title": "Game Development Internship", "field": "game development", "description": "An internship with regional game studios partnered with the Interactive Media Lab."},
        ],
    },
}


async def enrich() -> None:
    client = get_supabase_client()

    for institution_id, fields in INSTITUTION_FIELDS.items():
        InstitutionReview_list = [InstitutionReview.model_validate(r) for r in fields["student_reviews"]]
        payload = {**fields, "student_reviews": [r.model_dump(mode="json") for r in InstitutionReview_list]}

        def _update(iid: str = institution_id, data: dict = payload) -> None:
            client.table("institutions").update(data).eq("id", iid).execute()

        await asyncio.to_thread(_update)

    innovation_centers: list[InnovationCenter] = []
    faculty_highlights: list[FacultyHighlight] = []
    student_ambassadors: list[StudentAmbassador] = []
    student_projects: list[StudentProject] = []
    internship_opportunities: list[InternshipOpportunity] = []

    for inst_id, entry in CHILD_ENRICHMENTS.items():
        for i, center in enumerate(entry["innovation_centers"]):
            innovation_centers.append(InnovationCenter(id=f"{inst_id}_innovation_{i}", institution_id=inst_id, **center))
        for i, faculty in enumerate(entry["faculty_highlights"]):
            faculty_highlights.append(FacultyHighlight(id=f"{inst_id}_faculty_{i}", institution_id=inst_id, **faculty))
        for i, ambassador in enumerate(entry["student_ambassadors"]):
            student_ambassadors.append(StudentAmbassador(id=f"{inst_id}_ambassador_{i}", institution_id=inst_id, **ambassador))
        for i, project in enumerate(entry["student_projects"]):
            student_projects.append(StudentProject(id=f"{inst_id}_project_{i}", institution_id=inst_id, **project))
        for i, internship in enumerate(entry["internship_opportunities"]):
            internship_opportunities.append(InternshipOpportunity(id=f"{inst_id}_internship_{i}", institution_id=inst_id, **internship))

    def _upsert_children() -> None:
        client.table("innovation_centers").upsert([c.model_dump(mode="json") for c in innovation_centers]).execute()
        client.table("faculty_highlights").upsert([f.model_dump(mode="json") for f in faculty_highlights]).execute()
        client.table("student_ambassadors").upsert([a.model_dump(mode="json") for a in student_ambassadors]).execute()
        client.table("student_projects").upsert([p.model_dump(mode="json") for p in student_projects]).execute()
        client.table("internship_opportunities").upsert([i.model_dump(mode="json") for i in internship_opportunities]).execute()

    await asyncio.to_thread(_upsert_children)

    print(
        f"Updated {len(INSTITUTION_FIELDS)} institutions' new fields. "
        f"Backfilled {len(innovation_centers)} innovation centers, {len(faculty_highlights)} faculty highlights, "
        f"{len(student_ambassadors)} student ambassadors, {len(student_projects)} student projects, "
        f"{len(internship_opportunities)} internship opportunities across {len(CHILD_ENRICHMENTS)} institutions."
    )


if __name__ == "__main__":
    asyncio.run(enrich())

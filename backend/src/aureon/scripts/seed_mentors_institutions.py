"""One-time seed script for Phase 3's Mentor and Institution Knowledge
Bases, extended in V13 (Career Exploration Ecosystem) with Expert
Connect's richer mentor fields, NIAT as the first collaborating
educational organization, and the shared Experience Events table.

Run via: python -m aureon.scripts.seed_mentors_institutions

A modest, honestly-scoped starting set (~15 mentors across the requested
role types, ~8 institutions each with a few research labs/student
organizations/academic programs) — real structured content, not prompt
text, proving the matching architecture. Expandable over time; not
presented as full coverage. Mentor/ambassador/student-project names are
illustrative composite personas (labeled by role/field), not fabricated
real, contactable individuals — same honesty convention as Phase 2's
Human Stories. Idempotent: upserts by id, safe to re-run.
"""

import asyncio

from aureon.domain.models.career_event import CareerEvent
from aureon.domain.models.entrance_exam import EntranceExam
from aureon.domain.models.institution import (
    AcademicProgram,
    FacultyHighlight,
    InnovationCenter,
    Institution,
    InternshipOpportunity,
    ResearchLab,
    StudentAmbassador,
    StudentOrganization,
    StudentProject,
)
from aureon.domain.models.mentor import Mentor
from aureon.services.supabase.client import get_supabase_client

MENTORS: list[dict] = [
    {
        "id": "mentor_elena_vasquez",
        "name": "Dr. Elena Vasquez, Materials Science Professor",
        "role_type": "professor",
        "field": "materials science",
        "bio": "Runs a university lab studying next-generation battery materials; known for taking on students with more curiosity than formal credentials.",
        "trait_tags": ["analytical_thinking", "curiosity"],
        "learning_style_fit": "Hands-on experimenters who learn by iterating in a lab rather than from lectures alone.",
        "organization": "Aurora Institute of Technology",
        "years_experience": 14,
        "journey_highlights": ["Led a battery-materials lab from 2 to 20 researchers", "Published foundational work on solid-state electrolytes"],
        "discussion_topics": ["Choosing a PhD lab", "Materials research careers", "Balancing lab work with coursework"],
    },
    {
        "id": "mentor_priya_nair",
        "name": "Dr. Priya Nair, Computational Biology Researcher",
        "role_type": "researcher",
        "field": "computational biology",
        "bio": "Works at the intersection of genomics and machine learning, mentoring students moving between biology and computer science.",
        "trait_tags": ["curiosity", "analytical_thinking"],
        "learning_style_fit": "Students comfortable holding two disciplines at once rather than specializing early.",
        "organization": "Indian Institute of Advanced Sciences",
        "years_experience": 9,
        "journey_highlights": ["Moved from wet-lab biology into computational genomics mid-PhD", "Built an open-source variant-calling pipeline used across three labs"],
        "discussion_topics": ["Switching disciplines mid-career", "Genomics + machine learning", "Reading papers outside your field"],
    },
    {
        "id": "mentor_marcus_chen",
        "name": "Marcus Chen, Senior Software Engineer",
        "role_type": "industry_professional",
        "field": "software engineering",
        "bio": "A decade in industry building backend systems at scale; mentors students weighing engineering against research paths.",
        "trait_tags": ["analytical_thinking", "learning_style"],
        "learning_style_fit": "Learners who want concrete, practical feedback tied to real production systems.",
        "organization": "A logistics-technology company",
        "years_experience": 11,
        "journey_highlights": ["Scaled a backend system from thousands to millions of daily requests", "Moved from individual contributor to tech lead"],
        "discussion_topics": ["Industry vs. research paths", "System design interviews", "Growing from junior to senior engineer"],
    },
    {
        "id": "mentor_aisha_osei",
        "name": "Aisha Osei, UX Design Lead",
        "role_type": "industry_professional",
        "field": "product design",
        "bio": "Leads design at a mid-size product company, with a background bridging psychology and visual design.",
        "trait_tags": ["creativity", "communication"],
        "learning_style_fit": "Students who learn best by watching real users interact with what they build.",
        "organization": "A consumer product company",
        "years_experience": 10,
        "journey_highlights": ["Transitioned from psychology research into product design", "Built and led a 6-person design team"],
        "discussion_topics": ["Breaking into UX design", "Building a design portfolio", "Design research methods"],
    },
    {
        "id": "mentor_daniel_kim",
        "name": "Daniel Kim, Climate Tech Startup Founder",
        "role_type": "founder",
        "field": "climate technology",
        "bio": "Founded a climate-focused hardware startup after years in corporate energy; mentors aspiring founders on the realities of early-stage building.",
        "trait_tags": ["leadership", "motivation"],
        "learning_style_fit": "Students energized by ambiguity and building something from nothing.",
        "organization": "A climate-hardware startup (founder)",
        "years_experience": 13,
        "journey_highlights": ["Left a corporate energy role to found a hardware startup", "Raised seed funding for a first-of-its-kind climate product"],
        "discussion_topics": ["Starting a hardware company", "Fundraising realities", "Corporate-to-founder transitions"],
    },
    {
        "id": "mentor_sofia_marino",
        "name": "Sofia Marino, Independent Documentary Filmmaker",
        "role_type": "creator",
        "field": "documentary film",
        "bio": "Self-funds and directs documentaries on social issues; mentors students exploring creative, non-traditional career paths.",
        "trait_tags": ["creativity", "values"],
        "learning_style_fit": "Students who want to see how a creative career actually sustains itself financially, not just artistically.",
        "organization": "Independent (self-funded)",
        "years_experience": 12,
        "journey_highlights": ["Self-funded and directed three feature documentaries", "Built a sustainable freelance production practice"],
        "discussion_topics": ["Funding independent creative work", "Documentary storytelling", "Sustaining a freelance career"],
    },
    {
        "id": "mentor_rajesh_gupta",
        "name": "Dr. Rajesh Gupta, Neuroscience Professor",
        "role_type": "professor",
        "field": "neuroscience",
        "bio": "Studies decision-making in the brain; enjoys mentoring students who ask why more than what.",
        "trait_tags": ["curiosity", "analytical_thinking"],
        "learning_style_fit": "Students drawn to slow, careful inquiry over quick answers.",
        "organization": "Meridian University",
        "years_experience": 18,
        "journey_highlights": ["Runs a decision-neuroscience lab for over a decade", "Mentored students into both academic and clinical paths"],
        "discussion_topics": ["Academic research careers", "Applying to neuroscience PhD programs", "Reading primary literature"],
    },
    {
        "id": "mentor_naomi_osei_bonsu",
        "name": "Dr. Naomi Osei-Bonsu, Public Health Researcher",
        "role_type": "researcher",
        "field": "public health",
        "bio": "Researches health policy in low-resource settings; mentors students interested in impact-driven, evidence-based careers.",
        "trait_tags": ["values", "communication"],
        "learning_style_fit": "Students who want their work to matter to real communities, not just publish well.",
        "organization": "Andes Global University",
        "years_experience": 10,
        "journey_highlights": ["Led field research programs across multiple low-resource settings", "Shaped regional health policy through published research"],
        "discussion_topics": ["Impact-driven research careers", "Public health fieldwork", "Evidence-based policy work"],
    },
    {
        "id": "mentor_liam_oconnor",
        "name": "Liam O'Connor, Data Science Manager",
        "role_type": "industry_professional",
        "field": "data science",
        "bio": "Manages a data science team at a logistics company; mentors students on translating analytical skill into business impact.",
        "trait_tags": ["analytical_thinking", "leadership"],
        "learning_style_fit": "Students who want to see how technical analysis connects to real decisions.",
        "organization": "A logistics company",
        "years_experience": 9,
        "journey_highlights": ["Moved from individual analyst to managing a data science team", "Built forecasting models now used company-wide"],
        "discussion_topics": ["Breaking into data science", "Analyst to manager transition", "Communicating analysis to non-technical stakeholders"],
    },
    {
        "id": "mentor_fatima_al_sayed",
        "name": "Fatima Al-Sayed, EdTech Founder",
        "role_type": "founder",
        "field": "education technology",
        "bio": "Built an EdTech company after teaching for several years; mentors students combining a specific domain passion with entrepreneurship.",
        "trait_tags": ["motivation", "creativity"],
        "learning_style_fit": "Students who learn by launching small experiments rather than planning extensively first.",
        "organization": "An education-technology company (founder)",
        "years_experience": 11,
        "journey_highlights": ["Taught for several years before founding an EdTech company", "Grew the company from a classroom pilot to a full product"],
        "discussion_topics": ["Teaching-to-founder transitions", "Validating an EdTech idea", "Early-stage product experiments"],
    },
    {
        "id": "mentor_chris_bello",
        "name": "Chris Bello, Independent Game Developer",
        "role_type": "creator",
        "field": "game development",
        "bio": "Builds and ships small independent games solo; mentors students exploring creative-technical hybrid careers.",
        "trait_tags": ["creativity", "learning_style"],
        "learning_style_fit": "Self-directed learners who prefer building complete small projects over structured courses.",
        "organization": "Independent (solo developer)",
        "years_experience": 8,
        "journey_highlights": ["Shipped multiple solo-developed indie games", "Built a sustainable practice without a publisher"],
        "discussion_topics": ["Solo game development", "Shipping small complete projects", "Creative-technical hybrid careers"],
    },
    {
        "id": "mentor_wei_zhang",
        "name": "Dr. Wei Zhang, Robotics Professor",
        "role_type": "professor",
        "field": "robotics",
        "bio": "Leads a robotics lab focused on manipulation and control; mentors students weighing hardware versus software-only paths.",
        "trait_tags": ["analytical_thinking", "curiosity"],
        "learning_style_fit": "Students who enjoy working where physical constraints meet algorithms.",
        "organization": "Kyoto Innovation University",
        "years_experience": 16,
        "journey_highlights": ["Leads a manipulation-and-control robotics lab", "Mentored students into both hardware and software robotics careers"],
        "discussion_topics": ["Hardware vs. software robotics paths", "Robotics research labs", "Manipulation and control fundamentals"],
    },
    {
        "id": "mentor_amara_chukwu",
        "name": "Dr. Amara Chukwu, Astrophysics Researcher",
        "role_type": "researcher",
        "field": "astrophysics",
        "bio": "Studies exoplanet formation; mentors students drawn to long-horizon, curiosity-driven basic research.",
        "trait_tags": ["curiosity", "analytical_thinking"],
        "learning_style_fit": "Students comfortable with research that may not show clear results for years.",
        "organization": "Indian Institute of Advanced Sciences",
        "years_experience": 10,
        "journey_highlights": ["Studies exoplanet formation using observational data", "Mentored students through long-horizon basic-research projects"],
        "discussion_topics": ["Long-horizon basic research", "Astrophysics career paths", "Handling uncertainty in research"],
    },
    {
        "id": "mentor_isabella_rossi",
        "name": "Isabella Rossi, Nonprofit Program Director",
        "role_type": "industry_professional",
        "field": "international development",
        "bio": "Runs field programs for an international NGO; mentors students weighing mission-driven work against traditional career tracks.",
        "trait_tags": ["values", "leadership"],
        "learning_style_fit": "Students who want to test their values against real operational constraints.",
        "organization": "An international NGO",
        "years_experience": 12,
        "journey_highlights": ["Ran field programs across multiple countries", "Moved from field coordinator to program director"],
        "discussion_topics": ["Mission-driven career paths", "Nonprofit vs. traditional career tracks", "Field program realities"],
    },
    {
        "id": "mentor_jordan_park",
        "name": "Jordan Park, Freelance Writer and Content Creator",
        "role_type": "creator",
        "field": "writing",
        "bio": "Built a full-time freelance writing and content career after leaving a corporate job; mentors students exploring independent creative work.",
        "trait_tags": ["creativity", "communication"],
        "learning_style_fit": "Students who want an honest look at the instability and freedom of independent creative work.",
        "organization": "Independent (freelance)",
        "years_experience": 7,
        "journey_highlights": ["Left a corporate job to freelance full-time", "Built a sustainable independent writing practice"],
        "discussion_topics": ["Freelance career realities", "Corporate-to-independent transitions", "Building a writing practice"],
    },
]

INSTITUTIONS: list[dict] = [
    {
        "id": "inst_aurora_institute",
        "name": "Aurora Institute of Technology",
        "country": "United States",
        "city": "Cambridge",
        "research_culture": "Deeply research-intensive, with undergraduates commonly joining active labs within their first year.",
        "innovation_ecosystem": "Dense startup and venture activity immediately surrounding campus, with strong founder alumni networks.",
        "industry_collaboration": "Extensive sponsored research partnerships with major technology and hardware companies.",
        "placements": "Strong placement into both research PhD programs and technology industry roles.",
        "learning_environment": "Fast-paced, project-heavy, with high expectations for independent initiative.",
        "trait_tags": ["analytical_thinking", "curiosity"],
        "campus_life_and_culture": "A tight-knit, project-driven community where late-night lab sessions and student-run hackathons are as much a part of campus life as classes themselves.",
        "fees_summary": "Tuition is on the higher end for private research universities; substantial need-based and merit aid is typically available.",
        "scholarships_summary": "Offers its own need-based and merit scholarships; students are also encouraged to pursue external scholarships and research fellowships alongside these.",
        "labs": [
            {"name": "Adaptive Materials Lab", "focus_area": "battery and materials research", "description": "Studies next-generation energy storage materials."},
            {"name": "Autonomous Systems Lab", "focus_area": "robotics", "description": "Builds robotic manipulation and control systems."},
        ],
        "orgs": [
            {"name": "Student Robotics Club", "focus_area": "robotics competitions", "description": "Designs and builds competition robots year-round."},
        ],
        "programs": [
            {"name": "BSc Materials Science and Engineering", "degree_type": "Bachelor's", "field": "materials science", "description": "Core materials science with a strong computational modeling component."},
            {"name": "MSc Robotics", "degree_type": "Master's", "field": "robotics", "description": "Combines mechanical design, controls, and machine learning."},
        ],
    },
    {
        "id": "inst_meridian_university",
        "name": "Meridian University",
        "country": "United Kingdom",
        "city": "London",
        "research_culture": "Broad, cross-disciplinary research culture spanning humanities, sciences, and professional programs.",
        "innovation_ecosystem": "Strong ties to London's finance, media, and policy sectors.",
        "industry_collaboration": "Frequent guest lectures and internship pipelines with major London employers.",
        "placements": "Diverse placement outcomes across finance, consulting, media, and public policy.",
        "learning_environment": "Traditional lecture/tutorial structure with strong emphasis on independent essay-based work.",
        "trait_tags": ["communication", "analytical_thinking"],
        "labs": [
            {"name": "Public Policy Analytics Lab", "focus_area": "health policy research", "description": "Analyzes health policy outcomes using large public datasets."},
        ],
        "orgs": [
            {"name": "Debate Society", "focus_area": "public speaking and argumentation", "description": "One of the university's oldest and most active societies."},
            {"name": "Documentary Filmmaking Society", "focus_area": "film production", "description": "Produces short documentaries on social issues."},
        ],
        "programs": [
            {"name": "BA Politics, Philosophy and Economics", "degree_type": "Bachelor's", "field": "social science", "description": "Interdisciplinary program combining political theory, philosophy, and economics."},
            {"name": "MSc Public Health Policy", "degree_type": "Master's", "field": "public health", "description": "Focused on health systems and policy evaluation."},
        ],
    },
    {
        "id": "inst_kyoto_innovation_university",
        "name": "Kyoto Innovation University",
        "country": "Japan",
        "city": "Kyoto",
        "research_culture": "Emphasizes long-term, methodical research with strong mentorship continuity between students and faculty.",
        "innovation_ecosystem": "Growing hub for robotics and precision-manufacturing startups, supported by regional industry.",
        "industry_collaboration": "Close relationships with regional manufacturing and electronics companies.",
        "placements": "Strong placement into Japanese engineering and manufacturing firms, plus a growing research pipeline.",
        "learning_environment": "Structured, discipline-focused environment valuing precision and depth over breadth.",
        "trait_tags": ["analytical_thinking", "learning_style"],
        "labs": [
            {"name": "Precision Robotics Lab", "focus_area": "industrial robotics", "description": "Develops precision manipulation systems for manufacturing."},
            {"name": "Human-Robot Interaction Lab", "focus_area": "robotics and design", "description": "Studies how humans and robots collaborate safely."},
        ],
        "orgs": [
            {"name": "Traditional Craft and Technology Society", "focus_area": "craft-technology fusion", "description": "Explores intersections between traditional craftsmanship and modern engineering."},
        ],
        "programs": [
            {"name": "BEng Mechanical and Robotics Engineering", "degree_type": "Bachelor's", "field": "robotics", "description": "Strong hands-on mechanical design foundation before specialization."},
            {"name": "PhD Robotics", "degree_type": "Doctorate", "field": "robotics", "description": "Long-form research track with close faculty mentorship."},
        ],
    },
    {
        "id": "inst_iias_bengaluru",
        "name": "Indian Institute of Advanced Sciences",
        "country": "India",
        "city": "Bengaluru",
        "research_culture": "Research-intensive with a strong emphasis on applied science and engineering problems relevant to industry.",
        "innovation_ecosystem": "Located within India's largest technology hub, with dense startup and R&D-center density nearby.",
        "industry_collaboration": "Deep partnerships with both multinational tech R&D centers and homegrown startups.",
        "placements": "Strong placement into technology, biotech, and research roles domestically and internationally.",
        "learning_environment": "Rigorous, exam- and project-driven, with significant emphasis on foundational depth.",
        "trait_tags": ["analytical_thinking", "curiosity"],
        "labs": [
            {"name": "Genomics and Computational Biology Lab", "focus_area": "computational biology", "description": "Applies machine learning to genomic data analysis."},
            {"name": "Astrophysics and Space Sciences Lab", "focus_area": "astrophysics", "description": "Studies exoplanet detection and stellar formation."},
        ],
        "orgs": [
            {"name": "Entrepreneurship Cell", "focus_area": "startup incubation", "description": "Supports student startup teams with mentorship and seed funding connections."},
        ],
        "programs": [
            {"name": "BTech Computer Science and Engineering", "degree_type": "Bachelor's", "field": "computer science", "description": "Broad computing foundation with strong research exposure."},
            {"name": "MSc Computational Biology", "degree_type": "Master's", "field": "computational biology", "description": "Combines biology, statistics, and machine learning."},
            {"name": "PhD Astrophysics", "degree_type": "Doctorate", "field": "astrophysics", "description": "Research-focused doctoral track in observational and theoretical astrophysics."},
        ],
    },
    {
        "id": "inst_nordholm_technical_university",
        "name": "Nordholm Technical University",
        "country": "Sweden",
        "city": "Stockholm",
        "research_culture": "Strong sustainability and climate-focused research culture across engineering disciplines.",
        "innovation_ecosystem": "Active climate-tech and clean-energy startup scene, supported by national innovation funding.",
        "industry_collaboration": "Partnerships with major Nordic energy and manufacturing companies on sustainability projects.",
        "placements": "Strong placement into clean energy, sustainable engineering, and climate policy roles.",
        "learning_environment": "Collaborative, project-based, with significant group work and industry-sponsored capstones.",
        "trait_tags": ["values", "analytical_thinking"],
        "labs": [
            {"name": "Sustainable Energy Systems Lab", "focus_area": "renewable energy engineering", "description": "Researches grid-scale renewable energy integration."},
            {"name": "Climate Materials Lab", "focus_area": "sustainable materials", "description": "Develops lower-carbon-footprint industrial materials."},
        ],
        "orgs": [
            {"name": "Climate Action Student Network", "focus_area": "sustainability advocacy", "description": "Organizes campus sustainability initiatives and policy campaigns."},
        ],
        "programs": [
            {"name": "MSc Sustainable Energy Engineering", "degree_type": "Master's", "field": "energy engineering", "description": "Focused on renewable energy systems design."},
            {"name": "BEng Environmental Engineering", "degree_type": "Bachelor's", "field": "environmental engineering", "description": "Core engineering foundation applied to environmental systems."},
        ],
    },
    {
        "id": "inst_cape_town_design_school",
        "name": "Cape Town School of Design and Innovation",
        "country": "South Africa",
        "city": "Cape Town",
        "research_culture": "Practice-based research culture centered on design methods and creative process documentation.",
        "innovation_ecosystem": "Growing regional creative-industries and design-tech startup scene.",
        "industry_collaboration": "Partnerships with regional design studios, media companies, and consumer brands.",
        "placements": "Strong placement into design, UX, and creative industry roles across Africa and internationally.",
        "learning_environment": "Studio-based, critique-driven, with heavy emphasis on portfolio development.",
        "trait_tags": ["creativity", "communication"],
        "labs": [
            {"name": "Human-Centered Design Lab", "focus_area": "UX research", "description": "Studies user behavior across digital product design."},
        ],
        "orgs": [
            {"name": "Design Collective", "focus_area": "collaborative design projects", "description": "Cross-disciplinary student design studio working with local businesses."},
            {"name": "Film and New Media Society", "focus_area": "digital media production", "description": "Produces short films and digital media projects."},
        ],
        "programs": [
            {"name": "BA User Experience Design", "degree_type": "Bachelor's", "field": "design", "description": "Combines psychology, visual design, and prototyping."},
            {"name": "MA Design Innovation", "degree_type": "Master's", "field": "design", "description": "Advanced studio-based design research program."},
        ],
    },
    {
        "id": "inst_andes_global_university",
        "name": "Andes Global University",
        "country": "Chile",
        "city": "Santiago",
        "research_culture": "Balanced research culture spanning engineering, public policy, and natural sciences, serving as a regional research hub.",
        "innovation_ecosystem": "Emerging regional startup ecosystem with growing government innovation support.",
        "industry_collaboration": "Partnerships with regional mining, agriculture, and renewable energy industries.",
        "placements": "Strong regional placement across engineering, public sector, and growing tech sectors.",
        "learning_environment": "Structured coursework with increasing research integration in later years.",
        "trait_tags": ["analytical_thinking", "values"],
        "labs": [
            {"name": "Renewable Resources Lab", "focus_area": "renewable energy and mining sustainability", "description": "Researches sustainable practices in resource-intensive industries."},
        ],
        "orgs": [
            {"name": "Public Health Student Association", "focus_area": "community health initiatives", "description": "Runs community health outreach programs."},
        ],
        "programs": [
            {"name": "BSc Public Health", "degree_type": "Bachelor's", "field": "public health", "description": "Focused on regional health systems and policy."},
            {"name": "BEng Environmental and Mining Engineering", "degree_type": "Bachelor's", "field": "environmental engineering", "description": "Addresses sustainability in resource-intensive industries."},
        ],
    },
    {
        "id": "inst_pacific_rim_media_arts",
        "name": "Pacific Rim Institute of Media Arts",
        "country": "Australia",
        "city": "Sydney",
        "research_culture": "Practice-led research culture centered on media production, storytelling, and creative technology.",
        "innovation_ecosystem": "Active media, gaming, and creative-technology startup scene.",
        "industry_collaboration": "Strong ties to film, game development, and digital media studios across the Asia-Pacific region.",
        "placements": "Strong placement into film, game development, and content creation industries.",
        "learning_environment": "Production-focused, deadline-driven, with frequent industry-judged showcases.",
        "trait_tags": ["creativity", "learning_style"],
        "labs": [
            {"name": "Interactive Media Lab", "focus_area": "game development research", "description": "Explores emerging interactive storytelling and game design techniques."},
        ],
        "orgs": [
            {"name": "Independent Game Developers Guild", "focus_area": "game jams and indie development", "description": "Organizes regular game jams and showcases student-built games."},
        ],
        "programs": [
            {"name": "BA Game Design and Development", "degree_type": "Bachelor's", "field": "game development", "description": "Combines programming, design, and narrative craft."},
            {"name": "BA Documentary Filmmaking", "degree_type": "Bachelor's", "field": "film", "description": "Practice-based documentary production program."},
        ],
    },
    {
        # V13 — NIAT is seeded as Aureon's first collaborating educational
        # organization and serves as the demonstration partner for the
        # College Collaboration ecosystem — never described as a
        # university anywhere in copy.
        "id": "inst_niat",
        "name": "NIAT",
        "country": "India",
        "city": "Hyderabad",
        "research_culture": "Applied, project-first learning culture built around real industry problems rather than lecture-first instruction.",
        "innovation_ecosystem": "An in-house innovation and incubation environment connecting student projects directly to industry mentors.",
        "industry_collaboration": "Active collaboration with technology companies on curriculum design, live projects, and hiring pipelines.",
        "placements": "Strong placement pipeline into full-stack, AI, and product engineering roles.",
        "learning_environment": "Cohort-based, project-driven, with continuous real-world building rather than exam-only assessment.",
        "trait_tags": ["analytical_thinking", "motivation", "curiosity"],
        "is_partner": True,
        "campus_life_and_culture": "A high-energy, builder-first culture — students spend more time shipping real projects with peers than sitting in lectures.",
        "fees_summary": "Program fees are structured around outcome-linked plans in addition to standard upfront tuition; specifics vary by track.",
        "scholarships_summary": "Merit-based fee waivers are available for standout project portfolios submitted during admissions.",
        "labs": [
            {"name": "Applied AI Lab", "focus_area": "applied machine learning", "description": "Student teams build real applied-AI projects with industry mentor guidance."},
        ],
        "orgs": [
            {"name": "Builders Guild", "focus_area": "peer-led project building", "description": "A student-run community organizing build sprints and peer code reviews."},
        ],
        "programs": [
            {"name": "Full-Stack Development Track", "degree_type": "Certificate", "field": "software engineering", "description": "Project-based full-stack web and mobile development training."},
            {"name": "AI/ML Engineering Track", "degree_type": "Certificate", "field": "artificial intelligence", "description": "Applied machine learning and AI systems engineering training."},
        ],
        "innovation_centers": [
            {"name": "NIAT Innovation Hub", "focus_area": "student product incubation", "description": "Supports student teams turning course projects into real, demoable products."},
        ],
        "faculty_highlights": [
            {"name": "Lead Instructor, Full-Stack Track", "title": "Full-Stack Engineering Lead", "expertise_area": "full-stack web development", "bio": "Guides cohorts through building and shipping complete full-stack applications."},
            {"name": "Lead Instructor, AI/ML Track", "title": "AI/ML Engineering Lead", "expertise_area": "applied machine learning", "bio": "Guides cohorts through applied AI/ML projects grounded in real datasets."},
        ],
        "student_ambassadors": [
            {"student_label": "Full-Stack Track, Cohort 3", "program": "Full-Stack Development Track", "message": "The project-first format meant I was shipping real features within the first few weeks."},
            {"student_label": "AI/ML Track, Cohort 2", "program": "AI/ML Engineering Track", "message": "Working directly with industry mentors on applied AI projects changed how I think about building, not just learning theory."},
        ],
        "student_projects": [
            {"student_label": "Full-Stack Track student team", "project_title": "Campus Resource Booking Platform", "description": "A real-time booking system for shared campus resources, built end-to-end by a student team.", "skills_used": ["React", "FastAPI", "PostgreSQL"]},
            {"student_label": "AI/ML Track student team", "project_title": "Attendance Insight System", "description": "A computer-vision-based attendance analytics prototype built as a cohort capstone project.", "skills_used": ["Python", "Computer Vision", "PyTorch"]},
        ],
        "internship_opportunities": [
            {"title": "Full-Stack Engineering Internship", "field": "software engineering", "description": "A structured internship pairing students with partner-company engineering teams."},
            {"title": "Applied AI Internship", "field": "artificial intelligence", "description": "A structured internship applying AI/ML skills to real partner-company problems."},
        ],
    },
]

#: V13 — shared Experience Events Knowledge Base (workshops/hackathons/
#: open days are institution-hosted; career talks are mentor-hosted).
CAREER_EVENTS: list[dict] = [
    {
        "id": "event_niat_hackathon_1",
        "title": "NIAT Build Sprint Hackathon",
        "event_type": "hackathon",
        "institution_id": "inst_niat",
        "description": "A weekend build sprint where student teams ship a working prototype from scratch.",
    },
    {
        "id": "event_niat_open_day_1",
        "title": "NIAT Open Day",
        "event_type": "open_day",
        "institution_id": "inst_niat",
        "description": "An open campus day for prospective students to see real student projects and meet current cohorts.",
    },
    {
        "id": "event_niat_workshop_1",
        "title": "Applied AI Workshop",
        "event_type": "workshop",
        "institution_id": "inst_niat",
        "description": "A hands-on workshop introducing applied machine learning through a real dataset walkthrough.",
    },
    {
        "id": "event_marcus_chen_talk",
        "title": "Scaling Backend Systems: A Career Talk",
        "event_type": "career_talk",
        "mentor_id": "mentor_marcus_chen",
        "description": "A career talk on what it actually looks like to grow from junior engineer to tech lead.",
    },
    {
        "id": "event_aisha_osei_talk",
        "title": "Breaking Into UX Design: A Career Talk",
        "event_type": "career_talk",
        "mentor_id": "mentor_aisha_osei",
        "description": "A career talk on building a design portfolio and breaking into product design roles.",
    },
]


#: Keys on an INSTITUTIONS entry that are nested child-entity lists, never
#: passed directly to Institution.model_validate.
_INSTITUTION_CHILD_KEYS = (
    "labs", "orgs", "programs", "innovation_centers", "faculty_highlights",
    "student_ambassadors", "student_projects", "internship_opportunities",
)

#: Explore Batch 1 — Entrance Hub merged into College Explorer. Real
#: exams accepted by multiple institutions (see approved plan's
#: Decisions Log on why this is a denormalized, institution-independent
#: entity rather than an institution-owned child table).
ENTRANCE_EXAMS: list[dict] = [
    {
        "id": "exam_global_engineering_aptitude",
        "name": "Global Engineering Aptitude Test",
        "description": "A widely used entrance exam assessing mathematics, physics, and problem-solving for engineering and applied-science programs.",
        "eligibility": ["Completed or completing secondary/high school education", "Strong foundation in mathematics and physics"],
        "preparation_guidance": "Focused practice on mathematics and physics problem sets, plus timed mock exams closer to the test date.",
        "typical_timeline": "Registration typically opens 4-6 months before the exam; scores are usually valid for one admissions cycle.",
        "accepted_institution_ids": ["inst_aurora_institute", "inst_nordholm_technical_university", "inst_niat"],
    },
    {
        "id": "exam_international_liberal_arts_assessment",
        "name": "International Liberal Arts Assessment",
        "description": "An entrance assessment for broad liberal-arts and interdisciplinary undergraduate programs, covering critical reading, writing, and reasoning.",
        "eligibility": ["Completed or completing secondary/high school education"],
        "preparation_guidance": "Reading widely across disciplines and practicing structured argumentative writing under time constraints.",
        "typical_timeline": "Offered multiple times a year; most institutions accept scores from the past two years.",
        "accepted_institution_ids": ["inst_meridian_university", "inst_andes_global_university"],
    },
    {
        "id": "exam_design_portfolio_review",
        "name": "Design & Creative Portfolio Review",
        "description": "A portfolio-based entrance process (not a written exam) used by design and creative-arts programs to assess real creative work.",
        "eligibility": ["A body of original creative work in the relevant discipline"],
        "preparation_guidance": "Building a focused, honest portfolio of real completed work rather than a large volume of unfinished pieces.",
        "typical_timeline": "Portfolio submission windows typically open 3-4 months before the admissions decision date.",
        "accepted_institution_ids": ["inst_cape_town_design_school", "inst_pacific_rim_media_arts"],
    },
    {
        "id": "exam_research_aptitude_interview",
        "name": "Research Aptitude Interview",
        "description": "A structured interview-based assessment used by research-intensive programs to evaluate scientific reasoning and genuine research interest.",
        "eligibility": ["Completing or holding a relevant undergraduate degree", "Some prior research exposure recommended but not required"],
        "preparation_guidance": "Preparing to discuss real prior projects/coursework in depth, and reading recent work from the specific research groups of interest.",
        "typical_timeline": "Interviews are typically scheduled 2-3 months after an initial application review.",
        "accepted_institution_ids": ["inst_kyoto_innovation_university", "inst_iias_bengaluru"],
    },
]


async def seed() -> None:
    client = get_supabase_client()

    mentors = [Mentor.model_validate(m) for m in MENTORS]

    institutions: list[Institution] = []
    labs: list[ResearchLab] = []
    orgs: list[StudentOrganization] = []
    programs: list[AcademicProgram] = []
    innovation_centers: list[InnovationCenter] = []
    faculty_highlights: list[FacultyHighlight] = []
    student_ambassadors: list[StudentAmbassador] = []
    student_projects: list[StudentProject] = []
    internship_opportunities: list[InternshipOpportunity] = []

    for entry in INSTITUTIONS:
        inst_id = entry["id"]
        institutions.append(
            Institution.model_validate({k: v for k, v in entry.items() if k not in _INSTITUTION_CHILD_KEYS})
        )
        for i, lab in enumerate(entry["labs"]):
            labs.append(ResearchLab(id=f"{inst_id}_lab_{i}", institution_id=inst_id, **lab))
        for i, org in enumerate(entry["orgs"]):
            orgs.append(StudentOrganization(id=f"{inst_id}_org_{i}", institution_id=inst_id, **org))
        for i, program in enumerate(entry["programs"]):
            programs.append(AcademicProgram(id=f"{inst_id}_program_{i}", institution_id=inst_id, **program))
        for i, center in enumerate(entry.get("innovation_centers", [])):
            innovation_centers.append(InnovationCenter(id=f"{inst_id}_innovation_{i}", institution_id=inst_id, **center))
        for i, faculty in enumerate(entry.get("faculty_highlights", [])):
            faculty_highlights.append(FacultyHighlight(id=f"{inst_id}_faculty_{i}", institution_id=inst_id, **faculty))
        for i, ambassador in enumerate(entry.get("student_ambassadors", [])):
            student_ambassadors.append(StudentAmbassador(id=f"{inst_id}_ambassador_{i}", institution_id=inst_id, **ambassador))
        for i, project in enumerate(entry.get("student_projects", [])):
            student_projects.append(StudentProject(id=f"{inst_id}_project_{i}", institution_id=inst_id, **project))
        for i, internship in enumerate(entry.get("internship_opportunities", [])):
            internship_opportunities.append(InternshipOpportunity(id=f"{inst_id}_internship_{i}", institution_id=inst_id, **internship))

    events = [CareerEvent.model_validate(e) for e in CAREER_EVENTS]
    entrance_exams = [EntranceExam.model_validate(x) for x in ENTRANCE_EXAMS]

    def _upsert() -> None:
        client.table("mentors").upsert([m.model_dump(mode="json") for m in mentors]).execute()
        client.table("institutions").upsert([i.model_dump(mode="json") for i in institutions]).execute()
        client.table("entrance_exams").upsert([x.model_dump(mode="json") for x in entrance_exams]).execute()
        client.table("research_labs").upsert([lb.model_dump(mode="json") for lb in labs]).execute()
        client.table("student_organizations").upsert([o.model_dump(mode="json") for o in orgs]).execute()
        client.table("academic_programs").upsert([p.model_dump(mode="json") for p in programs]).execute()
        client.table("innovation_centers").upsert([c.model_dump(mode="json") for c in innovation_centers]).execute()
        client.table("faculty_highlights").upsert([f.model_dump(mode="json") for f in faculty_highlights]).execute()
        client.table("student_ambassadors").upsert([a.model_dump(mode="json") for a in student_ambassadors]).execute()
        client.table("student_projects").upsert([p.model_dump(mode="json") for p in student_projects]).execute()
        client.table("internship_opportunities").upsert([i.model_dump(mode="json") for i in internship_opportunities]).execute()
        client.table("career_events").upsert([e.model_dump(mode="json") for e in events]).execute()

    await asyncio.to_thread(_upsert)
    print(
        f"Seeded {len(mentors)} mentors, {len(institutions)} institutions, "
        f"{len(labs)} research labs, {len(orgs)} student organizations, {len(programs)} academic programs, "
        f"{len(innovation_centers)} innovation centers, {len(faculty_highlights)} faculty highlights, "
        f"{len(student_ambassadors)} student ambassadors, {len(student_projects)} student projects, "
        f"{len(internship_opportunities)} internship opportunities, {len(events)} experience events, "
        f"{len(entrance_exams)} entrance exams."
    )


if __name__ == "__main__":
    asyncio.run(seed())

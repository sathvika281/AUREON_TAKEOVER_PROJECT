"""One-time seed script for Discover Batch 4's Life Missions catalog.

Run via: python -m aureon.scripts.seed_life_missions

A comprehensive (22-mission) catalog of real-world-impact missions a
student might resonate with — purpose discovery, not career
recommendation. Each mission carries rich, real, production-quality
metadata: famous people, organizations, books, documentaries, podcasts,
real-world examples, suggested careers, and more, favoring
domain-specific real names over generically-famous ones repeated
everywhere. Every entry carries its own `source_note` honesty
disclaimer (see domain/models/life_mission.py). Idempotent: upserts by
id, safe to re-run.
"""

import asyncio

from aureon.domain.models.life_mission import LifeMission
from aureon.services.supabase.client import get_supabase_client

MISSIONS: list[dict] = [
    {
        "id": "mission_build_technology",
        "name": "Build Technology",
        "description": "The drive to build tools, software, and systems that make things possible for other people — from a small app that saves someone time to infrastructure that runs at global scale.",
        "famous_people": [
            "Grace Hopper",
            "Linus Torvalds",
            "Margaret Hamilton",
            "Ada Lovelace"
        ],
        "organizations": [
            "Mozilla Foundation",
            "Free Software Foundation",
            "Internet Archive",
            "Electronic Frontier Foundation",
            "Ford Foundation",
            "Bill & Melinda Gates Foundation",
            "Rockefeller Foundation",
            "Open Society Foundations"
        ],
        "companies": [
            "GitHub",
            "Vercel",
            "Stripe",
            "Zerodha",
            "Salesforce"
        ],
        "nonprofits": [
            "Code.org",
            "Girls Who Code",
            "Software Carpentry"
        ],
        "books": [
            "The Mythical Man-Month by Fred Brooks",
            "Hackers by Steven Levy",
            "The Soul of a New Machine by Tracy Kidder"
        ],
        "documentaries": [
            "General Magic",
            "Coded Bias",
            "The Social Dilemma",
            "Icarus"
        ],
        "podcasts": [
            "Changelog",
            "Software Engineering Daily",
            "TED Talks Daily",
            "Freakonomics Radio"
        ],
        "communities": [
            "r/programming (Reddit)",
            "local hackathon and coding-club communities"
        ],
        "real_world_examples": [
            "Open-source maintainers keeping critical infrastructure running for free",
            "A student building a tool that automates a tedious school process",
            "Engineers building accessibility tools for people with disabilities"
        ],
        "suggested_careers": [
            "Software Engineer",
            "Systems Architect",
            "DevOps Engineer",
            "Product Engineer",
            "Open-Source Maintainer"
        ],
        "projects": [
            "Build and ship a small real tool someone else actually uses",
            "Contribute a fix to an open-source project",
            "Automate a repetitive task with a script",
            "Build a personal website or portfolio app"
        ],
        "volunteering_opportunities": [
            "Teach a coding club at a local school",
            "Contribute to a nonprofit's open-source tooling",
            "Mentor a beginner through a coding community"
        ],
        "research_areas": [
            "Distributed systems",
            "Human-computer interaction",
            "Programming-language design"
        ],
        "startup_ideas": [
            "A tool that automates a specific tedious workflow",
            "An accessibility-focused app for an underserved group",
            "A developer tool that saves other engineers real time"
        ],
        "related_tags": [
            "technology",
            "software",
            "engineering",
            "programming",
            "systems",
            "build",
            "code"
        ]
    },
    {
        "id": "mission_solve_climate_problems",
        "name": "Solve Climate Problems",
        "description": "Working directly on reducing emissions, adapting infrastructure, and protecting communities from a changing climate — through science, engineering, policy, or organizing.",
        "famous_people": [
            "Greta Thunberg",
            "Katharine Hayhoe",
            "Bill McKibben",
            "Wangari Maathai"
        ],
        "organizations": [
            "Project Drawdown",
            "Climate Reality Project",
            "350.org",
            "Rocky Mountain Institute",
            "MacArthur Foundation",
            "Carnegie Endowment for International Peace",
            "Aspen Institute",
            "World Economic Forum"
        ],
        "companies": [
            "Tesla Energy",
            "Ørsted",
            "Climeworks",
            "Beyond Meat",
            "Ben & Jerry's"
        ],
        "nonprofits": [
            "Environmental Defense Fund",
            "Sunrise Movement",
            "Fridays for Future"
        ],
        "books": [
            "Drawdown edited by Paul Hawken",
            "How to Avoid a Climate Disaster by Bill Gates",
            "The Uninhabitable Earth by David Wallace-Wells"
        ],
        "documentaries": [
            "An Inconvenient Truth",
            "Kiss the Ground",
            "Chasing Coral",
            "Won't You Be My Neighbor?"
        ],
        "podcasts": [
            "How to Save a Planet",
            "Outrage + Optimism",
            "Planet Money",
            "Hidden Brain"
        ],
        "communities": [
            "r/climate (Reddit)",
            "local Fridays for Future chapters"
        ],
        "real_world_examples": [
            "A city redesigning stormwater systems for extreme-weather resilience",
            "A company switching its supply chain to renewable energy",
            "A student-led campaign getting a school to install solar panels"
        ],
        "suggested_careers": [
            "Climate Scientist",
            "Renewable Energy Engineer",
            "Sustainability Consultant",
            "Environmental Policy Analyst",
            "Carbon Markets Analyst"
        ],
        "projects": [
            "Run a school energy or waste audit",
            "Build a small solar or wind demo project",
            "Analyze local climate-data trends",
            "Organize a sustainability campaign with a measurable goal"
        ],
        "volunteering_opportunities": [
            "Volunteer with a local environmental campaign",
            "Join a community solar or tree-planting initiative",
            "Help a nonprofit measure its carbon footprint"
        ],
        "research_areas": [
            "Carbon capture technology",
            "Climate-resilient infrastructure",
            "Renewable-energy storage"
        ],
        "startup_ideas": [
            "A carbon-footprint tracking tool for small businesses",
            "A marketplace connecting reclaimed materials to builders",
            "A local renewable-energy microgrid service"
        ],
        "related_tags": [
            "climate",
            "sustainability",
            "environment",
            "renewable energy",
            "carbon",
            "conservation"
        ]
    },
    {
        "id": "mission_improve_healthcare",
        "name": "Improve Healthcare",
        "description": "Making healthcare more effective, accessible, and humane — through direct clinical care, medical research, health technology, or health-system design.",
        "famous_people": [
            "Paul Farmer",
            "Atul Gawande",
            "Jonas Salk",
            "Florence Nightingale"
        ],
        "organizations": [
            "World Health Organization",
            "Partners In Health",
            "Doctors Without Borders",
            "TED",
            "Skoll Foundation",
            "Clinton Foundation",
            "Wellcome Trust"
        ],
        "companies": [
            "Moderna",
            "Apollo Hospitals",
            "Illumina",
            "Practo",
            "Patagonia"
        ],
        "nonprofits": [
            "PATH",
            "Global Fund to Fight AIDS, Tuberculosis and Malaria",
            "Direct Relief"
        ],
        "books": [
            "Being Mortal by Atul Gawande",
            "Mountains Beyond Mountains by Tracy Kidder",
            "The Emperor of All Maladies by Siddhartha Mukherjee"
        ],
        "documentaries": [
            "The Bleeding Edge",
            "Fed Up",
            "Human Nature",
            "RBG"
        ],
        "podcasts": [
            "Freakonomics, M.D.",
            "The Peter Attia Drive",
            "The Ezra Klein Show",
            "Invisibilia"
        ],
        "communities": [
            "r/medicine (Reddit)",
            "Health Occupations Students of America (HOSA)"
        ],
        "real_world_examples": [
            "A rural clinic using telemedicine to reach patients who can't travel",
            "A public-health team eliminating a disease outbreak through vaccination drives",
            "A biomedical engineer designing low-cost diagnostic devices for underserved regions"
        ],
        "suggested_careers": [
            "Physician",
            "Public Health Analyst",
            "Biomedical Engineer",
            "Health Policy Researcher",
            "Nurse Practitioner"
        ],
        "projects": [
            "Organize a health-awareness campaign at school",
            "Volunteer consistently at a clinic or hospital",
            "Research a real public-health issue in your community",
            "Design a low-cost health-monitoring prototype"
        ],
        "volunteering_opportunities": [
            "Volunteer at a hospital or community clinic",
            "Support a public-health awareness drive",
            "Assist a health nonprofit with outreach"
        ],
        "research_areas": [
            "Global health equity",
            "Medical diagnostics technology",
            "Health-systems design"
        ],
        "startup_ideas": [
            "A telemedicine platform for underserved rural areas",
            "A low-cost diagnostic device for common conditions",
            "A medication-adherence app for chronic-illness patients"
        ],
        "related_tags": [
            "healthcare",
            "medicine",
            "public health",
            "biomedical",
            "wellness",
            "clinical"
        ]
    },
    {
        "id": "mission_educate_people",
        "name": "Educate People",
        "description": "Helping other people learn and grow — through direct teaching, curriculum design, mentoring, or building tools and platforms that make learning more accessible.",
        "famous_people": [
            "Malala Yousafzai",
            "Sal Khan",
            "Maria Montessori",
            "Paulo Freire"
        ],
        "organizations": [
            "UNESCO",
            "Teach For All",
            "Room to Read",
            "Robert Wood Johnson Foundation",
            "Ford Foundation",
            "Bill & Melinda Gates Foundation",
            "Rockefeller Foundation"
        ],
        "companies": [
            "Khan Academy",
            "Coursera",
            "Duolingo",
            "BYJU'S",
            "Danone"
        ],
        "nonprofits": [
            "Pratham",
            "Room to Read",
            "DonorsChoose"
        ],
        "books": [
            "Mindset by Carol Dweck",
            "Pedagogy of the Oppressed by Paulo Freire",
            "Make It Stick by Peter Brown"
        ],
        "documentaries": [
            "Waiting for Superman",
            "Most Likely to Succeed",
            "He Named Me Malala",
            "The True Cost"
        ],
        "podcasts": [
            "Cult of Pedagogy",
            "Freakonomics Radio (education episodes)",
            "99% Invisible",
            "WorkLife with Adam Grant"
        ],
        "communities": [
            "r/Teachers (Reddit)",
            "local peer-tutoring programs"
        ],
        "real_world_examples": [
            "A teacher redesigning a curriculum to reach struggling students",
            "A nonprofit building libraries in underserved regions",
            "A student launching a free tutoring program for peers"
        ],
        "suggested_careers": [
            "Classroom Teacher",
            "Instructional Designer",
            "EdTech Product Manager",
            "School Counselor",
            "Curriculum Developer"
        ],
        "projects": [
            "Tutor a student in a subject you're strong in",
            "Design and teach a mini-lesson to peers",
            "Build a simple learning app or study tool",
            "Start a free peer-tutoring program"
        ],
        "volunteering_opportunities": [
            "Volunteer with a literacy or after-school program",
            "Mentor a younger student",
            "Help a local school digitize learning materials"
        ],
        "research_areas": [
            "Learning science",
            "Educational equity",
            "Personalized-learning technology"
        ],
        "startup_ideas": [
            "A peer-tutoring marketplace for a specific subject",
            "A learning app for an underserved language community",
            "A tool that helps teachers personalize lesson plans"
        ],
        "related_tags": [
            "education",
            "teaching",
            "learning",
            "curriculum",
            "literacy",
            "mentoring"
        ]
    },
    {
        "id": "mission_discover_knowledge",
        "name": "Discover Knowledge",
        "description": "The pursuit of understanding for its own sake — asking real questions, running real experiments, and pushing the edge of what's known through rigorous inquiry.",
        "famous_people": [
            "Marie Curie",
            "Richard Feynman",
            "Jane Goodall",
            "Katherine Johnson"
        ],
        "organizations": [
            "CERN",
            "National Geographic Society",
            "Royal Society",
            "Open Society Foundations",
            "MacArthur Foundation",
            "Carnegie Endowment for International Peace",
            "Aspen Institute"
        ],
        "companies": [
            "DeepMind",
            "Bell Labs",
            "Tata Institute of Fundamental Research",
            "Unilever"
        ],
        "nonprofits": [
            "Society for Science",
            "American Association for the Advancement of Science"
        ],
        "books": [
            "A Short History of Nearly Everything by Bill Bryson",
            "Lab Girl by Hope Jahren",
            "The Structure of Scientific Revolutions by Thomas Kuhn"
        ],
        "documentaries": [
            "Particle Fever",
            "Jane",
            "The Farthest",
            "Blackfish"
        ],
        "podcasts": [
            "Radiolab",
            "Science Vs",
            "TED Talks Daily",
            "Freakonomics Radio"
        ],
        "communities": [
            "r/AskScience (Reddit)",
            "university undergraduate research programs"
        ],
        "real_world_examples": [
            "A grad student's small experiment leading to an unexpected discovery",
            "A citizen-science project mapping biodiversity",
            "A researcher spending years verifying one precise measurement"
        ],
        "suggested_careers": [
            "Research Scientist",
            "Data Scientist",
            "Lab Technician",
            "Postdoctoral Researcher",
            "Field Researcher"
        ],
        "projects": [
            "Design and run a simple experiment",
            "Write a literature review on a topic of interest",
            "Enter a school science fair",
            "Replicate a published study's basic method"
        ],
        "volunteering_opportunities": [
            "Join a citizen-science project",
            "Assist a university research lab",
            "Help organize a local science fair"
        ],
        "research_areas": [
            "Fundamental physics",
            "Behavioral ecology",
            "Cognitive science"
        ],
        "startup_ideas": [
            "A citizen-science data-collection app",
            "A tool that makes research papers more accessible to non-experts",
            "A platform connecting amateur researchers to real projects"
        ],
        "related_tags": [
            "research",
            "science",
            "discovery",
            "curiosity",
            "experiment",
            "knowledge"
        ]
    },
    {
        "id": "mission_create_art",
        "name": "Create Art",
        "description": "Making things that move people — visual art, illustration, sculpture, and creative work built on technical craft and honest self-expression.",
        "famous_people": [
            "Frida Kahlo",
            "Yayoi Kusama",
            "Banksy",
            "Ai Weiwei"
        ],
        "organizations": [
            "Museum of Modern Art (MoMA)",
            "Tate",
            "Serpentine Galleries",
            "World Economic Forum",
            "TED",
            "Skoll Foundation",
            "Clinton Foundation"
        ],
        "companies": [
            "Adobe",
            "Christie's",
            "Sotheby's",
            "IKEA"
        ],
        "nonprofits": [
            "Art for Justice Fund",
            "Studio in a School"
        ],
        "books": [
            "Art & Fear by David Bayles and Ted Orland",
            "Ways of Seeing by John Berger",
            "The Artist's Way by Julia Cameron"
        ],
        "documentaries": [
            "Exit Through the Gift Shop",
            "Frida",
            "Kusama: Infinity",
            "Cowspiracy"
        ],
        "podcasts": [
            "Art Curious",
            "The Great Women Artists",
            "Planet Money",
            "Hidden Brain"
        ],
        "communities": [
            "r/Art (Reddit)",
            "local art collective and co-op studios"
        ],
        "real_world_examples": [
            "A muralist transforming an underused public space",
            "An illustrator building a following through consistent daily practice",
            "An art-therapy program helping trauma survivors process experience"
        ],
        "suggested_careers": [
            "Illustrator",
            "Fine Artist",
            "Art Curator",
            "Muralist",
            "Art Therapist"
        ],
        "projects": [
            "Create a themed series of 10 original works",
            "Curate a small exhibition, even informally",
            "Paint a public mural with community input",
            "Sell or exhibit one piece publicly"
        ],
        "volunteering_opportunities": [
            "Teach a free art class for kids",
            "Volunteer at a local gallery or museum",
            "Contribute art to a community mural project"
        ],
        "research_areas": [
            "Art therapy",
            "Public art and urban design",
            "Digital-art tools"
        ],
        "startup_ideas": [
            "A platform connecting local artists with public-art commissions",
            "An affordable art-supplies exchange for students",
            "A digital-illustration commission marketplace"
        ],
        "related_tags": [
            "art",
            "creativity",
            "illustration",
            "design",
            "expression",
            "visual"
        ]
    },
    {
        "id": "mission_entertain_millions",
        "name": "Entertain Millions",
        "description": "Creating stories, games, music, or performances that bring joy, connection, and shared experience to large audiences.",
        "famous_people": [
            "Hayao Miyazaki",
            "Shonda Rhimes",
            "Hideo Kojima",
            "Beyoncé"
        ],
        "organizations": [
            "Sundance Institute",
            "Academy of Motion Picture Arts and Sciences",
            "Recording Academy",
            "Wellcome Trust",
            "Robert Wood Johnson Foundation",
            "Ford Foundation",
            "Bill & Melinda Gates Foundation"
        ],
        "companies": [
            "Pixar Animation Studios",
            "Netflix",
            "Riot Games",
            "Studio Ghibli",
            "LEGO Group"
        ],
        "nonprofits": [
            "Sundance Institute",
            "American Film Institute"
        ],
        "books": [
            "Save the Cat by Blake Snyder",
            "The Art of Game Design by Jesse Schell",
            "Creativity, Inc. by Ed Catmull"
        ],
        "documentaries": [
            "Jiro Dreams of Sushi (craft parallel)",
            "20 Feet from Stardom",
            "Score: A Film Music Documentary",
            "The Social Dilemma"
        ],
        "podcasts": [
            "The Business (KCRW)",
            "Song Exploder",
            "The Ezra Klein Show",
            "Invisibilia"
        ],
        "communities": [
            "r/filmmakers (Reddit)",
            "r/gamedev (Reddit)"
        ],
        "real_world_examples": [
            "An indie game studio reaching millions of players with a tiny team",
            "A songwriter's track becoming a global cultural moment",
            "A streaming series sparking worldwide conversation"
        ],
        "suggested_careers": [
            "Director",
            "Game Designer",
            "Composer",
            "Screenwriter",
            "Producer"
        ],
        "projects": [
            "Shoot and edit a short film",
            "Build and ship a small playable game",
            "Write and record an original song",
            "Produce a short-form video series"
        ],
        "volunteering_opportunities": [
            "Crew on a local student film production",
            "Volunteer at a community arts festival",
            "Mentor a young creator in your craft"
        ],
        "research_areas": [
            "Narrative design",
            "Audience psychology",
            "Interactive storytelling"
        ],
        "startup_ideas": [
            "A platform for discovering independent creators in a niche genre",
            "A tool that helps small creative teams produce content faster",
            "A local-language entertainment platform for an underserved market"
        ],
        "related_tags": [
            "entertainment",
            "film",
            "music",
            "gaming",
            "storytelling",
            "media"
        ]
    },
    {
        "id": "mission_protect_nature",
        "name": "Protect Nature",
        "description": "Conserving ecosystems and natural resources — forests, wetlands, rivers, and biodiversity — through science, land management, and advocacy.",
        "famous_people": [
            "Wangari Maathai",
            "David Attenborough",
            "Rachel Carson",
            "Aldo Leopold"
        ],
        "organizations": [
            "The Nature Conservancy",
            "World Wildlife Fund",
            "Sierra Club",
            "Rockefeller Foundation",
            "Open Society Foundations",
            "MacArthur Foundation",
            "Carnegie Endowment for International Peace"
        ],
        "companies": [
            "Patagonia",
            "Ecosia",
            "Salesforce"
        ],
        "nonprofits": [
            "Rainforest Alliance",
            "Conservation International"
        ],
        "books": [
            "Silent Spring by Rachel Carson",
            "The Sixth Extinction by Elizabeth Kolbert",
            "A Sand County Almanac by Aldo Leopold"
        ],
        "documentaries": [
            "Our Planet",
            "Chasing Ice",
            "The Biggest Little Farm",
            "Living on One Dollar"
        ],
        "podcasts": [
            "Nature Podcast",
            "The Wild",
            "99% Invisible",
            "WorkLife with Adam Grant"
        ],
        "communities": [
            "r/environment (Reddit)",
            "local conservation-volunteer networks"
        ],
        "real_world_examples": [
            "A reforestation project restoring a degraded watershed",
            "A community managing a marine protected area sustainably",
            "A land trust preserving open space near a growing city"
        ],
        "suggested_careers": [
            "Conservation Scientist",
            "Environmental Lawyer",
            "Park Ranger",
            "Land-Use Planner",
            "Ecologist"
        ],
        "projects": [
            "Organize a local tree-planting or cleanup project",
            "Map biodiversity in a nearby natural area",
            "Research a local conservation issue and propose action",
            "Build a native-species garden"
        ],
        "volunteering_opportunities": [
            "Volunteer with a land trust or conservation group",
            "Join a habitat-restoration workday",
            "Support an environmental-education program"
        ],
        "research_areas": [
            "Ecosystem restoration",
            "Conservation biology",
            "Land-use policy"
        ],
        "startup_ideas": [
            "A tool that helps landowners track reforestation progress",
            "A citizen-science biodiversity mapping app",
            "A sustainable land-management consultancy"
        ],
        "related_tags": [
            "nature",
            "conservation",
            "environment",
            "ecology",
            "wildlife",
            "sustainability"
        ]
    },
    {
        "id": "mission_build_businesses",
        "name": "Build Businesses",
        "description": "Creating and growing organizations that deliver real value sustainably — from a small local business to a scaling company solving a genuine problem.",
        "famous_people": [
            "Sara Blakely",
            "Phil Knight",
            "Falguni Nayar",
            "Whitney Wolfe Herd"
        ],
        "organizations": [
            "Y Combinator",
            "Techstars",
            "Indian School of Business Entrepreneurship Cell",
            "Aspen Institute",
            "World Economic Forum",
            "TED",
            "Skoll Foundation"
        ],
        "companies": [
            "Razorpay",
            "Flipkart",
            "Notion",
            "Ben & Jerry's"
        ],
        "nonprofits": [
            "Endeavor",
            "Network for Teaching Entrepreneurship"
        ],
        "books": [
            "Zero to One by Peter Thiel",
            "The Lean Startup by Eric Ries",
            "Shoe Dog by Phil Knight"
        ],
        "documentaries": [
            "Startup.com",
            "The Founder",
            "General Magic",
            "Icarus"
        ],
        "podcasts": [
            "How I Built This",
            "Masters of Scale",
            "TED Talks Daily",
            "Freakonomics Radio"
        ],
        "communities": [
            "r/startups (Reddit)",
            "local startup incubator meetups"
        ],
        "real_world_examples": [
            "A founder bootstrapping a small business to profitability without outside funding",
            "A student turning a side project into a real paying business",
            "A local entrepreneur solving a hyper-specific community need"
        ],
        "suggested_careers": [
            "Startup Founder",
            "Product Manager",
            "Operations Lead",
            "Business Development Manager",
            "Growth Marketer"
        ],
        "projects": [
            "Launch a small real product or service and get paying customers",
            "Run a micro-business with real numbers",
            "Pitch a business idea at a school competition",
            "Interview a local founder about their journey"
        ],
        "volunteering_opportunities": [
            "Mentor a peer's small-business idea",
            "Volunteer at a local business incubator event",
            "Help a small local business with basic operations"
        ],
        "research_areas": [
            "Business-model innovation",
            "Market entry strategy",
            "Organizational design"
        ],
        "startup_ideas": [
            "A tool solving a specific, underserved local problem",
            "A subscription service for an everyday need",
            "A B2B tool that saves small businesses real time"
        ],
        "related_tags": [
            "entrepreneurship",
            "business",
            "startup",
            "product",
            "growth",
            "venture"
        ]
    },
    {
        "id": "mission_explore_space",
        "name": "Explore Space",
        "description": "Pushing the boundary of what humanity knows and can reach beyond Earth — spacecraft, satellites, planetary science, and the systems that make exploration possible.",
        "famous_people": [
            "Katherine Johnson",
            "Yuri Gagarin",
            "Sally Ride",
            "Kalpana Chawla"
        ],
        "organizations": [
            "NASA",
            "ISRO",
            "European Space Agency",
            "Planetary Society",
            "Clinton Foundation",
            "Wellcome Trust",
            "Robert Wood Johnson Foundation",
            "Ford Foundation"
        ],
        "companies": [
            "SpaceX",
            "Blue Origin",
            "Rocket Lab",
            "Patagonia"
        ],
        "nonprofits": [
            "The Planetary Society",
            "Space Generation Advisory Council"
        ],
        "books": [
            "Cosmos by Carl Sagan",
            "An Astronaut's Guide to Life on Earth by Chris Hadfield",
            "Packing for Mars by Mary Roach"
        ],
        "documentaries": [
            "The Farthest",
            "In the Shadow of the Moon",
            "Apollo 11",
            "Won't You Be My Neighbor?"
        ],
        "podcasts": [
            "The Planetary Society's Planetary Radio",
            "Houston We Have a Podcast",
            "Planet Money",
            "Hidden Brain"
        ],
        "communities": [
            "r/space (Reddit)",
            "AIAA student chapters"
        ],
        "real_world_examples": [
            "A student-built CubeSat successfully reaching orbit",
            "A rover mission returning years of planetary data",
            "A small satellite startup enabling affordable Earth imaging"
        ],
        "suggested_careers": [
            "Aerospace Engineer",
            "Astronaut",
            "Planetary Scientist",
            "Satellite Systems Engineer",
            "Mission Control Specialist"
        ],
        "projects": [
            "Build and launch a model rocket",
            "Track satellites with a low-cost SDR receiver",
            "Simulate an orbital trajectory in Python",
            "Enter a CanSat or high-altitude balloon competition"
        ],
        "volunteering_opportunities": [
            "Volunteer with a local astronomy club",
            "Help run a school rocketry or CanSat program",
            "Support a citizen-science astronomy project"
        ],
        "research_areas": [
            "Planetary science",
            "Spacecraft propulsion",
            "Astrobiology"
        ],
        "startup_ideas": [
            "A low-cost satellite-imaging analysis service",
            "An educational space-simulation tool for schools",
            "A ground-station-as-a-service platform for small satellites"
        ],
        "related_tags": [
            "space",
            "aerospace",
            "astronomy",
            "satellites",
            "exploration",
            "rockets"
        ]
    },
    {
        "id": "mission_improve_government",
        "name": "Improve Government",
        "description": "Making public institutions work better — more transparent, efficient, and responsive — through civil service, policy design, or civic technology.",
        "famous_people": [
            "Jennifer Pahlka",
            "Atal Bihari Vajpayee (public administration reform)",
            "Angela Merkel"
        ],
        "organizations": [
            "Code for America",
            "Ash Center for Democratic Governance (Harvard)",
            "Centre for Civil Society",
            "Bill & Melinda Gates Foundation",
            "Rockefeller Foundation",
            "Open Society Foundations",
            "MacArthur Foundation"
        ],
        "companies": [
            "Deloitte Public Sector",
            "Palantir Government Solutions",
            "Danone"
        ],
        "nonprofits": [
            "Code for America",
            "Sunlight Foundation"
        ],
        "books": [
            "The Fifth Risk by Michael Lewis",
            "Recoding America by Jennifer Pahlka",
            "The Utopia of Rules by David Graeber"
        ],
        "documentaries": [
            "Knock Down the House",
            "Get Me Roger Stone (as a case study)",
            "The Vote",
            "RBG"
        ],
        "podcasts": [
            "Pod Save America",
            "The Weeds",
            "The Ezra Klein Show",
            "Invisibilia"
        ],
        "communities": [
            "r/PoliticalScience (Reddit)",
            "civic-tech volunteer networks"
        ],
        "real_world_examples": [
            "A city redesigning its permit process to cut wait times drastically",
            "A civic-tech team rebuilding a broken government website",
            "A local government adopting participatory budgeting"
        ],
        "suggested_careers": [
            "Civil Servant",
            "Public Administrator",
            "Policy Advisor",
            "Civic Technologist",
            "Legislative Analyst"
        ],
        "projects": [
            "Attend and report on a local government meeting",
            "Propose a specific process improvement to a local office",
            "Analyze public budget or service data",
            "Run for a student-government position"
        ],
        "volunteering_opportunities": [
            "Volunteer with a civic-engagement or election initiative",
            "Support a civic-tech project rebuilding a public service",
            "Intern with a local government office"
        ],
        "research_areas": [
            "Public-sector innovation",
            "Civic technology",
            "Government transparency"
        ],
        "startup_ideas": [
            "A civic-tech tool simplifying access to a public service",
            "A government-data transparency dashboard",
            "A platform helping citizens track local budget spending"
        ],
        "related_tags": [
            "government",
            "public administration",
            "civic",
            "policy",
            "democracy",
            "public service"
        ]
    },
    {
        "id": "mission_help_communities",
        "name": "Help Communities",
        "description": "Strengthening the people and places closest to home — organizing neighbors, running local programs, and building the social fabric that helps communities thrive.",
        "famous_people": [
            "Dorothy Day",
            "Cesar Chavez",
            "Jane Addams"
        ],
        "organizations": [
            "United Way",
            "Local Initiatives Support Corporation",
            "AmeriCorps",
            "Carnegie Endowment for International Peace",
            "Aspen Institute",
            "World Economic Forum",
            "TED"
        ],
        "companies": [
            "Nextdoor",
            "Patagonia (community grants program)",
            "Unilever"
        ],
        "nonprofits": [
            "United Way",
            "Habitat for Humanity",
            "Local community foundations"
        ],
        "books": [
            "Bowling Alone by Robert Putnam",
            "The Soul of a Citizen by Paul Loeb",
            "Palaces for the People by Eric Klinenberg"
        ],
        "documentaries": [
            "Waging Change",
            "American Factory",
            "The True Cost"
        ],
        "podcasts": [
            "Community Signal",
            "Reveal (community-impact reporting)",
            "99% Invisible",
            "WorkLife with Adam Grant"
        ],
        "communities": [
            "local neighborhood association networks",
            "AmeriCorps alumni networks"
        ],
        "real_world_examples": [
            "Neighbors organizing a food-security program during a local crisis",
            "A community land trust keeping housing affordable",
            "Youth volunteers running a free tutoring and mentorship program"
        ],
        "suggested_careers": [
            "Community Organizer",
            "Nonprofit Program Director",
            "Social Worker",
            "Neighborhood Planner",
            "Volunteer Coordinator"
        ],
        "projects": [
            "Organize a neighborhood clean-up or resource drive",
            "Start a peer-support or mentorship program",
            "Run a local fundraiser tied to a measurable community need",
            "Survey your community about its most urgent need"
        ],
        "volunteering_opportunities": [
            "Volunteer with a local community foundation",
            "Join a neighborhood mutual-aid network",
            "Help organize a community event"
        ],
        "research_areas": [
            "Community development",
            "Social capital and civic engagement",
            "Local economic development"
        ],
        "startup_ideas": [
            "A local mutual-aid coordination app",
            "A platform connecting volunteers to hyper-local needs",
            "A community resource directory for a specific neighborhood"
        ],
        "related_tags": [
            "community",
            "social work",
            "organizing",
            "neighborhood",
            "civic engagement",
            "volunteering"
        ]
    },
    {
        "id": "mission_advance_science",
        "name": "Advance Science",
        "description": "Pushing scientific understanding forward through rigorous research — designing experiments, testing hypotheses, and contributing real, verifiable knowledge to a field.",
        "famous_people": [
            "Marie Curie",
            "Charles Darwin",
            "Jennifer Doudna",
            "Chien-Shiung Wu"
        ],
        "organizations": [
            "National Science Foundation",
            "Royal Society",
            "Indian Institute of Science",
            "Skoll Foundation",
            "Clinton Foundation",
            "Wellcome Trust",
            "Robert Wood Johnson Foundation"
        ],
        "companies": [
            "DeepMind",
            "Illumina",
            "IKEA"
        ],
        "nonprofits": [
            "Howard Hughes Medical Institute",
            "Society for Science"
        ],
        "books": [
            "The Structure of Scientific Revolutions by Thomas Kuhn",
            "A Crack in Creation by Jennifer Doudna",
            "Longitude by Dava Sobel"
        ],
        "documentaries": [
            "Particle Fever",
            "The Man Who Knew Infinity (as inspiration)",
            "Picture a Scientist",
            "Blackfish"
        ],
        "podcasts": [
            "Science Vs",
            "Nature Podcast",
            "TED Talks Daily",
            "Freakonomics Radio"
        ],
        "communities": [
            "r/AskScience (Reddit)",
            "university research-lab networks"
        ],
        "real_world_examples": [
            "A small university lab's finding reshaping a field's understanding",
            "A collaborative open-science project accelerating vaccine research",
            "An undergraduate's research project published in a real journal"
        ],
        "suggested_careers": [
            "Research Scientist",
            "Laboratory Director",
            "Data Scientist",
            "Science Communicator",
            "Postdoctoral Researcher"
        ],
        "projects": [
            "Design and run a real experiment with a clear hypothesis",
            "Write up findings in a structured scientific format",
            "Enter a research-focused science fair or competition",
            "Assist with data analysis on an active research project"
        ],
        "volunteering_opportunities": [
            "Volunteer as a research assistant in a university lab",
            "Support a citizen-science data-collection project",
            "Help organize a school science fair"
        ],
        "research_areas": [
            "Whatever field genuinely interests you — biology, physics, chemistry, or the social sciences",
            "Reproducibility and open science",
            "Interdisciplinary research methods"
        ],
        "startup_ideas": [
            "A tool that helps researchers share and reproduce findings",
            "A citizen-science platform for a specific research question",
            "A lab-equipment-sharing service for under-resourced schools"
        ],
        "related_tags": [
            "science",
            "research",
            "experiment",
            "discovery",
            "academia",
            "data"
        ]
    },
    {
        "id": "mission_fight_poverty",
        "name": "Fight Poverty",
        "description": "Working to break cycles of poverty through direct aid, economic opportunity, and systemic change — from microfinance to policy reform to grassroots organizing.",
        "famous_people": [
            "Muhammad Yunus",
            "Esther Duflo",
            "Abhijit Banerjee",
            "Jacqueline Novogratz"
        ],
        "organizations": [
            "Grameen Bank",
            "GiveDirectly",
            "World Bank",
            "Ford Foundation",
            "Bill & Melinda Gates Foundation",
            "Rockefeller Foundation",
            "Open Society Foundations"
        ],
        "companies": [
            "Kiva",
            "Acumen",
            "LEGO Group"
        ],
        "nonprofits": [
            "BRAC",
            "Oxfam",
            "GiveDirectly"
        ],
        "books": [
            "Poor Economics by Abhijit Banerjee and Esther Duflo",
            "Banker to the Poor by Muhammad Yunus",
            "The Blue Sweater by Jacqueline Novogratz"
        ],
        "documentaries": [
            "Living on One Dollar",
            "Poverty, Inc.",
            "Inside Job (systemic angle)",
            "Cowspiracy"
        ],
        "podcasts": [
            "Freakonomics Radio (development episodes)",
            "Rethinking Poverty",
            "Planet Money",
            "Hidden Brain"
        ],
        "communities": [
            "r/development (Reddit)",
            "local anti-poverty coalition networks"
        ],
        "real_world_examples": [
            "A microfinance program helping small entrepreneurs build sustainable businesses",
            "A direct cash-transfer program measurably improving household outcomes",
            "A community-led savings group building financial resilience"
        ],
        "suggested_careers": [
            "Development Economist",
            "Microfinance Program Manager",
            "Policy Researcher",
            "Social Worker",
            "Impact Evaluation Specialist"
        ],
        "projects": [
            "Research a real poverty-reduction program's measured outcomes",
            "Organize a fundraiser tied to a specific, measurable intervention",
            "Volunteer with a program serving low-income families",
            "Design a small financial-literacy workshop"
        ],
        "volunteering_opportunities": [
            "Volunteer with a local anti-poverty or food-security program",
            "Support a microfinance or financial-inclusion initiative",
            "Tutor students from under-resourced schools"
        ],
        "research_areas": [
            "Randomized-controlled-trial development economics",
            "Microfinance and financial inclusion",
            "Social safety-net design"
        ],
        "startup_ideas": [
            "A savings or micro-lending app for underserved communities",
            "A skills-training platform connecting people to real jobs",
            "A tool that simplifies access to social-benefit programs"
        ],
        "related_tags": [
            "poverty",
            "development",
            "economics",
            "microfinance",
            "social impact",
            "inequality"
        ]
    },
    {
        "id": "mission_build_better_cities",
        "name": "Build Better Cities",
        "description": "Designing urban spaces, housing, and infrastructure that make cities more livable, equitable, and sustainable for everyone who calls them home.",
        "famous_people": [
            "Jane Jacobs",
            "Jan Gehl",
            "Janette Sadik-Khan"
        ],
        "organizations": [
            "Project for Public Spaces",
            "Urban Land Institute",
            "C40 Cities",
            "MacArthur Foundation",
            "Carnegie Endowment for International Peace",
            "Aspen Institute",
            "World Economic Forum"
        ],
        "companies": [
            "Gensler",
            "Arup",
            "Salesforce"
        ],
        "nonprofits": [
            "Strong Towns",
            "Local land trusts and housing nonprofits"
        ],
        "books": [
            "The Death and Life of Great American Cities by Jane Jacobs",
            "Cities for People by Jan Gehl",
            "Order Without Design by Alain Bertaud"
        ],
        "documentaries": [
            "Citizen Jane: Battle for the City",
            "Urbanized",
            "The Social Dilemma"
        ],
        "podcasts": [
            "The War on Cars",
            "Strong Towns Podcast",
            "The Ezra Klein Show",
            "Invisibilia"
        ],
        "communities": [
            "r/urbanplanning (Reddit)",
            "local YIMBY and urbanist meetup groups"
        ],
        "real_world_examples": [
            "A city converting a car-choked street into a pedestrian plaza",
            "A housing nonprofit developing affordable units near transit",
            "A community redesigning a park through participatory planning"
        ],
        "suggested_careers": [
            "Urban Planner",
            "Civil Engineer",
            "Transportation Planner",
            "Housing Policy Analyst",
            "Landscape Architect"
        ],
        "projects": [
            "Redesign a public space you use often, with a real proposal",
            "Map walkability or transit access in your neighborhood",
            "Attend a real city-planning meeting and give input",
            "Research a local housing-affordability issue"
        ],
        "volunteering_opportunities": [
            "Volunteer with a local housing or urbanist advocacy group",
            "Support a community park or public-space improvement project",
            "Join a local planning-commission public comment process"
        ],
        "research_areas": [
            "Transit-oriented development",
            "Affordable-housing policy",
            "Climate-resilient urban infrastructure"
        ],
        "startup_ideas": [
            "A tool helping residents track and comment on local development proposals",
            "A shared-mobility solution for underserved neighborhoods",
            "A platform matching vacant lots to community-garden projects"
        ],
        "related_tags": [
            "cities",
            "urban planning",
            "housing",
            "infrastructure",
            "architecture",
            "transportation"
        ]
    },
    {
        "id": "mission_improve_mental_health",
        "name": "Improve Mental Health",
        "description": "Helping people understand, manage, and heal from mental-health challenges — through clinical care, research, peer support, or destigmatizing conversation.",
        "famous_people": [
            "Brené Brown",
            "Viktor Frankl",
            "Bessel van der Kolk",
            "Simone Biles (public advocacy)"
        ],
        "organizations": [
            "World Health Organization (mental health division)",
            "National Alliance on Mental Illness (NAMI)",
            "Mental Health America",
            "TED",
            "Skoll Foundation",
            "Clinton Foundation",
            "Wellcome Trust"
        ],
        "companies": [
            "Headspace",
            "BetterHelp",
            "Calm",
            "Ben & Jerry's"
        ],
        "nonprofits": [
            "NAMI",
            "The Trevor Project",
            "Mental Health America"
        ],
        "books": [
            "The Body Keeps the Score by Bessel van der Kolk",
            "Man's Search for Meaning by Viktor Frankl",
            "Lost Connections by Johann Hari"
        ],
        "documentaries": [
            "Crazywise",
            "The Bipolar Bear Family (accessible mental-health storytelling)",
            "A Beautiful Mind (narrative case study)",
            "Living on One Dollar"
        ],
        "podcasts": [
            "The Hilarious World of Depression",
            "Therapy for Black Girls",
            "99% Invisible",
            "WorkLife with Adam Grant"
        ],
        "communities": [
            "r/mentalhealth (Reddit)",
            "local peer-support networks"
        ],
        "real_world_examples": [
            "A school introducing a peer-listening program that measurably reduced student distress",
            "A telehealth platform expanding therapy access to rural areas",
            "A workplace redesigning policies around burnout and mental health"
        ],
        "suggested_careers": [
            "Clinical Psychologist",
            "School Counselor",
            "Psychiatric Nurse",
            "Mental-Health Researcher",
            "Peer Support Specialist"
        ],
        "projects": [
            "Start a peer-support or mental-health-awareness initiative at school",
            "Research a real mental-health intervention's effectiveness",
            "Design a stress-management workshop for peers",
            "Volunteer with a crisis-support hotline (with appropriate training)"
        ],
        "volunteering_opportunities": [
            "Volunteer with a mental-health awareness nonprofit",
            "Train as a peer listener or crisis-line volunteer",
            "Support a school-based mental-health program"
        ],
        "research_areas": [
            "Trauma-informed care",
            "Adolescent mental health",
            "Digital mental-health interventions"
        ],
        "startup_ideas": [
            "A peer-support app for a specific underserved group",
            "A stress-management tool tailored for students",
            "A platform simplifying access to affordable therapy"
        ],
        "related_tags": [
            "mental health",
            "psychology",
            "wellbeing",
            "counseling",
            "therapy",
            "wellness"
        ]
    },
    {
        "id": "mission_design_better_products",
        "name": "Design Better Products",
        "description": "Making everyday products and experiences genuinely easier, safer, and more delightful to use, through careful research, iteration, and craft.",
        "famous_people": [
            "Dieter Rams",
            "Jony Ive",
            "Don Norman"
        ],
        "organizations": [
            "IDEO",
            "Industrial Designers Society of America",
            "Robert Wood Johnson Foundation",
            "Ford Foundation",
            "Bill & Melinda Gates Foundation",
            "Rockefeller Foundation"
        ],
        "companies": [
            "Apple",
            "Figma",
            "Frog Design",
            "Patagonia"
        ],
        "nonprofits": [
            "Design for America"
        ],
        "books": [
            "The Design of Everyday Things by Don Norman",
            "Change by Design by Tim Brown",
            "Hooked by Nir Eyal"
        ],
        "documentaries": [
            "Objectified",
            "Abstract: The Art of Design",
            "Icarus"
        ],
        "podcasts": [
            "Design Matters with Debbie Millman",
            "NN/g UX Podcast",
            "TED Talks Daily",
            "Freakonomics Radio"
        ],
        "communities": [
            "r/UXDesign (Reddit)",
            "Designer Hangout community"
        ],
        "real_world_examples": [
            "A redesigned hospital form that cut patient errors significantly",
            "A product team iterating a checkout flow to reduce user frustration",
            "A physical product redesigned for one-handed accessibility"
        ],
        "suggested_careers": [
            "UX/UI Designer",
            "Industrial Designer",
            "Product Manager",
            "Design Researcher",
            "Service Designer"
        ],
        "projects": [
            "Redesign a poorly-designed everyday product or app screen",
            "Run a 5-user usability test on something real",
            "Build and test a physical or digital prototype",
            "Interview five real users about a genuine pain point"
        ],
        "volunteering_opportunities": [
            "Volunteer design skills for a nonprofit's product or materials",
            "Mentor a beginner in a design community",
            "Support an accessibility-focused design project"
        ],
        "research_areas": [
            "Human-centered design methods",
            "Accessibility and inclusive design",
            "Behavioral design"
        ],
        "startup_ideas": [
            "A redesigned version of a frustrating everyday tool",
            "An accessibility-focused product for an underserved group",
            "A design-consulting service for small local businesses"
        ],
        "related_tags": [
            "design",
            "product",
            "ux",
            "usability",
            "innovation",
            "prototyping"
        ]
    },
    {
        "id": "mission_protect_wildlife",
        "name": "Protect Wildlife",
        "description": "Working to conserve endangered species and the habitats they depend on — through fieldwork, research, anti-poaching efforts, or wildlife-focused advocacy.",
        "famous_people": [
            "Jane Goodall",
            "Dian Fossey",
            "Steve Irwin",
            "Jack Hanna"
        ],
        "organizations": [
            "World Wildlife Fund",
            "Wildlife Conservation Society",
            "Jane Goodall Institute",
            "Open Society Foundations",
            "MacArthur Foundation",
            "Carnegie Endowment for International Peace",
            "Aspen Institute"
        ],
        "companies": [
            "Panthera (wild cat conservation, nonprofit-adjacent)",
            "LEGO Group",
            "Salesforce"
        ],
        "nonprofits": [
            "World Wildlife Fund",
            "Wildlife Conservation Society",
            "African Wildlife Foundation"
        ],
        "books": [
            "In the Shadow of Man by Jane Goodall",
            "The Sixth Extinction by Elizabeth Kolbert",
            "Gorillas in the Mist by Dian Fossey"
        ],
        "documentaries": [
            "Virunga",
            "The Ivory Game",
            "My Octopus Teacher",
            "Won't You Be My Neighbor?"
        ],
        "podcasts": [
            "Nature Podcast",
            "The Wild",
            "Planet Money",
            "Hidden Brain"
        ],
        "communities": [
            "r/conservation (Reddit)",
            "local wildlife-rehabilitation volunteer networks"
        ],
        "real_world_examples": [
            "A ranger program cutting poaching rates through community partnership",
            "A wildlife corridor reconnecting fragmented habitats",
            "Citizen-science tracking helping protect a migratory species"
        ],
        "suggested_careers": [
            "Wildlife Biologist",
            "Conservation Officer",
            "Wildlife Veterinarian",
            "Field Researcher",
            "Environmental Educator"
        ],
        "projects": [
            "Volunteer at a wildlife rehabilitation center",
            "Run a citizen-science species-monitoring project locally",
            "Research an endangered species' conservation status and propose action",
            "Build a habitat feature for local wildlife (bird boxes, pollinator garden)"
        ],
        "volunteering_opportunities": [
            "Volunteer with a wildlife rehabilitation or sanctuary program",
            "Support a local habitat-restoration project",
            "Join a citizen-science wildlife tracking initiative"
        ],
        "research_areas": [
            "Conservation genetics",
            "Human-wildlife conflict mitigation",
            "Habitat connectivity"
        ],
        "startup_ideas": [
            "A citizen-science wildlife-tracking app",
            "A tool helping farmers reduce human-wildlife conflict sustainably",
            "An eco-tourism platform that directly funds conservation"
        ],
        "related_tags": [
            "wildlife",
            "conservation",
            "biodiversity",
            "ecology",
            "nature",
            "animals"
        ]
    },
    {
        "id": "mission_improve_agriculture",
        "name": "Improve Agriculture",
        "description": "Making food systems more productive, sustainable, and resilient — through agronomy, agricultural engineering, or food-supply-chain innovation.",
        "famous_people": [
            "Norman Borlaug",
            "M.S. Swaminathan",
            "Wangari Maathai"
        ],
        "organizations": [
            "Food and Agriculture Organization (FAO)",
            "CGIAR",
            "International Rice Research Institute",
            "World Economic Forum",
            "TED",
            "Skoll Foundation",
            "Clinton Foundation"
        ],
        "companies": [
            "John Deere",
            "Indigo Agriculture",
            "Corteva Agriscience",
            "Unilever"
        ],
        "nonprofits": [
            "Heifer International",
            "One Acre Fund"
        ],
        "books": [
            "The Omnivore's Dilemma by Michael Pollan",
            "The Third Plate by Dan Barber",
            "Farmageddon by Philip Lymbery"
        ],
        "documentaries": [
            "Kiss the Ground",
            "Food, Inc.",
            "The Biggest Little Farm",
            "RBG"
        ],
        "podcasts": [
            "The Furrow",
            "Farm to Table Talk",
            "The Ezra Klein Show",
            "Invisibilia"
        ],
        "communities": [
            "r/farming (Reddit)",
            "Future Farmers of America (FFA)"
        ],
        "real_world_examples": [
            "Precision-agriculture sensors cutting a farm's water use significantly",
            "A smallholder cooperative improving yields through shared knowledge",
            "A drought-resistant crop variety improving food security in a region"
        ],
        "suggested_careers": [
            "Agronomist",
            "Agricultural Engineer",
            "Food Scientist",
            "Precision Agriculture Technologist",
            "Supply-Chain Analyst"
        ],
        "projects": [
            "Start a school or home garden with data tracking",
            "Test soil samples from different locations and compare results",
            "Research a local food-supply chain's inefficiencies",
            "Build a simple automated irrigation or monitoring system"
        ],
        "volunteering_opportunities": [
            "Volunteer at a community farm or garden",
            "Support a local food-security or gleaning program",
            "Assist a university agricultural-extension project"
        ],
        "research_areas": [
            "Precision agriculture",
            "Crop genetics",
            "Sustainable soil management"
        ],
        "startup_ideas": [
            "A low-cost soil-sensor kit for smallholder farmers",
            "A marketplace connecting small farms directly to local buyers",
            "A food-waste-reduction tool for the supply chain"
        ],
        "related_tags": [
            "agriculture",
            "farming",
            "food systems",
            "sustainability",
            "agritech",
            "crops"
        ]
    },
    {
        "id": "mission_preserve_culture_and_heritage",
        "name": "Preserve Culture and Heritage",
        "description": "Protecting languages, traditions, historical sites, and cultural knowledge from being lost — through documentation, education, and active community practice.",
        "famous_people": [
            "UNESCO World Heritage advocates broadly",
            "Wole Soyinka",
            "Toni Morrison"
        ],
        "organizations": [
            "UNESCO World Heritage Centre",
            "Endangered Languages Project",
            "Smithsonian Institution",
            "Wellcome Trust",
            "Robert Wood Johnson Foundation",
            "Ford Foundation",
            "Bill & Melinda Gates Foundation"
        ],
        "companies": [
            "Google Arts & Culture",
            "Danone",
            "Unilever"
        ],
        "nonprofits": [
            "World Monuments Fund",
            "Living Tongues Institute for Endangered Languages"
        ],
        "books": [
            "Braiding Sweetgrass by Robin Wall Kimmerer",
            "The Storyteller by Mario Vargas Llosa",
            "When a Language Dies by K. David Harrison"
        ],
        "documentaries": [
            "The Linguists",
            "Rivers and Tides",
            "Free Solo (heritage-adjacent stewardship theme)",
            "The True Cost"
        ],
        "podcasts": [
            "99% Invisible (heritage/design episodes)",
            "Endangered Languages podcast series",
            "99% Invisible",
            "WorkLife with Adam Grant"
        ],
        "communities": [
            "r/linguistics (Reddit)",
            "local cultural-heritage preservation societies"
        ],
        "real_world_examples": [
            "A community documenting an endangered language before its last fluent speakers pass",
            "A historical restoration project preserving a threatened landmark",
            "A digital archive making traditional knowledge accessible to younger generations"
        ],
        "suggested_careers": [
            "Museum Curator",
            "Archivist",
            "Documentary Linguist",
            "Historic Preservationist",
            "Cultural Program Director"
        ],
        "projects": [
            "Interview an elder in your community and document their story",
            "Research and document a local historical site",
            "Build a small digital archive of a cultural tradition",
            "Organize a cultural-heritage awareness event"
        ],
        "volunteering_opportunities": [
            "Volunteer with a local historical society or museum",
            "Support a language-documentation project",
            "Help digitize community oral histories"
        ],
        "research_areas": [
            "Documentary linguistics",
            "Historic preservation methods",
            "Digital archiving"
        ],
        "startup_ideas": [
            "A platform for recording and preserving family or community oral histories",
            "A language-learning app for an endangered language",
            "A tool helping museums digitize and share collections"
        ],
        "related_tags": [
            "culture",
            "heritage",
            "history",
            "language",
            "preservation",
            "tradition"
        ]
    },
    {
        "id": "mission_advance_human_rights",
        "name": "Advance Human Rights",
        "description": "Working to protect fundamental freedoms and dignity for people everywhere — through legal advocacy, investigative research, or grassroots organizing.",
        "famous_people": [
            "Malala Yousafzai",
            "Nelson Mandela",
            "Eleanor Roosevelt",
            "Bryan Stevenson"
        ],
        "organizations": [
            "Amnesty International",
            "Human Rights Watch",
            "United Nations Human Rights Office",
            "Rockefeller Foundation",
            "Open Society Foundations",
            "MacArthur Foundation",
            "Carnegie Endowment for International Peace"
        ],
        "companies": [
            "IKEA",
            "LEGO Group"
        ],
        "nonprofits": [
            "Amnesty International",
            "Human Rights Watch",
            "Equal Justice Initiative"
        ],
        "books": [
            "Just Mercy by Bryan Stevenson",
            "Evicted by Matthew Desmond",
            "I Am Malala by Malala Yousafzai"
        ],
        "documentaries": [
            "13th",
            "The Act of Killing",
            "He Named Me Malala",
            "Blackfish"
        ],
        "podcasts": [
            "Rights & Wrongs",
            "The Global Human Rights Podcast",
            "TED Talks Daily",
            "Freakonomics Radio"
        ],
        "communities": [
            "r/humanrights (Reddit)",
            "local Amnesty International student chapters"
        ],
        "real_world_examples": [
            "A legal-aid clinic winning wrongful-conviction exonerations",
            "An advocacy campaign leading to real policy reform",
            "A grassroots movement securing labor protections for a vulnerable group"
        ],
        "suggested_careers": [
            "Human Rights Lawyer",
            "Policy Researcher",
            "Investigative Journalist",
            "Advocacy Campaign Manager",
            "Legal Aid Attorney"
        ],
        "projects": [
            "Research a real human-rights issue and present findings",
            "Organize an awareness campaign on a specific rights issue",
            "Volunteer at a legal-aid or advocacy organization",
            "Write to a policymaker about a documented rights concern"
        ],
        "volunteering_opportunities": [
            "Volunteer with a legal-aid clinic",
            "Join a local human-rights advocacy chapter",
            "Support a refugee or immigrant-rights organization"
        ],
        "research_areas": [
            "International human-rights law",
            "Access-to-justice research",
            "Civil-rights history"
        ],
        "startup_ideas": [
            "A tool helping people document and report rights violations safely",
            "A platform simplifying access to legal-aid resources",
            "A civic-education app on human rights for young people"
        ],
        "related_tags": [
            "human rights",
            "justice",
            "advocacy",
            "law",
            "equality",
            "civil rights"
        ]
    },
    {
        "id": "mission_improve_financial_literacy",
        "name": "Improve Financial Literacy",
        "description": "Helping people build real financial confidence and security — through education, accessible tools, and honest guidance on budgeting, saving, and investing.",
        "famous_people": [
            "Suze Orman",
            "Dave Ramsey",
            "Elizabeth Warren (consumer-finance advocacy)"
        ],
        "organizations": [
            "Jump$tart Coalition for Personal Financial Literacy",
            "National Endowment for Financial Education",
            "Aspen Institute",
            "World Economic Forum",
            "TED",
            "Skoll Foundation"
        ],
        "companies": [
            "Vanguard",
            "Zerodha (investor education initiatives)",
            "Salesforce"
        ],
        "nonprofits": [
            "Operation HOPE",
            "Junior Achievement"
        ],
        "books": [
            "The Intelligent Investor by Benjamin Graham",
            "I Will Teach You to Be Rich by Ramit Sethi",
            "Your Money or Your Life by Vicki Robin"
        ],
        "documentaries": [
            "Broke, Busted & Disgusted",
            "Maxed Out",
            "Cowspiracy"
        ],
        "podcasts": [
            "The Ramsey Show",
            "ChooseFI",
            "Planet Money",
            "Hidden Brain"
        ],
        "communities": [
            "r/personalfinance (Reddit)",
            "Junior Achievement student programs"
        ],
        "real_world_examples": [
            "A community workshop helping first-time earners build a real budget",
            "A school program teaching students to manage a simulated portfolio",
            "A nonprofit helping low-income families access banking services"
        ],
        "suggested_careers": [
            "Financial Educator",
            "Financial Planner",
            "Consumer-Finance Policy Analyst",
            "Community Banking Officer",
            "Personal Finance Content Creator"
        ],
        "projects": [
            "Build a personal budget tracker and use it for a real month",
            "Teach a basic financial-literacy workshop to peers",
            "Run a stock-market simulation portfolio",
            "Research predatory lending practices in your community"
        ],
        "volunteering_opportunities": [
            "Volunteer with a financial-literacy nonprofit",
            "Tutor peers on budgeting basics",
            "Support a community banking-access initiative"
        ],
        "research_areas": [
            "Behavioral finance",
            "Financial-inclusion policy",
            "Consumer-protection regulation"
        ],
        "startup_ideas": [
            "A budgeting app tailored for first-time earners",
            "A financial-literacy curriculum for underserved schools",
            "A tool simplifying access to fair banking for the unbanked"
        ],
        "related_tags": [
            "finance",
            "financial literacy",
            "money",
            "budgeting",
            "investing",
            "economics"
        ]
    }
]


async def seed() -> None:
    client = get_supabase_client()
    missions = [LifeMission.model_validate(m) for m in MISSIONS]

    def _upsert() -> None:
        client.table("life_missions").upsert([m.model_dump(mode="json") for m in missions]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(missions)} life missions.")


if __name__ == "__main__":
    asyncio.run(seed())

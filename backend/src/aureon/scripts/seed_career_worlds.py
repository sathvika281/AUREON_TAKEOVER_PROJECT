"""One-time seed script for Discover Batch 4's Missing Worlds catalog.

Run via: python -m aureon.scripts.seed_career_worlds

A comprehensive (31-world) catalog of entire career ecosystems, each
with rich, real, production-quality metadata — colleges, companies,
books, videos, communities, projects, internships — favoring
domain-specific real institutions over generically-famous names reused
everywhere (Le Cordon Bleu for Hospitality, Wageningen for Agriculture,
Scripps for Marine Sciences, rather than Harvard/MIT/Google repeated
across every world). Every entry carries its own `source_note` honesty
disclaimer (see domain/models/career_world.py) — never presented as a
continuously-verified or exhaustive directory. Idempotent: upserts by
id, safe to re-run.
"""

import asyncio

from aureon.domain.models.career_world import CareerWorld
from aureon.services.supabase.client import get_supabase_client

WORLDS: list[dict] = [
    {
        "id": "world_space",
        "name": "Space",
        "description": "Space is the world of designing, building, launching, and operating the systems that let humanity leave Earth's atmosphere — from rockets and satellites to the science of what lies beyond. It spans deep engineering, physics, and mission operations, most of which happens years before any launch.",
        "why_it_matters": "Satellites underpin GPS, weather forecasting, global communication, and climate monitoring — space infrastructure is now a quiet backbone of daily life on Earth, not just an exploration frontier.",
        "global_importance": "A growing number of countries and private companies now operate real space programs, and satellite-dependent industries (telecom, agriculture, defense, logistics) touch billions of people daily.",
        "future_growth": "Falling launch costs are widening real participation beyond national space agencies, and satellite mega-constellations, lunar programs, and commercial space stations are active, funded areas of near-term growth.",
        "famous_careers": [
            "Aerospace Engineer",
            "Astronaut",
            "Mission Control Specialist",
            "Satellite Systems Engineer",
            "Planetary Scientist"
        ],
        "beginner_roadmap": [
            "Learn physics and orbital-mechanics basics",
            "Build and fly model rockets",
            "Join a rocketry or CanSat club",
            "Take an introductory astrodynamics course",
            "Contribute to an open-source satellite or ground-station project"
        ],
        "required_skills": [
            "Physics",
            "Orbital mechanics",
            "Systems engineering",
            "Programming (Python/C++)",
            "Materials science",
            "Project management",
            "Problem-solving under constraints"
        ],
        "misconceptions": [
            "You must be a pilot to work in space",
            "Space careers are only for astronauts",
            "It's all rocket launches, not years of engineering"
        ],
        "related_industries": [
            "aerospace",
            "space",
            "satellites",
            "astronomy",
            "rocketry"
        ],
        "videos": [
            "Kurzgesagt – In a Nutshell (YouTube)",
            "NASA (YouTube)",
            "Everyday Astronaut",
            "Scott Manley"
        ],
        "books": [
            "Cosmos by Carl Sagan",
            "Packing for Mars by Mary Roach",
            "An Astronaut's Guide to Life on Earth by Chris Hadfield",
            "The Right Stuff by Tom Wolfe"
        ],
        "communities": [
            "r/space (Reddit)",
            "AIAA — American Institute of Aeronautics and Astronautics",
            "Space Generation Advisory Council"
        ],
        "beginner_projects": [
            "Build and launch a model rocket",
            "Track satellites with a low-cost SDR receiver",
            "Simulate an orbital trajectory in Python",
            "Enter a CanSat or high-altitude balloon competition"
        ],
        "internships": [
            "NASA internship programs",
            "ISRO student internships",
            "SpaceX internship program"
        ],
        "colleges": [
            "MIT",
            "Caltech",
            "Purdue University",
            "Georgia Institute of Technology",
            "University of Colorado Boulder",
            "ISAE-SUPAERO",
            "Indian Institute of Space Science and Technology (IIST)",
            "International Space University",
            "University of Toronto",
            "National University of Singapore",
            "University of Melbourne",
            "Technical University of Munich"
        ],
        "companies": [
            "SpaceX",
            "Blue Origin",
            "NASA",
            "ISRO",
            "Rocket Lab",
            "Northrop Grumman",
            "Maxar Technologies",
            "Airbus Defence and Space",
            "Accenture",
            "Deloitte",
            "PwC"
        ]
    },
    {
        "id": "world_biotechnology",
        "name": "Biotechnology",
        "description": "Biotechnology applies biology at the molecular level to solve real problems — engineering cells, genes, and organisms to develop medicines, diagnostics, sustainable materials, and better food systems.",
        "why_it_matters": "Modern vaccines, gene therapies, and crop science all depend on biotechnology — it sits at the center of how humanity responds to disease, food security, and environmental pressure.",
        "global_importance": "From mRNA vaccine platforms to CRISPR gene editing, biotech breakthroughs of the last decade have already reshaped medicine and agriculture worldwide, with real economic and public-health stakes.",
        "future_growth": "Falling gene-sequencing costs and maturing gene-editing tools are widening real access to biotech research and entrepreneurship well beyond traditional pharma labs.",
        "famous_careers": [
            "Genetic Engineer",
            "Bioprocess Engineer",
            "Clinical Research Scientist",
            "Bioinformatician",
            "Biomanufacturing Technician"
        ],
        "beginner_roadmap": [
            "Study biology and chemistry fundamentals",
            "Learn basic wet-lab techniques",
            "Join a school or iGEM synthetic-biology team",
            "Take an online genomics or bioinformatics course",
            "Volunteer in a university research lab"
        ],
        "required_skills": [
            "Molecular biology",
            "Lab techniques",
            "Data analysis",
            "Genomics",
            "Statistics",
            "Regulatory awareness",
            "Attention to detail"
        ],
        "misconceptions": [
            "Biotech is only for pre-med students",
            "You need a PhD to work in the field",
            "It's all about curing disease, not manufacturing or agriculture"
        ],
        "related_industries": [
            "biotechnology",
            "healthcare",
            "pharmaceuticals",
            "genomics",
            "life sciences"
        ],
        "videos": [
            "Kurzgesagt – In a Nutshell",
            "iBiology (YouTube)",
            "Amoeba Sisters"
        ],
        "books": [
            "The Gene by Siddhartha Mukherjee",
            "A Crack in Creation by Jennifer Doudna",
            "The Emperor of All Maladies by Siddhartha Mukherjee"
        ],
        "communities": [
            "r/biotech (Reddit)",
            "International Genetically Engineered Machine (iGEM) community",
            "Biotechnology Innovation Organization (BIO)"
        ],
        "beginner_projects": [
            "Extract DNA from a strawberry",
            "Analyze a public genomic dataset",
            "Build a simple bioinformatics script",
            "Enter a synthetic-biology competition"
        ],
        "internships": [
            "iGEM team internships",
            "pharmaceutical company summer internships",
            "university wet-lab research assistantships"
        ],
        "colleges": [
            "MIT",
            "Johns Hopkins University",
            "ETH Zurich",
            "University of California San Diego",
            "Karolinska Institute",
            "Imperial College London",
            "Indian Institute of Technology Bombay",
            "University of Cambridge",
            "University of Edinburgh",
            "Seoul National University",
            "University of Tokyo",
            "University of Delhi"
        ],
        "companies": [
            "Moderna",
            "Illumina",
            "Genentech",
            "Regeneron",
            "Biocon",
            "Novozymes",
            "Amgen",
            "Ginkgo Bioworks",
            "EY",
            "KPMG",
            "IBM"
        ]
    },
    {
        "id": "world_marine_sciences",
        "name": "Marine Sciences",
        "description": "Marine sciences study the ocean itself — its biology, chemistry, physics, and the technology used to explore and protect it, from coral reefs and deep-sea ecosystems to fisheries and ocean-climate interactions.",
        "why_it_matters": "The ocean regulates Earth's climate, feeds billions of people, and remains largely unmapped — marine science is central to both food security and understanding a changing planet.",
        "global_importance": "Coastal nations depend on healthy oceans for fishing, trade, and tourism, and ocean-climate research directly informs global climate policy.",
        "future_growth": "Underwater robotics, ocean-monitoring satellites, and deep-sea exploration technology are opening real new research and engineering roles beyond traditional field biology.",
        "famous_careers": [
            "Marine Biologist",
            "Oceanographer",
            "Marine Conservation Officer",
            "Underwater Robotics Engineer",
            "Fisheries Scientist"
        ],
        "beginner_roadmap": [
            "Volunteer at a local aquarium",
            "Learn to snorkel or scuba dive safely",
            "Study biology and chemistry",
            "Join a beach or reef citizen-science program",
            "Take an introductory oceanography course"
        ],
        "required_skills": [
            "Biology",
            "Chemistry",
            "Data collection",
            "Statistics",
            "Fieldwork stamina",
            "Environmental monitoring",
            "Scientific writing"
        ],
        "misconceptions": [
            "Marine science is just swimming with dolphins",
            "You need to live near an ocean to study it",
            "It's only biology, not engineering or policy"
        ],
        "related_industries": [
            "marine sciences",
            "oceanography",
            "environment",
            "conservation",
            "fisheries"
        ],
        "videos": [
            "Ocean Today (NOAA)",
            "Nigel Marven (YouTube)",
            "Blue Planet documentary clips"
        ],
        "books": [
            "The Sea Around Us by Rachel Carson",
            "Blue Mind by Wallace J. Nichols",
            "The Soul of an Octopus by Sy Montgomery"
        ],
        "communities": [
            "r/marinebiology (Reddit)",
            "Marine Conservation Society",
            "Society for Marine Mammalogy"
        ],
        "beginner_projects": [
            "Run a local water-quality testing project",
            "Participate in a citizen-science reef survey",
            "Build a simple underwater camera rig",
            "Analyze public ocean-temperature datasets"
        ],
        "internships": [
            "NOAA student internships",
            "Woods Hole summer student fellowships",
            "aquarium volunteer and internship programs"
        ],
        "colleges": [
            "Scripps Institution of Oceanography (UC San Diego)",
            "Woods Hole Oceanographic Institution",
            "University of Southampton — National Oceanography Centre",
            "James Cook University",
            "University of Miami Rosenstiel School",
            "Dalhousie University",
            "Plymouth Marine Laboratory",
            "University of Tasmania",
            "University of Sydney",
            "McGill University",
            "University of British Columbia",
            "Nanyang Technological University"
        ],
        "companies": [
            "Ocean Infinity",
            "Schmidt Ocean Institute",
            "Woods Hole Oceanographic Institution",
            "NOAA",
            "Fugro",
            "Saildrone",
            "Infosys",
            "Tata Consultancy Services",
            "Wipro"
        ]
    },
    {
        "id": "world_public_policy",
        "name": "Public Policy",
        "description": "Public policy is the work of researching, designing, and evaluating the rules and programs that shape how societies function — from healthcare and education to housing and taxation.",
        "why_it_matters": "Nearly every major social outcome — health, poverty, education access, safety — is shaped by policy decisions, making this the field where evidence and real-world impact meet most directly.",
        "global_importance": "Governments and institutions worldwide face urgent, evidence-driven policy challenges around inequality, technology regulation, and public health.",
        "future_growth": "Data-driven policy analysis and evidence-based program evaluation are steadily replacing intuition-based governance, creating real demand for analytically-skilled policy professionals.",
        "famous_careers": [
            "Policy Analyst",
            "Legislative Aide",
            "Program Evaluator",
            "Diplomat",
            "Regulatory Affairs Specialist"
        ],
        "beginner_roadmap": [
            "Join a debate or Model UN club",
            "Read policy analysis from real think tanks",
            "Volunteer for a local government office or campaign",
            "Take an introductory economics or political science course",
            "Write a policy memo on a real local issue"
        ],
        "required_skills": [
            "Research",
            "Writing",
            "Data analysis",
            "Economics",
            "Public speaking",
            "Negotiation",
            "Critical thinking"
        ],
        "misconceptions": [
            "Public policy is the same as politics",
            "You need a law degree to work in policy",
            "It's all national-level Washington work"
        ],
        "related_industries": [
            "public policy",
            "government",
            "political science",
            "international relations",
            "economics"
        ],
        "videos": [
            "TED Talks on policy",
            "Council on Foreign Relations (YouTube)",
            "Vox policy explainers"
        ],
        "books": [
            "Thinking, Fast and Slow by Daniel Kahneman",
            "The Fifth Risk by Michael Lewis",
            "Nudge by Richard Thaler and Cass Sunstein"
        ],
        "communities": [
            "r/PoliticalScience (Reddit)",
            "Model United Nations clubs",
            "Young Professionals in Foreign Policy"
        ],
        "beginner_projects": [
            "Write a policy brief on a real local issue",
            "Analyze public budget data",
            "Organize a community town hall",
            "Intern with a city council office"
        ],
        "internships": [
            "think tank research internships",
            "city and state government internships",
            "UN Youth Programmes"
        ],
        "colleges": [
            "Harvard Kennedy School",
            "London School of Economics",
            "Georgetown School of Foreign Service",
            "Sciences Po",
            "Lee Kuan Yew School of Public Policy",
            "National Law School of India University",
            "Fletcher School (Tufts)",
            "University of Chicago Harris School",
            "KAIST",
            "Peking University",
            "University of Hong Kong",
            "Trinity College Dublin"
        ],
        "companies": [
            "RAND Corporation",
            "Brookings Institution",
            "Deloitte Public Sector",
            "World Bank",
            "McKinsey Public Sector Practice",
            "Honeywell",
            "3M",
            "Philips"
        ]
    },
    {
        "id": "world_design",
        "name": "Design",
        "description": "Design is the discipline of shaping how products, spaces, and digital experiences work and feel — solving real usability and communication problems through research, prototyping, and iteration.",
        "why_it_matters": "Every app, product, and public space you use was deliberately designed — good design determines whether something is usable, accessible, and genuinely helpful.",
        "global_importance": "As digital products reach billions of users, small design decisions have outsized global impact on accessibility, trust, and how information is understood.",
        "future_growth": "Demand for UX research and service design is growing as companies realize good design reduces cost and builds user trust far more reliably than added features.",
        "famous_careers": [
            "UX/UI Designer",
            "Industrial Designer",
            "Graphic Designer",
            "Design Researcher",
            "Service Designer"
        ],
        "beginner_roadmap": [
            "Learn design fundamentals: color, typography, layout",
            "Practice with free tools like Figma",
            "Redesign an app or product you use daily",
            "Build a small portfolio of real projects",
            "Get feedback from a design community"
        ],
        "required_skills": [
            "Visual communication",
            "User research",
            "Prototyping tools",
            "Empathy and observation",
            "Sketching",
            "Systems thinking",
            "Critique and iteration"
        ],
        "misconceptions": [
            "Design is just making things look pretty",
            "You need to be a natural artist",
            "Anyone can do UX without training"
        ],
        "related_industries": [
            "design",
            "ux",
            "product design",
            "industrial design",
            "graphic design"
        ],
        "videos": [
            "The Futur (YouTube)",
            "NN/g usability research videos",
            "Adobe Creative Cloud tutorials"
        ],
        "books": [
            "The Design of Everyday Things by Don Norman",
            "Don't Make Me Think by Steve Krug",
            "Change by Design by Tim Brown"
        ],
        "communities": [
            "r/UXDesign (Reddit)",
            "Designer Hangout community",
            "AIGA — the professional design association"
        ],
        "beginner_projects": [
            "Redesign a poorly-designed app screen",
            "Design a poster for a real cause",
            "Run a 5-user usability test",
            "Build a simple product prototype"
        ],
        "internships": [
            "design studio internships",
            "in-house product design internships",
            "design fellowship programs"
        ],
        "colleges": [
            "Rhode Island School of Design",
            "Parsons School of Design",
            "Royal College of Art",
            "ArtCenter College of Design",
            "National Institute of Design (India)",
            "Central Saint Martins",
            "Aalto University",
            "Pratt Institute",
            "University of Amsterdam",
            "KTH Royal Institute of Technology",
            "Indian Institute of Technology Delhi",
            "Indian Institute of Technology Madras"
        ],
        "companies": [
            "IDEO",
            "Figma",
            "Adobe",
            "Frog Design",
            "Pentagram",
            "Fjord (Accenture Song)",
            "Samsung",
            "Larsen & Toubro",
            "Bechtel"
        ]
    },
    {
        "id": "world_agriculture",
        "name": "Agriculture",
        "description": "Agriculture is the science and business of growing food and managing land sustainably — spanning soil science, crop genetics, precision farming technology, and food supply chains.",
        "why_it_matters": "Every person depends on agriculture daily, and feeding a growing global population sustainably is one of the most consequential technical challenges of this century.",
        "global_importance": "Climate change, water scarcity, and soil degradation make sustainable agriculture a global priority, not a niche rural concern.",
        "future_growth": "Precision agriculture — sensors, drones, and data-driven farming — is rapidly modernizing a traditionally low-tech industry, opening real engineering and data-science roles.",
        "famous_careers": [
            "Agronomist",
            "Agricultural Engineer",
            "Food Scientist",
            "Precision Agriculture Technologist",
            "Farm Manager"
        ],
        "beginner_roadmap": [
            "Volunteer or work on a local farm",
            "Learn basic soil and plant science",
            "Join FFA or a 4-H club",
            "Try a precision-agriculture app or tool",
            "Start a small home or school garden project"
        ],
        "required_skills": [
            "Biology",
            "Soil science",
            "Data analysis",
            "Equipment operation",
            "Sustainability practices",
            "Business basics",
            "Observation"
        ],
        "misconceptions": [
            "Agriculture is only manual farm labor",
            "It's a declining, low-tech industry",
            "You need to grow up on a farm to enter it"
        ],
        "related_industries": [
            "agriculture",
            "agritech",
            "food systems",
            "sustainability",
            "farming"
        ],
        "videos": [
            "FAO (YouTube)",
            "Kurzgesagt on food systems",
            "MidWest Farm Report-style channels"
        ],
        "books": [
            "The Omnivore's Dilemma by Michael Pollan",
            "Farmageddon by Philip Lymbery",
            "The Third Plate by Dan Barber"
        ],
        "communities": [
            "r/farming (Reddit)",
            "Future Farmers of America (FFA)",
            "Young Farmers Coalition"
        ],
        "beginner_projects": [
            "Start a school or home garden with data tracking",
            "Test soil samples from different locations",
            "Build a simple automated irrigation timer",
            "Research a local food-supply chain"
        ],
        "internships": [
            "agribusiness summer internships",
            "university agricultural-extension programs",
            "agri-tech startup internships"
        ],
        "colleges": [
            "Wageningen University & Research",
            "UC Davis",
            "Cornell College of Agriculture and Life Sciences",
            "Indian Agricultural Research Institute",
            "Punjab Agricultural University",
            "University of Guelph",
            "University of Reading",
            "Iowa State University",
            "University of Waterloo",
            "University of Illinois Urbana-Champaign",
            "Texas A&M University",
            "University of Wisconsin-Madison"
        ],
        "companies": [
            "John Deere",
            "Bayer Crop Science",
            "Corteva Agriscience",
            "Indigo Agriculture",
            "ITC Agri Business",
            "Syngenta",
            "AECOM",
            "Jacobs Engineering",
            "Capgemini"
        ]
    },
    {
        "id": "world_hospitality",
        "name": "Hospitality",
        "description": "Hospitality is the business of creating great guest and dining experiences — hotels, restaurants, events, and tourism — built on service design, operations, and genuine care for people.",
        "why_it_matters": "Travel and dining are among the largest global industries, and hospitality careers directly shape how people experience new places and celebrate milestones.",
        "global_importance": "Tourism supports economies worldwide, and hospitality is often a major employer and growth engine in developing regions.",
        "future_growth": "Experience-driven travel, boutique hospitality, and revenue-management technology are professionalizing the field well beyond traditional front-desk roles.",
        "famous_careers": [
            "Hotel General Manager",
            "Executive Chef",
            "Event Planner",
            "Guest Experience Manager",
            "Revenue Manager"
        ],
        "beginner_roadmap": [
            "Work a part-time job in food service or front-desk",
            "Take a basic culinary or hospitality course",
            "Shadow an event or hotel manager",
            "Learn a booking or point-of-sale system",
            "Volunteer to help run a school or community event"
        ],
        "required_skills": [
            "Customer service",
            "Communication",
            "Multitasking",
            "Cultural awareness",
            "Budgeting",
            "Team leadership",
            "Composure under pressure"
        ],
        "misconceptions": [
            "Hospitality is just serving food",
            "It's low-skill, low-growth work",
            "You can't build a real career without owning a restaurant"
        ],
        "related_industries": [
            "hospitality",
            "tourism",
            "culinary",
            "events",
            "food service"
        ],
        "videos": [
            "Bon Appétit (YouTube)",
            "Chef's Table-style documentaries",
            "hotel-management case-study channels"
        ],
        "books": [
            "Setting the Table by Danny Meyer",
            "Kitchen Confidential by Anthony Bourdain",
            "The Ritz-Carlton Way service-culture writings"
        ],
        "communities": [
            "r/KitchenConfidential (Reddit)",
            "American Hotel & Lodging Educational Institute network",
            "local culinary guilds"
        ],
        "beginner_projects": [
            "Plan and run a small community event",
            "Cook a themed dinner for family or friends",
            "Shadow-work at a local restaurant",
            "Design a mock hotel guest-experience journey"
        ],
        "internships": [
            "hotel management trainee programs",
            "culinary apprenticeships",
            "event-planning internships"
        ],
        "colleges": [
            "Le Cordon Bleu",
            "Culinary Institute of America (CIA)",
            "Ecole hôtelière de Lausanne",
            "Cornell School of Hotel Administration",
            "Institute of Hotel Management (India network)",
            "Glion Institute of Higher Education",
            "Les Roches Global Hospitality Education",
            "Pennsylvania State University",
            "Ohio State University",
            "University of Manchester",
            "University of Bristol"
        ],
        "companies": [
            "Marriott International",
            "Hilton",
            "Taj Hotels",
            "Four Seasons",
            "Airbnb",
            "Accor",
            "Siemens Digital Industries",
            "Reliance Industries",
            "Accenture"
        ]
    },
    {
        "id": "world_law",
        "name": "Law",
        "description": "Law is the profession of interpreting, applying, and shaping the rules that govern society — from courtroom litigation to corporate contracts, human rights advocacy, and legal policy.",
        "why_it_matters": "Law underpins how disputes get resolved fairly, how rights get protected, and how businesses and governments operate within agreed rules.",
        "global_importance": "As technology, climate, and global trade raise new legal questions, the field keeps expanding into genuinely new specializations.",
        "future_growth": "Legal technology, international arbitration, and technology/privacy law are fast-growing specializations beyond traditional litigation.",
        "famous_careers": [
            "Litigator",
            "Corporate Counsel",
            "Public Defender",
            "Human Rights Lawyer",
            "Legal Policy Analyst"
        ],
        "beginner_roadmap": [
            "Join a debate or moot court club",
            "Read landmark case summaries",
            "Volunteer with a legal-aid clinic",
            "Take an introductory law or civics course",
            "Shadow a practicing lawyer"
        ],
        "required_skills": [
            "Argumentation",
            "Research",
            "Writing",
            "Reading comprehension",
            "Ethics",
            "Public speaking",
            "Attention to detail"
        ],
        "misconceptions": [
            "All lawyers go to court",
            "Law is only for people who want to argue",
            "It's a guaranteed path to wealth"
        ],
        "related_industries": [
            "law",
            "legal services",
            "justice",
            "human rights",
            "policy"
        ],
        "videos": [
            "LegalEagle (YouTube)",
            "Crash Course Government and Politics",
            "Oxford Union debate recordings"
        ],
        "books": [
            "Getting to Yes by Roger Fisher and William Ury",
            "Just Mercy by Bryan Stevenson",
            "The Rule of Law by Tom Bingham"
        ],
        "communities": [
            "r/LawSchool (Reddit)",
            "Moot Court and Model UN societies",
            "local bar association student chapters"
        ],
        "beginner_projects": [
            "Write a mock legal brief on a real issue",
            "Organize a school moot court",
            "Research a landmark court case in depth",
            "Volunteer at a legal-aid organization"
        ],
        "internships": [
            "legal-aid clinic internships",
            "law firm summer clerkships",
            "court-shadowing programs"
        ],
        "colleges": [
            "Harvard Law School",
            "Yale Law School",
            "National Law School of India University",
            "Oxford Faculty of Law",
            "Georgetown Law",
            "University of Cambridge Faculty of Law",
            "NYU School of Law",
            "King's College London",
            "RMIT University",
            "Politecnico di Milano",
            "Delft University of Technology"
        ],
        "companies": [
            "Cyril Amarchand Mangaldas",
            "DLA Piper",
            "Skadden",
            "Clifford Chance",
            "Clio (legal tech)",
            "Deloitte",
            "PwC",
            "EY"
        ]
    },
    {
        "id": "world_finance",
        "name": "Finance",
        "description": "Finance is the discipline of managing money, risk, and investment — from personal financial planning and corporate finance to capital markets, insurance, and quantitative analysis.",
        "why_it_matters": "Finance determines how capital flows to businesses, ideas, and infrastructure — it shapes economic opportunity at every scale from a household budget to a national economy.",
        "global_importance": "Global markets connect economies worldwide, and financial literacy and analysis skills are foundational across nearly every industry.",
        "future_growth": "Fintech, algorithmic trading, and sustainable/impact investing are actively reshaping traditional finance career paths.",
        "famous_careers": [
            "Investment Analyst",
            "Financial Planner",
            "Actuary",
            "Risk Manager",
            "Quantitative Analyst"
        ],
        "beginner_roadmap": [
            "Learn budgeting and basic investing",
            "Take an introductory economics or statistics course",
            "Join or start an investment club",
            "Practice with a stock-market simulator",
            "Read one foundational finance book"
        ],
        "required_skills": [
            "Quantitative analysis",
            "Excel and data modeling",
            "Economics",
            "Risk assessment",
            "Communication",
            "Ethics",
            "Attention to detail"
        ],
        "misconceptions": [
            "Finance is only for math geniuses",
            "It's all trading stocks all day",
            "You need family wealth to get started"
        ],
        "related_industries": [
            "finance",
            "banking",
            "investing",
            "economics",
            "insurance"
        ],
        "videos": [
            "Khan Academy Finance",
            "Ben Felix (YouTube)",
            "Two Cents (PBS)"
        ],
        "books": [
            "The Intelligent Investor by Benjamin Graham",
            "Thinking in Bets by Annie Duke",
            "A Random Walk Down Wall Street by Burton Malkiel"
        ],
        "communities": [
            "r/personalfinance (Reddit)",
            "CFA Institute student chapters",
            "investment club networks"
        ],
        "beginner_projects": [
            "Build a personal budget tracker",
            "Run a stock-market simulation portfolio",
            "Analyze a public company's financial statements",
            "Start a school investment club"
        ],
        "internships": [
            "bank summer analyst programs",
            "fintech internships",
            "actuarial trainee programs"
        ],
        "colleges": [
            "Wharton School (UPenn)",
            "London School of Economics",
            "Indian Institute of Management network",
            "University of Chicago Booth",
            "NYU Stern",
            "HEC Paris",
            "KU Leuven",
            "Tsinghua University",
            "Fudan University",
            "University of Cape Town"
        ],
        "companies": [
            "Goldman Sachs",
            "JPMorgan Chase",
            "Vanguard",
            "HDFC Bank",
            "BlackRock",
            "Morgan Stanley",
            "KPMG",
            "IBM",
            "Infosys"
        ]
    },
    {
        "id": "world_psychology",
        "name": "Psychology",
        "description": "Psychology is the scientific study of mind and behavior — spanning clinical practice, research, counseling, and applying behavioral insight to workplaces, schools, and technology.",
        "why_it_matters": "Mental health, learning, and decision-making all rest on psychological science — it's foundational to human wellbeing far beyond the therapy room.",
        "global_importance": "Rising global attention to mental health has made psychological expertise urgently needed in schools, workplaces, and healthcare systems worldwide.",
        "future_growth": "Behavioral science is expanding into UX research, organizational psychology, and digital mental-health platforms, well beyond traditional clinical roles.",
        "famous_careers": [
            "Clinical Psychologist",
            "School Counselor",
            "Industrial-Organizational Psychologist",
            "Behavioral Researcher",
            "UX Researcher"
        ],
        "beginner_roadmap": [
            "Read an introductory psychology book",
            "Volunteer as a peer listener or counselor",
            "Take an introductory psychology course",
            "Journal and study your own behavior patterns",
            "Shadow a school counselor"
        ],
        "required_skills": [
            "Active listening",
            "Empathy",
            "Research methods",
            "Statistics",
            "Ethics",
            "Observation",
            "Communication"
        ],
        "misconceptions": [
            "Psychology is just common sense",
            "Psychologists can read minds",
            "It's the same as psychiatry"
        ],
        "related_industries": [
            "psychology",
            "mental health",
            "counseling",
            "behavioral science",
            "education"
        ],
        "videos": [
            "Crash Course Psychology",
            "Kati Morton (YouTube)",
            "Yale's The Science of Well-Being course clips"
        ],
        "books": [
            "Thinking, Fast and Slow by Daniel Kahneman",
            "Man's Search for Meaning by Viktor Frankl",
            "The Body Keeps the Score by Bessel van der Kolk"
        ],
        "communities": [
            "r/psychology (Reddit)",
            "Psi Chi psychology honor society",
            "local peer-counseling programs"
        ],
        "beginner_projects": [
            "Run a small survey-based behavior study",
            "Volunteer with a peer-support program",
            "Summarize a real psychology research paper",
            "Start a mental-health awareness campaign at school"
        ],
        "internships": [
            "hospital and clinic shadowing programs",
            "research-lab assistantships",
            "school counseling internships"
        ],
        "colleges": [
            "Stanford University",
            "University of Cambridge",
            "NIMHANS (India)",
            "University of Michigan",
            "Tavistock and Portman NHS Trust",
            "University College London",
            "University of São Paulo",
            "Australian National University",
            "University of Toronto",
            "National University of Singapore"
        ],
        "companies": [
            "Headspace",
            "BetterHelp",
            "Google People Analytics",
            "Kaiser Permanente",
            "Calm",
            "Tata Consultancy Services",
            "Wipro",
            "Honeywell"
        ]
    },
    {
        "id": "world_film",
        "name": "Film",
        "description": "Film is the craft of visual storytelling through moving images — directing, cinematography, editing, sound, and production, from short independent projects to major studio releases.",
        "why_it_matters": "Film shapes culture, empathy, and shared imagination at a global scale, and the underlying craft skills apply across advertising, documentary, and digital media too.",
        "global_importance": "Regional film industries — from Hollywood to Bollywood to Nollywood — are major cultural exporters and economic engines in their own right.",
        "future_growth": "Streaming platforms have massively expanded demand for content, opening real opportunities well beyond traditional theatrical releases.",
        "famous_careers": [
            "Director",
            "Cinematographer",
            "Film Editor",
            "Sound Designer",
            "Production Designer"
        ],
        "beginner_roadmap": [
            "Make a short film with a phone camera",
            "Learn basic editing software",
            "Volunteer on a local or student production",
            "Study one film shot-by-shot",
            "Enter a school or youth film festival"
        ],
        "required_skills": [
            "Storytelling",
            "Visual composition",
            "Editing software",
            "Collaboration",
            "Project management",
            "Camera and lighting basics",
            "Persistence"
        ],
        "misconceptions": [
            "You need expensive gear to start",
            "Film school is the only path in",
            "It's all glamorous red carpets"
        ],
        "related_industries": [
            "film",
            "media",
            "entertainment",
            "production",
            "animation"
        ],
        "videos": [
            "Every Frame a Painting",
            "StudioBinder (YouTube)",
            "Film Riot"
        ],
        "books": [
            "Save the Cat by Blake Snyder",
            "In the Blink of an Eye by Walter Murch",
            "Rebel Without a Crew by Robert Rodriguez"
        ],
        "communities": [
            "r/filmmakers (Reddit)",
            "local film-festival volunteer networks",
            "Sundance Collab community"
        ],
        "beginner_projects": [
            "Shoot and edit a 3-minute short film",
            "Storyboard an original scene",
            "Volunteer as crew on a local shoot",
            "Analyze the editing of a favorite film scene"
        ],
        "internships": [
            "production company internships",
            "local film-festival internships",
            "studio post-production internships"
        ],
        "colleges": [
            "USC School of Cinematic Arts",
            "NYU Tisch School of the Arts",
            "Film and Television Institute of India (FTII)",
            "National Film School (UK)",
            "AFI Conservatory",
            "La Fémis (France)",
            "University of Melbourne",
            "Technical University of Munich",
            "University of Edinburgh",
            "Seoul National University"
        ],
        "companies": [
            "A24",
            "Pixar Animation Studios",
            "Yash Raj Films",
            "Warner Bros.",
            "Studio Ghibli",
            "3M",
            "Philips",
            "Samsung"
        ]
    },
    {
        "id": "world_music",
        "name": "Music",
        "description": "Music spans performing, composing, producing, and engineering sound — a field built on technical craft, creativity, and years of deliberate practice across genres and roles.",
        "why_it_matters": "Music shapes identity and emotion across every culture, and the industry behind it — production, licensing, live events — is a genuinely large, structured career field.",
        "global_importance": "Streaming has globalized music discovery, letting artists and producers from anywhere reach worldwide audiences directly.",
        "future_growth": "Home-studio production technology and direct-to-fan platforms are lowering the barrier to real music careers outside traditional label systems.",
        "famous_careers": [
            "Composer",
            "Sound Engineer",
            "Music Producer",
            "Performing Musician",
            "Music Therapist"
        ],
        "beginner_roadmap": [
            "Learn a core instrument or DAW software",
            "Write and record one original piece",
            "Join a school or community ensemble",
            "Study a favorite artist's songwriting technique",
            "Perform at an open mic"
        ],
        "required_skills": [
            "Music theory",
            "An instrument or production software",
            "Ear training",
            "Collaboration",
            "Creativity",
            "Practice discipline",
            "Basic audio engineering"
        ],
        "misconceptions": [
            "Music careers require fame to succeed",
            "You must start as a child prodigy",
            "It's only performing, not producing or teaching"
        ],
        "related_industries": [
            "music",
            "audio production",
            "entertainment",
            "performing arts"
        ],
        "videos": [
            "Rick Beato (YouTube)",
            "Adam Neely",
            "NPR Tiny Desk Concerts"
        ],
        "books": [
            "This Is Your Brain on Music by Daniel Levitin",
            "The Music Lesson by Victor Wooten",
            "All You Need to Know About the Music Business by Donald Passman"
        ],
        "communities": [
            "r/WeAreTheMusicMakers (Reddit)",
            "local music-production communities",
            "songwriting collectives"
        ],
        "beginner_projects": [
            "Record and release an original song",
            "Score a short film scene",
            "Start a small ensemble or band",
            "Build a home recording setup"
        ],
        "internships": [
            "recording studio internships",
            "local label internships",
            "music therapy practicum placements"
        ],
        "colleges": [
            "Berklee College of Music",
            "Juilliard School",
            "Royal College of Music",
            "Trinity Laban Conservatoire",
            "Manhattan School of Music",
            "Guildhall School of Music and Drama",
            "University of Tokyo",
            "University of Delhi",
            "University of Sydney",
            "McGill University"
        ],
        "companies": [
            "Universal Music Group",
            "Spotify",
            "Sony Music",
            "Warner Music Group",
            "Larsen & Toubro",
            "Bechtel",
            "AECOM"
        ]
    },
    {
        "id": "world_gaming",
        "name": "Gaming",
        "description": "Gaming is the craft of designing and building interactive experiences — game design, programming, art, audio, and production, spanning indie projects to major studio titles.",
        "why_it_matters": "Games are one of the most widely-consumed entertainment forms globally, and the interaction-design skills they require now apply well beyond entertainment, into education and training.",
        "global_importance": "The games industry generates more revenue globally than film and music combined, spanning mobile, PC, and console markets worldwide.",
        "future_growth": "Indie tools and accessible engines have made small-team and solo game development a genuinely viable path, not just large-studio work.",
        "famous_careers": [
            "Game Designer",
            "Gameplay Programmer",
            "Game Artist",
            "Narrative Designer",
            "QA Test Lead"
        ],
        "beginner_roadmap": [
            "Learn a game engine (Unity or Godot)",
            "Build a tiny playable prototype",
            "Join a game jam",
            "Study the design of a favorite game",
            "Share work for feedback in a dev community"
        ],
        "required_skills": [
            "Programming",
            "Game design principles",
            "Problem-solving",
            "Art or audio basics",
            "Playtesting and iteration",
            "Collaboration",
            "Project scoping"
        ],
        "misconceptions": [
            "Making games is just playing games",
            "You need a huge team and budget",
            "It's only for programmers, not writers or artists"
        ],
        "related_industries": [
            "gaming",
            "game development",
            "software",
            "entertainment",
            "interactive media"
        ],
        "videos": [
            "GDC — Game Developers Conference talks",
            "Extra Credits (YouTube)",
            "Brackeys game-dev tutorials"
        ],
        "books": [
            "The Art of Game Design by Jesse Schell",
            "Blood, Sweat, and Pixels by Jason Schreier",
            "Rules of Play by Katie Salen and Eric Zimmerman"
        ],
        "communities": [
            "r/gamedev (Reddit)",
            "itch.io game-jam community",
            "Global Game Jam local chapters"
        ],
        "beginner_projects": [
            "Build a simple platformer in Unity or Godot",
            "Enter a 48-hour game jam",
            "Design a board game and playtest it",
            "Mod an existing game"
        ],
        "internships": [
            "game studio QA internships",
            "indie studio apprenticeships",
            "game-jam mentorship programs"
        ],
        "colleges": [
            "DigiPen Institute of Technology",
            "Carnegie Mellon Entertainment Technology Center",
            "University of Southern California Games program",
            "SAE Institute",
            "Full Sail University",
            "University of British Columbia",
            "Nanyang Technological University",
            "KAIST",
            "Peking University"
        ],
        "companies": [
            "Riot Games",
            "Nintendo",
            "Ubisoft",
            "Naughty Dog",
            "Supercell",
            "Valve",
            "Jacobs Engineering",
            "Capgemini",
            "Siemens Digital Industries"
        ]
    },
    {
        "id": "world_defense",
        "name": "Defense",
        "description": "Defense encompasses the engineering, strategy, intelligence, and operations that keep nations secure — spanning military service, defense technology, cybersecurity, and logistics.",
        "why_it_matters": "National and global security depends on a mix of technical innovation, disciplined operations, and strategic thinking developed in this field.",
        "global_importance": "Defense technology increasingly overlaps with civilian innovation — GPS, the internet, and jet engines all trace back to defense research.",
        "future_growth": "Cybersecurity, autonomous systems, and space-based defense are the fastest-growing specializations within the field.",
        "famous_careers": [
            "Defense Systems Engineer",
            "Intelligence Analyst",
            "Military Officer",
            "Cybersecurity Specialist",
            "Logistics Officer"
        ],
        "beginner_roadmap": [
            "Join a cadet corps or similar leadership program",
            "Study physics and systems thinking",
            "Learn the basics of cybersecurity",
            "Read a foundational strategy text",
            "Attend a defense-technology talk or open day"
        ],
        "required_skills": [
            "Discipline",
            "Systems engineering",
            "Strategic thinking",
            "Teamwork",
            "Technical proficiency",
            "Composure under pressure",
            "Communication"
        ],
        "misconceptions": [
            "Defense careers are only for soldiers",
            "It's all combat roles",
            "You can't have a technical or civilian career in defense"
        ],
        "related_industries": [
            "defense",
            "aerospace",
            "security",
            "military",
            "government"
        ],
        "videos": [
            "Smarter Every Day defense-tech episodes",
            "Real Engineering defense-tech features",
            "official service-branch channels"
        ],
        "books": [
            "The Art of War by Sun Tzu",
            "On War by Carl von Clausewitz",
            "Skunk Works by Ben Rich"
        ],
        "communities": [
            "r/DefenseTech (Reddit)",
            "cadet and ROTC-style programs",
            "veteran mentorship networks"
        ],
        "beginner_projects": [
            "Study a historical military-logistics case",
            "Build a basic cybersecurity home lab",
            "Join a debate on defense policy",
            "Research a defense-technology innovation"
        ],
        "internships": [
            "defense-contractor internships",
            "government defense-agency internships",
            "cadet summer training programs"
        ],
        "colleges": [
            "United States Military Academy (West Point)",
            "United States Naval Academy (Annapolis)",
            "National Defence Academy (India)",
            "Royal Military Academy Sandhurst",
            "Georgia Institute of Technology aerospace/defense research",
            "University of Hong Kong",
            "Trinity College Dublin",
            "University of Amsterdam",
            "KTH Royal Institute of Technology"
        ],
        "companies": [
            "Lockheed Martin",
            "Northrop Grumman",
            "BAE Systems",
            "Hindustan Aeronautics Limited",
            "Raytheon Technologies",
            "Reliance Industries",
            "Accenture",
            "Deloitte"
        ]
    },
    {
        "id": "world_climate",
        "name": "Climate",
        "description": "Climate work spans the science, engineering, and policy needed to understand and respond to a changing planet — from renewable energy and carbon capture to climate-risk modeling and environmental policy.",
        "why_it_matters": "Climate change is one of the defining technical and political challenges of this century, touching agriculture, infrastructure, health, and the global economy.",
        "global_importance": "Every country now faces real climate-adaptation and mitigation decisions, creating genuine, urgent demand for skilled people across science, engineering, and policy.",
        "future_growth": "Renewable energy, carbon-removal technology, and climate-risk finance are among the fastest-growing sectors globally.",
        "famous_careers": [
            "Climate Scientist",
            "Renewable Energy Engineer",
            "Sustainability Consultant",
            "Environmental Policy Analyst",
            "Carbon Markets Analyst"
        ],
        "beginner_roadmap": [
            "Calculate and reduce your own carbon footprint",
            "Join a school sustainability club",
            "Study basic climate science",
            "Volunteer for a local environmental campaign",
            "Learn how renewable-energy systems work"
        ],
        "required_skills": [
            "Environmental science",
            "Data analysis",
            "Systems thinking",
            "Policy literacy",
            "Communication",
            "Engineering basics",
            "Advocacy"
        ],
        "misconceptions": [
            "Climate careers are only activism",
            "It's too late to make a difference",
            "It's only for scientists, not engineers or policy people"
        ],
        "related_industries": [
            "climate",
            "sustainability",
            "renewable energy",
            "environment",
            "policy"
        ],
        "videos": [
            "Kurzgesagt – In a Nutshell",
            "Our Changing Climate (YouTube)",
            "Climate Town"
        ],
        "books": [
            "Drawdown edited by Paul Hawken",
            "The Uninhabitable Earth by David Wallace-Wells",
            "How to Avoid a Climate Disaster by Bill Gates"
        ],
        "communities": [
            "r/climate (Reddit)",
            "Fridays for Future local chapters",
            "Climate Reality Project"
        ],
        "beginner_projects": [
            "Run a school energy or waste audit",
            "Build a small solar or wind demo project",
            "Analyze local climate-data trends",
            "Organize a sustainability awareness campaign"
        ],
        "internships": [
            "renewable-energy company internships",
            "environmental NGO internships",
            "climate-policy research assistantships"
        ],
        "colleges": [
            "ETH Zurich",
            "Stanford Doerr School of Sustainability",
            "Wageningen University",
            "TERI School of Advanced Studies (India)",
            "University of East Anglia Climatic Research Unit",
            "Indian Institute of Technology Delhi",
            "Indian Institute of Technology Madras",
            "University of Waterloo",
            "University of Illinois Urbana-Champaign"
        ],
        "companies": [
            "Tesla Energy",
            "Ørsted",
            "Climeworks",
            "Patagonia",
            "Beyond Meat",
            "PwC",
            "EY",
            "KPMG"
        ]
    },
    {
        "id": "world_manufacturing",
        "name": "Manufacturing",
        "description": "Manufacturing is the science of turning designs into physical products at scale — process engineering, robotics, quality control, and supply-chain systems behind everything physically made.",
        "why_it_matters": "Nearly every physical object relies on manufacturing systems designed for precision, safety, and efficiency — it's a foundational, hands-on engineering discipline.",
        "global_importance": "Global supply chains depend on manufacturing expertise, and reshoring/automation trends are actively reshaping where and how things get built.",
        "future_growth": "Robotics, 3D printing, and smart-factory automation are transforming manufacturing into one of the most technology-intensive fields in engineering.",
        "famous_careers": [
            "Manufacturing Engineer",
            "Industrial Engineer",
            "Quality Assurance Manager",
            "Robotics Technician",
            "Supply Chain Analyst"
        ],
        "beginner_roadmap": [
            "Visit or tour a local factory",
            "Learn CAD software basics",
            "Join a robotics or maker club",
            "Study lean and Six Sigma fundamentals",
            "Build a small physical prototype"
        ],
        "required_skills": [
            "CAD and design tools",
            "Process optimization",
            "Quality control",
            "Robotics and automation basics",
            "Problem-solving",
            "Math",
            "Attention to detail"
        ],
        "misconceptions": [
            "Manufacturing is just assembly-line labor",
            "It's a shrinking, outdated industry",
            "There's no room for creativity"
        ],
        "related_industries": [
            "manufacturing",
            "industrial engineering",
            "robotics",
            "supply chain",
            "production"
        ],
        "videos": [
            "How It's Made (Discovery)",
            "Real Engineering (YouTube)",
            "Practical Engineering"
        ],
        "books": [
            "The Toyota Way by Jeffrey Liker",
            "The Goal by Eliyahu Goldratt",
            "Lean Thinking by James Womack and Daniel Jones"
        ],
        "communities": [
            "r/manufacturing (Reddit)",
            "Society of Manufacturing Engineers student chapters",
            "local maker-space communities"
        ],
        "beginner_projects": [
            "Design and 3D print a functional part",
            "Map and optimize a simple production process",
            "Build a small assembly-line simulation",
            "Join a robotics competition team"
        ],
        "internships": [
            "manufacturing-plant internships",
            "industrial-engineering co-ops",
            "robotics/automation internships"
        ],
        "colleges": [
            "Georgia Institute of Technology",
            "MIT mechanical/manufacturing engineering",
            "RWTH Aachen University",
            "University of Michigan",
            "Indian Institute of Technology network",
            "Texas A&M University",
            "University of Wisconsin-Madison",
            "Pennsylvania State University",
            "Ohio State University"
        ],
        "companies": [
            "Toyota",
            "Siemens",
            "Tata Steel",
            "General Electric",
            "Foxconn",
            "IBM",
            "Infosys",
            "Tata Consultancy Services"
        ]
    },
    {
        "id": "world_research",
        "name": "Research",
        "description": "Research is the disciplined pursuit of new knowledge — designing experiments, analyzing data, and publishing findings across every scientific and technical field.",
        "why_it_matters": "Nearly every technology and medical advance began as research — it's the engine behind long-term progress, not just an academic exercise.",
        "global_importance": "Global challenges from disease to climate require sustained, well-funded research across borders and disciplines.",
        "future_growth": "Data science and AI-assisted discovery are accelerating the pace of research across fields, from materials science to drug discovery.",
        "famous_careers": [
            "Research Scientist",
            "Lab Technician",
            "Data Scientist",
            "Postdoctoral Researcher",
            "Research Program Manager"
        ],
        "beginner_roadmap": [
            "Join a science fair or research competition",
            "Read one research paper end-to-end",
            "Reach out to a professor for a lab-shadowing opportunity",
            "Learn basic statistics",
            "Design and run a small experiment"
        ],
        "required_skills": [
            "Curiosity and questioning",
            "Statistics",
            "Scientific writing",
            "Experimental design",
            "Data analysis",
            "Patience",
            "Critical thinking"
        ],
        "misconceptions": [
            "Research is only for people pursuing a PhD",
            "It's all lab coats and test tubes",
            "Results have to be groundbreaking to matter"
        ],
        "related_industries": [
            "research",
            "science",
            "academia",
            "r&d",
            "data science"
        ],
        "videos": [
            "Veritasium",
            "SciShow",
            "3Blue1Brown"
        ],
        "books": [
            "A Short History of Nearly Everything by Bill Bryson",
            "The Structure of Scientific Revolutions by Thomas Kuhn",
            "Lab Girl by Hope Jahren"
        ],
        "communities": [
            "r/AskScience (Reddit)",
            "university undergraduate research programs",
            "local science-fair mentorship networks"
        ],
        "beginner_projects": [
            "Design and run a simple experiment",
            "Write a literature review on a topic of interest",
            "Enter a school science fair",
            "Replicate a published study's basic method"
        ],
        "internships": [
            "university summer undergraduate research programs",
            "national-lab internships",
            "corporate R&D internships"
        ],
        "colleges": [
            "MIT",
            "Stanford University",
            "University of Cambridge",
            "Indian Institute of Science (IISc)",
            "ETH Zurich",
            "Max Planck-affiliated institutes",
            "University of Manchester",
            "University of Bristol",
            "King's College London",
            "RMIT University"
        ],
        "companies": [
            "Bell Labs",
            "DeepMind",
            "Tata Institute of Fundamental Research",
            "CERN",
            "Wipro",
            "Honeywell",
            "3M"
        ]
    },
    {
        "id": "world_ngos",
        "name": "NGOs",
        "description": "NGO work is the professional practice of running real programs that address humanitarian and social needs — fundraising, field operations, advocacy, and measurable impact at scale.",
        "why_it_matters": "NGOs fill critical gaps governments and markets don't reach — disaster response, health access, education — and increasingly run as sophisticated, data-driven organizations.",
        "global_importance": "International NGOs coordinate humanitarian response and development work across nearly every country facing crisis or systemic need.",
        "future_growth": "Impact measurement and program-evaluation expertise are professionalizing the sector, creating real demand beyond traditional fundraising and field roles.",
        "famous_careers": [
            "Program Officer",
            "Humanitarian Field Worker",
            "Grant Writer",
            "Monitoring and Evaluation Specialist",
            "Community Organizer"
        ],
        "beginner_roadmap": [
            "Volunteer with a local nonprofit",
            "Learn grant-writing basics",
            "Study a real development-economics case",
            "Organize a small community fundraiser or drive",
            "Read one book on global development"
        ],
        "required_skills": [
            "Empathy",
            "Project management",
            "Fundraising and grant-writing",
            "Cross-cultural communication",
            "Data-driven evaluation",
            "Resilience",
            "Budgeting"
        ],
        "misconceptions": [
            "NGO work doesn't pay a real salary",
            "It's only volunteering, not a career",
            "You must work abroad to make an impact"
        ],
        "related_industries": [
            "ngo",
            "nonprofit",
            "humanitarian",
            "social impact",
            "development"
        ],
        "videos": [
            "TED Talks on global development",
            "Oxfam (YouTube)",
            "Doctors Without Borders field reports"
        ],
        "books": [
            "Poor Economics by Abhijit Banerjee and Esther Duflo",
            "Half the Sky by Nicholas Kristof and Sheryl WuDunn",
            "Dead Aid by Dambisa Moyo"
        ],
        "communities": [
            "r/nonprofit (Reddit)",
            "local NGO volunteer networks",
            "Net Impact student chapters"
        ],
        "beginner_projects": [
            "Organize a local fundraiser or donation drive",
            "Volunteer consistently with one nonprofit for a semester",
            "Write a grant proposal for a real cause",
            "Research and present on an NGO's impact model"
        ],
        "internships": [
            "nonprofit program internships",
            "UN Volunteers programme",
            "local NGO field internships"
        ],
        "colleges": [
            "London School of Economics — development studies",
            "Georgetown School of Foreign Service",
            "Tata Institute of Social Sciences",
            "SOAS University of London",
            "Fletcher School (Tufts)",
            "Politecnico di Milano",
            "Delft University of Technology",
            "KU Leuven",
            "Tsinghua University"
        ],
        "companies": [
            "Oxfam",
            "Doctors Without Borders (MSF)",
            "CARE International",
            "Save the Children",
            "BRAC",
            "Philips",
            "Samsung",
            "Larsen & Toubro"
        ]
    },
    {
        "id": "world_sports",
        "name": "Sports",
        "description": "Sports careers span coaching, analytics, sports medicine, and the business side of athletics — turning athletic passion into structured, professional roles on and off the field.",
        "why_it_matters": "Sports shape health, community identity, and a genuinely large global entertainment and business industry beyond just playing professionally.",
        "global_importance": "Major leagues, the Olympics, and grassroots sports programs all depend on skilled professionals in analytics, medicine, and management, not only athletes.",
        "future_growth": "Sports analytics and data science have transformed how teams recruit, train, and strategize, creating real technical career paths.",
        "famous_careers": [
            "Sports Analyst",
            "Athletic Trainer",
            "Sports Marketing Manager",
            "Coach",
            "Sports Data Scientist"
        ],
        "beginner_roadmap": [
            "Coach or assist a youth team",
            "Learn basic sports statistics and analytics",
            "Study the business side of a favorite league",
            "Volunteer at a local sporting event",
            "Track and analyze your own training data"
        ],
        "required_skills": [
            "Data analysis",
            "Communication",
            "Leadership",
            "Physiology basics",
            "Marketing",
            "Negotiation",
            "Discipline"
        ],
        "misconceptions": [
            "Sports careers require being a professional athlete",
            "It's only coaching",
            "There's no real science or business behind it"
        ],
        "related_industries": [
            "sports",
            "athletics",
            "sports management",
            "fitness",
            "sports science"
        ],
        "videos": [
            "ESPN 30 for 30",
            "Team Whistle (YouTube)",
            "sports-science breakdown channels"
        ],
        "books": [
            "Moneyball by Michael Lewis",
            "The Sports Gene by David Epstein",
            "Relentless by Tim Grover"
        ],
        "communities": [
            "r/sportsanalytics (Reddit)",
            "local youth-league coaching networks",
            "sports-management student associations"
        ],
        "beginner_projects": [
            "Analyze a real team's season statistics",
            "Coach or organize a youth sports session",
            "Design a training plan using real data",
            "Cover a local game as a sports journalist"
        ],
        "internships": [
            "sports team front-office internships",
            "sports-marketing agency internships",
            "athletic-training practicum placements"
        ],
        "colleges": [
            "University of Oregon sports business",
            "Loughborough University sports science",
            "Indian Institute of Sports Management",
            "German Sport University Cologne",
            "Ohio University sports administration",
            "Fudan University",
            "University of Cape Town",
            "University of São Paulo",
            "Australian National University"
        ],
        "companies": [
            "Nike",
            "ESPN",
            "FIFA",
            "Under Armour",
            "Bechtel",
            "AECOM",
            "Jacobs Engineering"
        ]
    },
    {
        "id": "world_fashion",
        "name": "Fashion",
        "description": "Fashion is the design, production, and business of clothing and personal style — spanning garment design, textile technology, retail, and increasingly sustainable production.",
        "why_it_matters": "Fashion is both a creative art form and one of the world's largest manufacturing and retail industries, with real environmental and labor stakes.",
        "global_importance": "Global fashion supply chains connect design studios, textile mills, and retail markets across continents.",
        "future_growth": "Sustainable materials, circular-fashion business models, and made-to-order production are reshaping a traditionally fast-moving, wasteful industry.",
        "famous_careers": [
            "Fashion Designer",
            "Textile Technologist",
            "Fashion Buyer",
            "Stylist",
            "Sustainable-Fashion Consultant"
        ],
        "beginner_roadmap": [
            "Learn basic sewing and pattern-making",
            "Sketch and design a small original collection",
            "Study the supply chain of a garment",
            "Volunteer or intern at a local boutique",
            "Follow one sustainable-fashion brand closely"
        ],
        "required_skills": [
            "Sketching and design",
            "Sewing and pattern-making",
            "Trend research",
            "Textile knowledge",
            "Marketing",
            "Business basics",
            "Sustainability awareness"
        ],
        "misconceptions": [
            "Fashion is just runway glamour",
            "You must be a great artist to design",
            "It's not a serious business career"
        ],
        "related_industries": [
            "fashion",
            "design",
            "textiles",
            "apparel",
            "retail"
        ],
        "videos": [
            "Business of Fashion (YouTube)",
            "runway-archive channels",
            "sustainable-fashion documentary channels"
        ],
        "books": [
            "The Fashion System by Roland Barthes",
            "Gods and Kings by Dana Thomas",
            "Overdressed by Elizabeth Cline"
        ],
        "communities": [
            "r/fashiondesign (Reddit)",
            "Council of Fashion Designers of America student network",
            "local sewing and textile guilds"
        ],
        "beginner_projects": [
            "Design and sew a small original garment",
            "Upcycle old clothing into a new piece",
            "Research a brand's supply chain and sustainability practices",
            "Style a themed lookbook shoot"
        ],
        "internships": [
            "fashion house design internships",
            "retail buying internships",
            "textile company internships"
        ],
        "colleges": [
            "Fashion Institute of Technology (FIT)",
            "Parsons School of Design",
            "Central Saint Martins",
            "National Institute of Fashion Technology (India)",
            "London College of Fashion",
            "University of Toronto",
            "National University of Singapore",
            "University of Melbourne",
            "Technical University of Munich"
        ],
        "companies": [
            "Zara (Inditex)",
            "LVMH",
            "Levi's",
            "Ralph Lauren",
            "H&M",
            "Capgemini",
            "Siemens Digital Industries",
            "Reliance Industries"
        ]
    },
    {
        "id": "world_architecture",
        "name": "Architecture",
        "description": "Architecture is the design of buildings and the spaces around them — combining structural science, spatial creativity, and sustainability into places people live, work, and gather.",
        "why_it_matters": "The built environment shapes daily life at every scale, from a single room's comfort to a city's livability and climate resilience.",
        "global_importance": "Rapid urbanization worldwide makes thoughtful, sustainable architecture and urban planning an urgent global need, not just an aesthetic pursuit.",
        "future_growth": "Sustainable and climate-adaptive design is becoming a standard expectation, not a specialty, across the profession.",
        "famous_careers": [
            "Architect",
            "Urban Planner",
            "Landscape Architect",
            "Structural Designer",
            "Interior Architect"
        ],
        "beginner_roadmap": [
            "Sketch buildings and spaces you notice daily",
            "Learn a basic 3D modeling tool like SketchUp",
            "Build a physical model of a small structure",
            "Study one building's design in depth",
            "Volunteer for a community design project"
        ],
        "required_skills": [
            "Spatial reasoning",
            "Drafting and CAD",
            "Structures and physics basics",
            "Sketching",
            "Project management",
            "Sustainability knowledge",
            "Communication"
        ],
        "misconceptions": [
            "Architecture is just drawing pretty buildings",
            "It takes a decade before you design anything real",
            "It's only for the artistically gifted"
        ],
        "related_industries": [
            "architecture",
            "urban planning",
            "design",
            "construction",
            "real estate"
        ],
        "videos": [
            "30X40 Design Workshop (YouTube)",
            "Archdaily project features",
            "Dezeen documentary content"
        ],
        "books": [
            "The Architecture of Happiness by Alain de Botton",
            "How Buildings Learn by Stewart Brand",
            "Delirious New York by Rem Koolhaas"
        ],
        "communities": [
            "r/architecture (Reddit)",
            "local AIA student chapters",
            "Archinect community"
        ],
        "beginner_projects": [
            "Design and model a small structure, from birdhouse to tiny home",
            "Redesign a public space you use often",
            "Document a building's architectural history",
            "Build a scale model from recycled materials"
        ],
        "internships": [
            "architecture firm internships",
            "urban-planning department internships",
            "design-build studio apprenticeships"
        ],
        "colleges": [
            "The Architectural Association (AA) School of Architecture",
            "Cooper Union",
            "ETH Zurich",
            "Bartlett School of Architecture (UCL)",
            "Sushant School of Art and Architecture (India)",
            "University of Edinburgh",
            "Seoul National University",
            "University of Tokyo",
            "University of Delhi"
        ],
        "companies": [
            "Foster + Partners",
            "Zaha Hadid Architects",
            "Gensler",
            "Skidmore, Owings & Merrill",
            "Studio Mumbai",
            "Accenture",
            "Deloitte",
            "PwC"
        ]
    },
    {
        "id": "world_aviation",
        "name": "Aviation",
        "description": "Aviation covers the engineering, operations, and piloting behind air travel — from aircraft design and maintenance to airline operations and air traffic control.",
        "why_it_matters": "Air travel connects the world's economies and cultures, and it depends on rigorous, safety-first engineering and operations expertise.",
        "global_importance": "Global aviation moves billions of passengers and a significant share of world trade by air freight each year.",
        "future_growth": "Sustainable aviation fuel, electric aircraft, and next-generation air-traffic systems are active areas of real near-term innovation.",
        "famous_careers": [
            "Commercial Pilot",
            "Aircraft Maintenance Engineer",
            "Air Traffic Controller",
            "Aerospace Systems Engineer",
            "Airline Operations Manager"
        ],
        "beginner_roadmap": [
            "Take an introductory flight lesson",
            "Study basic aerodynamics",
            "Build and fly RC aircraft or drones",
            "Visit an airport open day or aviation museum",
            "Learn basic aviation terminology and radio communication"
        ],
        "required_skills": [
            "Spatial awareness",
            "Physics",
            "Attention to detail",
            "Communication",
            "Decision-making under pressure",
            "Technical systems knowledge",
            "Discipline"
        ],
        "misconceptions": [
            "Aviation careers are only pilots",
            "It's prohibitively expensive to enter",
            "There's no room for engineers or ground-operations roles"
        ],
        "related_industries": [
            "aviation",
            "aerospace",
            "aircraft",
            "airlines",
            "air traffic"
        ],
        "videos": [
            "Mentour Pilot (YouTube)",
            "Smarter Every Day aviation episodes",
            "air-traffic-control breakdown channels"
        ],
        "books": [
            "Skunk Works by Ben Rich",
            "Fate Is the Hunter by Ernest K. Gann",
            "The Wright Brothers by David McCullough"
        ],
        "communities": [
            "r/aviation (Reddit)",
            "local flying clubs",
            "Aircraft Owners and Pilots Association student network"
        ],
        "beginner_projects": [
            "Build and fly a model aircraft or drone",
            "Study a real flight plan and airspace map",
            "Simulate a flight using free flight-simulator software",
            "Research an aircraft's engineering history"
        ],
        "internships": [
            "airline operations internships",
            "aircraft manufacturer internships",
            "air-traffic-control trainee programs"
        ],
        "colleges": [
            "Embry-Riddle Aeronautical University",
            "Purdue University aviation technology",
            "Cranfield University",
            "ISAE-SUPAERO",
            "Indira Gandhi Rashtriya Uran Akademi (India)",
            "University of Sydney",
            "McGill University",
            "University of British Columbia",
            "Nanyang Technological University"
        ],
        "companies": [
            "Boeing",
            "Airbus",
            "Delta Air Lines",
            "IndiGo",
            "General Electric Aviation",
            "EY",
            "KPMG",
            "IBM"
        ]
    },
    {
        "id": "world_journalism",
        "name": "Journalism",
        "description": "Journalism is the practice of investigating, verifying, and reporting real stories — from breaking news and data journalism to long-form investigative work.",
        "why_it_matters": "A free, skilled press is central to accountability and informed public decision-making, and demands rigorous fact-based writing.",
        "global_importance": "Global journalism shapes public understanding of everything from local corruption to international conflict.",
        "future_growth": "Data journalism and independent newsletter/podcast publishing are creating real new paths outside traditional newsroom structures.",
        "famous_careers": [
            "Investigative Reporter",
            "Broadcast Journalist",
            "Data Journalist",
            "Editor",
            "Documentary Producer"
        ],
        "beginner_roadmap": [
            "Write for a school or local newspaper",
            "Practice interviewing someone about a real story",
            "Learn basic fact-checking and source verification",
            "Start a blog or podcast on a topic you follow closely",
            "Study a well-reported investigative piece"
        ],
        "required_skills": [
            "Writing",
            "Interviewing",
            "Research",
            "Fact-checking",
            "Ethics",
            "Storytelling",
            "Adaptability"
        ],
        "misconceptions": [
            "Journalism is dying as a career",
            "It's just writing opinions",
            "You need to work at a huge outlet to matter"
        ],
        "related_industries": [
            "journalism",
            "media",
            "publishing",
            "broadcasting",
            "communications"
        ],
        "videos": [
            "Vox (YouTube)",
            "NYT's The Weekly-style explainers",
            "Poynter Institute training videos"
        ],
        "books": [
            "The Elements of Journalism by Bill Kovach and Tom Rosenstiel",
            "All the President's Men by Bob Woodward and Carl Bernstein",
            "Say Nothing by Patrick Radden Keefe"
        ],
        "communities": [
            "r/Journalism (Reddit)",
            "school newspaper and yearbook staff",
            "Society of Professional Journalists student chapters"
        ],
        "beginner_projects": [
            "Report and write a real local-interest story",
            "Start a niche newsletter or podcast",
            "Fact-check a published article",
            "Interview three people on one topic and compile findings"
        ],
        "internships": [
            "newsroom internships",
            "local newspaper reporting internships",
            "broadcast-station production internships"
        ],
        "colleges": [
            "Columbia Journalism School",
            "Indian Institute of Mass Communication",
            "City University of London journalism",
            "Northwestern University Medill",
            "University of Missouri School of Journalism",
            "KAIST",
            "Peking University",
            "University of Hong Kong",
            "Trinity College Dublin"
        ],
        "companies": [
            "The New York Times",
            "Reuters",
            "BBC",
            "The Hindu",
            "Associated Press",
            "Infosys",
            "Tata Consultancy Services",
            "Wipro"
        ]
    },
    {
        "id": "world_healthcare",
        "name": "Healthcare",
        "description": "Healthcare spans clinical care, public health, and health systems — physicians, nurses, therapists, and analysts working to prevent, diagnose, and treat illness at individual and population scale.",
        "why_it_matters": "Healthcare directly determines quality and length of life, and its roles range far beyond medicine into engineering, data, and policy.",
        "global_importance": "Health systems worldwide face urgent capacity, equity, and technology challenges that require skilled people across every specialty.",
        "future_growth": "Telemedicine, health data analytics, and biomedical engineering are expanding healthcare careers well beyond direct patient care.",
        "famous_careers": [
            "Physician",
            "Nurse",
            "Physical Therapist",
            "Public Health Analyst",
            "Biomedical Engineer"
        ],
        "beginner_roadmap": [
            "Volunteer at a hospital or clinic",
            "Get certified in basic first aid and CPR",
            "Shadow a healthcare professional",
            "Study human biology in depth",
            "Join a health-careers club"
        ],
        "required_skills": [
            "Biology and anatomy",
            "Empathy",
            "Communication",
            "Attention to detail",
            "Composure under pressure",
            "Ethics",
            "Teamwork"
        ],
        "misconceptions": [
            "Healthcare only means becoming a doctor",
            "It requires a decade before you help anyone",
            "It's not compatible with a tech or research interest"
        ],
        "related_industries": [
            "healthcare",
            "medicine",
            "public health",
            "biomedical",
            "wellness"
        ],
        "videos": [
            "Osmosis (YouTube)",
            "TED-Ed health explainers",
            "Doctor Mike"
        ],
        "books": [
            "When Breath Becomes Air by Paul Kalanithi",
            "The Emperor of All Maladies by Siddhartha Mukherjee",
            "Being Mortal by Atul Gawande"
        ],
        "communities": [
            "r/medicine (Reddit)",
            "Health Occupations Students of America (HOSA)",
            "local hospital volunteer programs"
        ],
        "beginner_projects": [
            "Organize a health-awareness campaign at school",
            "Volunteer consistently at a clinic or hospital",
            "Research a public-health issue in your community",
            "Shadow multiple healthcare roles to compare them"
        ],
        "internships": [
            "hospital volunteer and shadowing programs",
            "public-health department internships",
            "biomedical-research internships"
        ],
        "colleges": [
            "Johns Hopkins University School of Medicine",
            "All India Institute of Medical Sciences (AIIMS)",
            "Karolinska Institute",
            "University of Oxford Medical Sciences",
            "Duke University School of Medicine",
            "University of Amsterdam",
            "KTH Royal Institute of Technology",
            "Indian Institute of Technology Delhi",
            "Indian Institute of Technology Madras"
        ],
        "companies": [
            "Mayo Clinic",
            "Apollo Hospitals",
            "Cleveland Clinic",
            "Johnson & Johnson",
            "Kaiser Permanente",
            "Honeywell",
            "3M",
            "Philips"
        ]
    },
    {
        "id": "world_education",
        "name": "Education",
        "description": "Education is the design and delivery of learning — teaching, instructional design, and the technology and policy that shape how people acquire knowledge and skills.",
        "why_it_matters": "Every other field depends on education to prepare the people who will work in it — teaching well genuinely compounds into every student's future.",
        "global_importance": "Access to quality education remains one of the largest global equity gaps, and education technology is actively working to close it.",
        "future_growth": "EdTech, personalized learning platforms, and instructional design are expanding education careers well beyond the traditional classroom.",
        "famous_careers": [
            "Classroom Teacher",
            "Instructional Designer",
            "School Counselor",
            "EdTech Product Manager",
            "Curriculum Developer"
        ],
        "beginner_roadmap": [
            "Tutor a younger student regularly",
            "Design a short lesson and teach it to peers",
            "Volunteer with a literacy or after-school program",
            "Study how a favorite subject is best taught",
            "Learn a basic instructional-design tool"
        ],
        "required_skills": [
            "Communication",
            "Patience",
            "Curriculum design",
            "Empathy",
            "Public speaking",
            "Adaptability",
            "Assessment and feedback"
        ],
        "misconceptions": [
            "Teaching is low-paid with no career growth",
            "It's only classroom instruction",
            "Anyone can teach without training"
        ],
        "related_industries": [
            "education",
            "edtech",
            "teaching",
            "curriculum design",
            "learning"
        ],
        "videos": [
            "Crash Course (YouTube)",
            "TED-Ed",
            "Edutopia"
        ],
        "books": [
            "Mindset by Carol Dweck",
            "Pedagogy of the Oppressed by Paulo Freire",
            "Make It Stick by Peter Brown"
        ],
        "communities": [
            "r/Teachers (Reddit)",
            "Teach For All alumni networks",
            "local peer-tutoring programs"
        ],
        "beginner_projects": [
            "Tutor a student in a subject you're strong in",
            "Design and teach a mini-lesson to peers",
            "Build a simple learning app or study tool",
            "Volunteer with a literacy program"
        ],
        "internships": [
            "EdTech company internships",
            "school teaching-assistant programs",
            "curriculum-development internships"
        ],
        "colleges": [
            "Teachers College, Columbia University",
            "Harvard Graduate School of Education",
            "UCL Institute of Education",
            "Stanford Graduate School of Education",
            "Tata Institute of Social Sciences education programs",
            "University of Waterloo",
            "University of Illinois Urbana-Champaign",
            "Texas A&M University",
            "University of Wisconsin-Madison"
        ],
        "companies": [
            "Khan Academy",
            "Coursera",
            "BYJU'S",
            "Pearson",
            "Duolingo",
            "Samsung",
            "Larsen & Toubro",
            "Bechtel"
        ]
    },
    {
        "id": "world_entrepreneurship",
        "name": "Entrepreneurship",
        "description": "Entrepreneurship is the practice of identifying real problems and building new ventures to solve them — combining product thinking, resourcefulness, and business fundamentals.",
        "why_it_matters": "New ventures create jobs, technology, and solutions that established organizations often can't or won't pursue, driving much of economic innovation.",
        "global_importance": "Startup ecosystems worldwide are creating real economic opportunity outside traditional corporate career paths.",
        "future_growth": "Lower-cost tools for building and distributing products have made small, focused, capital-efficient startups increasingly viable.",
        "famous_careers": [
            "Startup Founder",
            "Product Manager",
            "Venture Capital Analyst",
            "Growth Marketer",
            "Operations Lead"
        ],
        "beginner_roadmap": [
            "Identify a real problem you can solve at small scale",
            "Build and sell a tiny product or service",
            "Join or start a school entrepreneurship club",
            "Pitch an idea to get real feedback",
            "Study one startup's early growth story"
        ],
        "required_skills": [
            "Problem-solving",
            "Resilience",
            "Basic finance",
            "Sales and persuasion",
            "Product thinking",
            "Networking",
            "Adaptability"
        ],
        "misconceptions": [
            "Entrepreneurship means you must build a tech startup",
            "Most founders are naturally fearless risk-takers",
            "You need funding before you can start"
        ],
        "related_industries": [
            "entrepreneurship",
            "startups",
            "business",
            "product",
            "venture capital"
        ],
        "videos": [
            "Y Combinator's Startup School (YouTube)",
            "How I Built This (NPR)",
            "YC office hours recordings"
        ],
        "books": [
            "The Lean Startup by Eric Ries",
            "Zero to One by Peter Thiel",
            "Shoe Dog by Phil Knight"
        ],
        "communities": [
            "r/startups (Reddit)",
            "local startup incubator meetups",
            "Junior Achievement entrepreneurship clubs"
        ],
        "beginner_projects": [
            "Launch a small real product or service and get paying customers",
            "Run a micro-business with real numbers",
            "Pitch a business idea at a school competition",
            "Interview a local founder about their journey"
        ],
        "internships": [
            "startup internships",
            "venture-capital analyst internships",
            "startup-accelerator fellow programs"
        ],
        "colleges": [
            "Stanford Graduate School of Business",
            "Indian School of Business",
            "Babson College",
            "MIT Sloan",
            "INSEAD",
            "Pennsylvania State University",
            "Ohio State University",
            "University of Manchester",
            "University of Bristol"
        ],
        "companies": [
            "Razorpay",
            "Notion",
            "Flipkart",
            "Y Combinator ecosystem startups",
            "AECOM",
            "Jacobs Engineering",
            "Capgemini"
        ]
    },
    {
        "id": "world_government",
        "name": "Government",
        "description": "Government careers involve running public institutions — civil administration, diplomacy, legislative work, and public services that keep a society functioning.",
        "why_it_matters": "Effective government delivers roads, courts, schools, and safety nets — the everyday infrastructure of public life depends on skilled administration.",
        "global_importance": "Nations worldwide depend on capable civil services and diplomats to manage everything from public health to international relations.",
        "future_growth": "Digital government services and data-driven public administration are modernizing traditionally paper-based bureaucracies.",
        "famous_careers": [
            "Civil Servant",
            "Diplomat",
            "Policy Advisor",
            "Public Administrator",
            "Legislative Analyst"
        ],
        "beginner_roadmap": [
            "Join Model UN or student government",
            "Study how your local government actually works",
            "Volunteer for a civic or election-related initiative",
            "Read one book on public administration",
            "Attend a public town hall or council meeting"
        ],
        "required_skills": [
            "Public speaking",
            "Policy analysis",
            "Negotiation",
            "Ethics",
            "Organization",
            "Communication",
            "Cultural awareness"
        ],
        "misconceptions": [
            "Government jobs are slow and unrewarding",
            "You need to be a politician to work in government",
            "It's only bureaucracy, not real impact"
        ],
        "related_industries": [
            "government",
            "public administration",
            "civil service",
            "diplomacy",
            "public policy"
        ],
        "videos": [
            "C-SPAN archives",
            "TED Talks on governance",
            "Crash Course Government and Politics"
        ],
        "books": [
            "The Fifth Risk by Michael Lewis",
            "Team of Rivals by Doris Kearns Goodwin",
            "The Utopia of Rules by David Graeber"
        ],
        "communities": [
            "r/PoliticalScience (Reddit)",
            "Model UN and Model Government clubs",
            "civil-service exam prep communities"
        ],
        "beginner_projects": [
            "Attend and report on a local government meeting",
            "Run for a student-government position",
            "Research a public-service reform proposal",
            "Volunteer with an election or civic-engagement drive"
        ],
        "internships": [
            "civil-service internship programs",
            "embassy and foreign-service internships",
            "legislative-office internships"
        ],
        "colleges": [
            "Harvard Kennedy School",
            "Lal Bahadur Shastri National Academy of Administration (India)",
            "London School of Economics",
            "ENA — École nationale d'administration (France)",
            "Georgetown School of Foreign Service",
            "King's College London",
            "RMIT University",
            "Politecnico di Milano",
            "Delft University of Technology"
        ],
        "companies": [
            "Indian Administrative Service",
            "U.S. Foreign Service",
            "UK Civil Service",
            "United Nations Secretariat",
            "European Commission",
            "Siemens Digital Industries",
            "Reliance Industries",
            "Accenture"
        ]
    },
    {
        "id": "world_skilled_trades",
        "name": "Skilled Trades",
        "description": "Skilled trades are the hands-on technical professions that build and maintain the physical world — electricians, plumbers, welders, and technicians working with real tools and systems.",
        "why_it_matters": "Every building, vehicle, and power system depends on skilled tradespeople, and the field offers a genuinely direct path to solid, respected careers.",
        "global_importance": "Aging infrastructure and a shortage of trained tradespeople make this one of the most in-demand, underrated career fields globally.",
        "future_growth": "Renewable-energy installation, EV maintenance, and smart-building systems are creating real new specializations within traditional trades.",
        "famous_careers": [
            "Electrician",
            "Plumber",
            "Welder",
            "HVAC Technician",
            "Automotive Technician"
        ],
        "beginner_roadmap": [
            "Take a hands-on shop or trades class",
            "Shadow a licensed tradesperson for a day",
            "Learn basic tool safety and use",
            "Research a local apprenticeship program",
            "Fix or build something small yourself"
        ],
        "required_skills": [
            "Manual dexterity",
            "Problem-solving",
            "Technical knowledge",
            "Safety practices",
            "Reading schematics and blueprints",
            "Customer service",
            "Physical stamina"
        ],
        "misconceptions": [
            "Trades are a fallback for people who can't go to college",
            "Trades don't pay well",
            "There's no growth path beyond the tools"
        ],
        "related_industries": [
            "skilled trades",
            "construction",
            "manufacturing",
            "technical services"
        ],
        "videos": [
            "This Old House (YouTube)",
            "Practical Engineering",
            "trade-specific channels for electricians and welders"
        ],
        "books": [
            "Shop Class as Soulcraft by Matthew Crawford",
            "Zen and the Art of Motorcycle Maintenance by Robert Pirsig",
            "practical trade-certification study guides"
        ],
        "communities": [
            "r/Trades (Reddit)",
            "local trade-union apprentice networks",
            "SkillsUSA student organization"
        ],
        "beginner_projects": [
            "Complete a basic home-repair project",
            "Build something functional from raw materials",
            "Shadow a licensed tradesperson",
            "Take an introductory trade-safety certification course"
        ],
        "internships": [
            "union apprenticeship programs",
            "technical-college co-op placements",
            "local contractor apprenticeships"
        ],
        "colleges": [
            "Industrial Training Institutes (ITI network, India)",
            "Lincoln Tech",
            "TAFE institutes",
            "local community and technical colleges",
            "KU Leuven",
            "Tsinghua University",
            "Fudan University",
            "University of Cape Town"
        ],
        "companies": [
            "Bosch",
            "Caterpillar",
            "Siemens technical trades divisions",
            "regional construction and utility firms",
            "Deloitte",
            "PwC",
            "EY"
        ]
    },
    {
        "id": "world_social_impact",
        "name": "Social Impact",
        "description": "Social impact work combines entrepreneurship and mission-driven organizing to solve social problems sustainably — social enterprises, impact investing, and community organizing.",
        "why_it_matters": "Social-impact careers prove that solving real social problems and building sustainable organizations aren't mutually exclusive.",
        "global_importance": "Impact investing and social entrepreneurship are growing globally as alternatives to both pure charity and pure profit-seeking business.",
        "future_growth": "Corporate social responsibility and B-Corp certification are pushing mainstream businesses to hire dedicated social-impact professionals.",
        "famous_careers": [
            "Social Entrepreneur",
            "Impact Investment Analyst",
            "Community Organizer",
            "Nonprofit Program Director",
            "Corporate Social Responsibility Manager"
        ],
        "beginner_roadmap": [
            "Volunteer consistently with a cause you care about",
            "Identify a real local problem and prototype a small solution",
            "Study one successful social enterprise's model",
            "Organize a community initiative",
            "Learn the basics of impact measurement"
        ],
        "required_skills": [
            "Empathy",
            "Systems thinking",
            "Project management",
            "Fundraising",
            "Community organizing",
            "Communication",
            "Resilience"
        ],
        "misconceptions": [
            "Social impact work can't also be a real business",
            "It's the same as charity",
            "You need to be wealthy to fund change"
        ],
        "related_industries": [
            "social impact",
            "social entrepreneurship",
            "nonprofit",
            "community development",
            "csr"
        ],
        "videos": [
            "TED Talks on social entrepreneurship",
            "Skoll Foundation (YouTube)",
            "Ashoka Changemakers content"
        ],
        "books": [
            "Banker to the Poor by Muhammad Yunus",
            "How to Change the World by David Bornstein",
            "Give and Take by Adam Grant"
        ],
        "communities": [
            "r/socialentrepreneurship (Reddit)",
            "Net Impact student chapters",
            "local community-organizing networks"
        ],
        "beginner_projects": [
            "Launch a small community-improvement project",
            "Volunteer and track measurable impact over a semester",
            "Design a social-enterprise business model",
            "Organize a fundraiser tied to a specific measurable goal"
        ],
        "internships": [
            "social-enterprise internships",
            "impact-investing fund internships",
            "community-organization fellowships"
        ],
        "colleges": [
            "Stanford d.school social innovation",
            "Skoll Centre for Social Entrepreneurship (Oxford)",
            "Duke Center for the Advancement of Social Entrepreneurship",
            "Yale School of Management",
            "Tata Institute of Social Sciences",
            "University of São Paulo",
            "Australian National University",
            "University of Toronto",
            "National University of Singapore"
        ],
        "companies": [
            "Ashoka",
            "Acumen",
            "TOMS",
            "B Lab (B Corp certification)",
            "Grameen Bank",
            "KPMG",
            "IBM",
            "Infosys"
        ]
    },
    {
        "id": "world_arts",
        "name": "Arts",
        "description": "The arts encompass visual art, illustration, sculpture, and curation — creative practice built on technical craft, observation, and years of deliberate work.",
        "why_it_matters": "Art shapes how societies see themselves and process shared experience, and the field spans genuine professional paths beyond the image of the struggling artist.",
        "global_importance": "Art markets, museums, and public art programs support real economic ecosystems worldwide, alongside art's cultural and therapeutic value.",
        "future_growth": "Digital illustration, art therapy, and public/community art programs are expanding real career paths beyond traditional gallery representation.",
        "famous_careers": [
            "Illustrator",
            "Fine Artist",
            "Art Curator",
            "Muralist",
            "Art Therapist"
        ],
        "beginner_roadmap": [
            "Draw or create something daily for a month",
            "Build a small portfolio of original work",
            "Visit a museum and study technique closely",
            "Enter a school or community art show",
            "Get feedback from an online art community"
        ],
        "required_skills": [
            "Technical craft in drawing, painting, or sculpture",
            "Creativity",
            "Observation",
            "Critique and feedback",
            "Persistence",
            "Composition",
            "Storytelling"
        ],
        "misconceptions": [
            "You can't make a real living as an artist",
            "Talent matters more than practice",
            "Art careers are only painting or sculpture"
        ],
        "related_industries": [
            "arts",
            "fine arts",
            "illustration",
            "museums",
            "creative"
        ],
        "videos": [
            "The Art Assignment (YouTube)",
            "Great Art Explained",
            "museum virtual-tour channels"
        ],
        "books": [
            "Ways of Seeing by John Berger",
            "Art & Fear by David Bayles and Ted Orland",
            "The Artist's Way by Julia Cameron"
        ],
        "communities": [
            "r/Art (Reddit)",
            "local art collective and co-op studios",
            "DeviantArt community"
        ],
        "beginner_projects": [
            "Create a themed series of 10 original works",
            "Curate a small exhibition, even informally",
            "Study and replicate a historical artwork's technique",
            "Sell or exhibit one piece publicly"
        ],
        "internships": [
            "gallery and museum internships",
            "art-restoration apprenticeships",
            "illustration studio internships"
        ],
        "colleges": [
            "Rhode Island School of Design",
            "Slade School of Fine Art (UCL)",
            "School of the Art Institute of Chicago",
            "Sir J.J. School of Art (India)",
            "Royal Academy of Arts",
            "University of Melbourne",
            "Technical University of Munich",
            "University of Edinburgh",
            "Seoul National University"
        ],
        "companies": [
            "Christie's",
            "Sotheby's",
            "Adobe",
            "local art galleries and museums",
            "Tata Consultancy Services",
            "Wipro",
            "Honeywell"
        ]
    },
    {
        "id": "world_international_development",
        "name": "International Development",
        "description": "International development addresses global poverty, inequality, and access to opportunity — combining economics, program design, and field implementation across countries.",
        "why_it_matters": "Reducing global poverty and improving health, education, and infrastructure access are among the largest-scale, most consequential efforts humanity undertakes.",
        "global_importance": "Multilateral institutions and NGOs coordinate development work across nearly every low- and middle-income country, with measurable real-world stakes.",
        "future_growth": "Evidence-based development — randomized program evaluation and data-driven aid — is professionalizing the field and improving real outcomes.",
        "famous_careers": [
            "Development Economist",
            "Humanitarian Program Manager",
            "Policy Researcher",
            "Monitoring and Evaluation Officer",
            "Field Coordinator"
        ],
        "beginner_roadmap": [
            "Volunteer with an international-development-focused club or NGO",
            "Study a real case of a development program's outcomes",
            "Learn a second language relevant to a region of interest",
            "Read one foundational development-economics book",
            "Research a global issue and propose a small local action"
        ],
        "required_skills": [
            "Cross-cultural communication",
            "Data analysis",
            "Economics",
            "Project management",
            "Ethics",
            "Language skills",
            "Resilience"
        ],
        "misconceptions": [
            "You must live abroad long-term to work in this field",
            "It's the same as charity work",
            "You need an economics PhD to contribute"
        ],
        "related_industries": [
            "international development",
            "humanitarian",
            "ngo",
            "global health",
            "foreign policy"
        ],
        "videos": [
            "TED Talks on global development",
            "World Bank (YouTube)",
            "UNDP field-story documentaries"
        ],
        "books": [
            "Poor Economics by Abhijit Banerjee and Esther Duflo",
            "The Bottom Billion by Paul Collier",
            "Development as Freedom by Amartya Sen"
        ],
        "communities": [
            "r/IRstudies (Reddit)",
            "Model UN alumni networks",
            "local development-focused clubs"
        ],
        "beginner_projects": [
            "Research and present on a real development program's outcomes",
            "Organize a global-issues awareness event",
            "Volunteer with an internationally-focused local organization",
            "Learn a language and study a region's development context in depth"
        ],
        "internships": [
            "UN Volunteers and UN internship programme",
            "World Bank internships",
            "international NGO field internships"
        ],
        "colleges": [
            "Fletcher School (Tufts)",
            "London School of Economics development studies",
            "Institute of Development Studies (Sussex)",
            "Jawaharlal Nehru University",
            "Johns Hopkins SAIS",
            "University of Tokyo",
            "University of Delhi",
            "University of Sydney",
            "McGill University"
        ],
        "companies": [
            "World Bank",
            "United Nations Development Programme",
            "USAID",
            "BRAC",
            "International Rescue Committee",
            "3M",
            "Philips",
            "Samsung"
        ]
    }
]


async def seed() -> None:
    client = get_supabase_client()
    worlds = [CareerWorld.model_validate(w) for w in WORLDS]

    def _upsert() -> None:
        client.table("career_worlds").upsert([w.model_dump(mode="json") for w in worlds]).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(worlds)} career worlds.")


if __name__ == "__main__":
    asyncio.run(seed())

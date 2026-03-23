import os
import streamlit as st
from typing import List, Dict, Any

# API Configuration - Google AI Only
def get_google_ai_token():
    """Get Google AI Pro API key"""
    token = None
    try:
        token = st.secrets["GOOGLE_AI_API_KEY"]
        if token and len(token) > 10:
            return token
    except Exception:
        pass
    
    token = os.getenv("GOOGLE_AI_API_KEY", "")
    if token and len(token) > 10:
        return token
    
    return ""

GOOGLE_AI_API_KEY = get_google_ai_token()

# ✅ GOOGLE AI MODELS - Gemini Family Only
GOOGLE_AI_MODELS = {
    "gemini_pro": "gemini-1.5-pro-latest",  # Best quality, most capable
    "gemini_flash": "gemini-1.5-flash-latest",  # Faster, still excellent
    "gemini_pro_002": "gemini-1.5-pro-002",  # Stable version
    "flash_20_lite": "gemini-2.0-flash-lite",
    "flash_20": "gemini-2.0-flash",
    "flash_25_lite": "gemini-2.5-flash-lite"
}

# Model selection - All Google AI
MAIN_MODEL = GOOGLE_AI_MODELS["flash_25_lite"]  # Main model for all tasks
SCORING_MODEL = GOOGLE_AI_MODELS["flash_25_lite"]  # For relevance scoring
CHATBOT_MODEL = GOOGLE_AI_MODELS["flash_25_lite"]  # For chatbot
DATA_EXTRACTION_MODEL = GOOGLE_AI_MODELS["flash_25_lite"]  # For data extraction

# File processing settings
UPLOAD_FOLDER = "./data/uploads"
CACHE_PATH = "./data/cache"
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB

# Scoring configuration - Simplified for Google AI only
SCORING_WEIGHTS = {
    "relevance_score": 0.70,  # Primary: Gemini relevance scoring
    "experience_match": 0.20,  # Experience alignment
    "skills_match": 0.10  # Skills extraction and matching
}

# Google AI settings - optimized for different tasks
GEMINI_SETTINGS = {
    "data_extraction": {
        "temperature": 0.1,  # Very focused for data extraction
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2000,  # Longer for structured data
        "timeout": 45
    },
    "relevance_scoring": {
        "temperature": 0.2,  # Slightly more creative for analysis
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 500,  # Medium length for scoring
        "timeout": 30
    },
    "chatbot": {
        "temperature": 0.3,  # More creative for conversations
        "top_p": 0.95,
        "top_k": 60,
        "max_output_tokens": 400,  # Good length for chat
        "timeout": 25,
        "system_instruction": """You are an expert HR consultant and resume screening specialist. 
Provide helpful, accurate, and professional advice about candidates, hiring, and recruitment.
Be specific and actionable in your responses. When discussing multiple candidates or analyses,
provide comparative insights and clear recommendations. Base your analysis on the resume data 
and analysis results provided in the context.

The primary employer context is M Group Services, which delivers essential infrastructure
services across water, energy, transport (highways, rail and aviation) and telecoms for
clients across the UK and Ireland, with a strong safety-first and client/customer-centric
culture. Focus on sector fit, safety mindset and delivery on regulated infrastructure."""
    }
}

# Thresholds
MIN_SCORE_THRESHOLD = 0.3
TOP_CANDIDATES = 15

# Enhanced Job templates optimized for multi-JD comparison
JOB_TEMPLATES = {
    "Senior Data Scientist": """
Senior Data Scientist position requiring:
- 5+ years experience in data science and analytics
- Advanced Python programming and SQL skills
- Deep experience with machine learning frameworks (TensorFlow, PyTorch, scikit-learn)
- Statistical analysis and data visualization capabilities
- Experience with cloud platforms (AWS, Azure, GCP)
- Leadership experience mentoring junior team members
- PhD or Master's degree in quantitative field preferred
- Strong problem-solving and communication skills
- Experience with big data technologies (Spark, Hadoop)
- Knowledge of MLOps and model deployment
    """,
    
    "Junior Data Scientist": """
Junior Data Scientist role requiring:
- 1-3 years experience in data science or related field
- Strong Python programming and SQL skills
- Familiarity with machine learning libraries (scikit-learn, pandas, numpy)
- Basic statistical analysis and data visualization capabilities
- Bachelor's degree in STEM field
- Experience with data cleaning and preprocessing
- Knowledge of Jupyter notebooks and Git
- Strong analytical and problem-solving abilities
- Eagerness to learn and grow in data science field
    """,
    
    "Senior Software Engineer - Backend": """
Senior Software Engineer (Backend) position requiring:
- 5+ years backend software development experience
- Proficiency in server-side languages (Python, Java, Go, Node.js)
- Experience with microservices architecture and distributed systems
- Database design and optimization (SQL and NoSQL)
- API development and RESTful services
- Cloud platform experience (AWS, Azure, GCP)
- DevOps and CI/CD pipeline experience
- Leadership and mentoring capabilities
- Bachelor's degree in Computer Science or related field
- Strong system design and architecture skills
    """,
    
    "Frontend Developer - React": """
Frontend Developer (React) role requiring:
- 3+ years React.js development experience
- Proficiency in JavaScript, HTML5, CSS3, and modern ES6+
- Experience with React ecosystem (Redux, React Router, Hooks)
- Knowledge of frontend build tools (Webpack, Babel, npm/yarn)
- Responsive design and mobile-first development
- Experience with version control (Git) and agile methodologies
- UI/UX design sensibility and attention to detail
- Bachelor's degree or equivalent experience
- Portfolio of web applications demonstrating React expertise
    """,
    
    "DevOps Engineer": """
DevOps Engineer position requiring:
- 4+ years DevOps and infrastructure automation experience
- Proficiency in containerization (Docker, Kubernetes)
- Cloud platform expertise (AWS, Azure, GCP)
- Infrastructure as Code (Terraform, CloudFormation, Ansible)
- CI/CD pipeline development and management
- Monitoring and logging systems (Prometheus, Grafana, ELK stack)
- Scripting languages (Python, Bash, PowerShell)
- Linux/Unix system administration
- Security best practices and compliance
- Bachelor's degree in relevant field preferred
    """,
    
    "Product Manager - Technical": """
Technical Product Manager role requiring:
- 4+ years product management experience in tech environment
- Technical background with ability to work closely with engineering teams
- Experience with agile/scrum methodology and product lifecycle management
- Strong analytical skills and data-driven decision making
- Market research and competitive analysis capabilities
- Stakeholder management and communication skills
- Experience with product analytics tools (Google Analytics, Mixpanel)
- Knowledge of software development processes
- MBA or technical degree preferred
- Track record of successful product launches
    """,
    
    "Marketing Manager - Digital": """
Digital Marketing Manager position requiring:
- 5+ years digital marketing experience with team leadership
- Expertise in digital marketing channels (SEO, SEM, social media, email)
- Analytics and performance measurement (Google Analytics, marketing automation)
- Campaign management and budget oversight experience
- Content marketing and brand management
- Marketing technology stack management (CRM, marketing automation)
- A/B testing and conversion optimization
- Bachelor's degree in Marketing, Business, or related field
- Excellent communication and project management skills
- Experience in B2B or B2C marketing environments
    """,
    
    "UX/UI Designer": """
UX/UI Designer position requiring:
- 3+ years user experience and interface design experience
- Proficiency in design tools (Figma, Sketch, Adobe Creative Suite)
- User research and usability testing experience
- Wireframing, prototyping, and user flow creation
- Understanding of design systems and component libraries
- Knowledge of frontend technologies (HTML, CSS, basic JavaScript)
- Portfolio demonstrating strong design thinking and process
- Experience with responsive and mobile design
- Bachelor's degree in Design, HCI, or related field
- Strong communication and collaboration skills
    """,
    
    "Sales Manager - Enterprise": """
Enterprise Sales Manager role requiring:
- 5+ years B2B sales experience with enterprise clients
- Track record of meeting or exceeding sales targets
- Experience with complex sales cycles and multiple stakeholders
- CRM proficiency (Salesforce, HubSpot) and sales process optimization
- Team leadership and sales coaching experience
- Strong negotiation and presentation skills
- Understanding of enterprise software or technology solutions
- Bachelor's degree in Business, Marketing, or related field
- Excellent communication and relationship building abilities
- Experience with account management and customer success
    """,
    
    "HR Business Partner": """
HR Business Partner position requiring:
- 4+ years HR generalist or business partner experience
- Employee relations and performance management expertise
- Talent acquisition and retention strategies
- Compensation and benefits administration
- HR policy development and compliance
- Change management and organizational development
- HRIS and HR analytics experience
- Bachelor's degree in HR, Business, Psychology, or related field
- PHR/SHRM certification preferred
- Strong interpersonal and advisory skills
    """,

    # --- M GROUP INFRASTRUCTURE TEMPLATES ---

    "MGroup Site Engineer - Water & Highways": """
Site Engineer role for M Group Services on water / highways civils projects in the UK and Ireland.
- Experience on water, utilities or major civils pipeline / highways schemes
- Strong setting-out, surveying and QA skills on trunk mains, drainage and structures
- Ability to coordinate plant, materials, workforce and subcontractors on live sites
- Working knowledge of CDM, SHEQ and environmental requirements on regulated infrastructure
- Competent with drawings, ITPs, as-builts and AutoCAD-style records
- Comfortable liaising with clients, local authorities, utilities and third parties
- HNC/HND or degree in Civil Engineering or similar; site-based mindset
    """,

    "MGroup Project Manager - Substations & Energy": """
Project Manager role delivering electrical transmission / substation projects for M Group Services.
- Proven experience leading multi-disciplinary M&E or civils projects in the energy sector
- Background in National Grid / DNO frameworks and UK utilities environments
- Strong NEC contract, commercial and risk management capability
- Full project lifecycle responsibility for time, cost, quality and safety performance
- Able to manage design, construction, commissioning and stakeholder engagement
- Deep understanding of UK H&S regulations (HSWA, CDM, EAWR) and permit systems
- Professional qualification in engineering / construction and recognised PM credential (e.g. APM)
    """,

    "MGroup Construction / Site Manager - Infrastructure": """
Construction / Site Manager role delivering water, energy, highways or rail infrastructure.
- Track record managing civils delivery teams on complex linear or site-based works
- Planning and sequencing works, coordinating multiple crews and subcontractors
- Enforcing safety-first culture and high standards of quality and environmental performance
- Experience with temporary works, traffic management and working near live services
- Comfortable producing and reviewing RAMS, permits, progress reports and forecasts
- Strong client and stakeholder interface skills on regulated infrastructure programmes
    """,

    "MGroup Delivery Manager - Utilities Programmes": """
Delivery Manager role overseeing programmes of utility infrastructure works.
- Experience delivering multi-site works across water, energy or telecoms frameworks
- Programme-level planning, resource allocation and performance management
- Ability to drive productivity, efficiency and right-first-time delivery
- Strong commercial awareness and experience with target-cost / NEC-style contracts
- Skilled at client reporting, risk management and continuous improvement initiatives
    """,

    "MGroup Foreman / Supervisor - Civils & Utilities": """
Working Foreman / Supervisor role on civils and utilities projects.
- Hands-on supervision of gangs delivering earthworks, drainage, pipelines or highways works
- Ensuring safe systems of work, tool-box talks and daily briefings
- Checking quality, setting out information and adherence to design
- Supporting site engineers and managers with records, progress and problem solving
    """,

    "MGroup Service Support / Coordination": """
Service Support / Coordination role within M Group Services.
- Coordinating work orders, schedules, street works or permits for field delivery teams
- Supporting customer and client communication for planned and reactive works
- Updating systems, trackers and reports for programme delivery
- Familiarity with UK utilities, highways or telecoms environments beneficial
    """
}

# Enhanced Google AI Prompts for multi-analysis support
GEMINI_PROMPTS = {
    "data_extraction": """You are an expert resume parser. Extract structured information from this resume text.

**Resume Text:**
{resume_text}

**Instructions:** Extract the following information in JSON format:

```json
{{
    "candidate_name": "Full name of candidate",
    "contact_info": {{
        "email": "email address",
        "phone": "phone number", 
        "location": "city, state/country",
        "linkedin": "linkedin profile"
    }},
    "professional_summary": "Brief 2-3 sentence summary of candidate",
    "work_experience": [
        {{
            "position": "Job title",
            "company": "Company name",
            "duration": "Time period",
            "key_responsibilities": ["responsibility 1", "responsibility 2"],
            "achievements": ["achievement 1", "achievement 2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree type and field",
            "institution": "School name",
            "graduation_year": "Year or expected year",
            "gpa": "If mentioned"
        }}
    ],
    "technical_skills": ["skill1", "skill2", "skill3"],
    "certifications": ["cert1", "cert2"],
    "total_years_experience": 5,
    "key_achievements": ["Notable accomplishment 1", "Notable accomplishment 2"],
    "languages": ["language1", "language2"],
    "soft_skills": ["communication", "leadership", "problem-solving"]
}}"""
}

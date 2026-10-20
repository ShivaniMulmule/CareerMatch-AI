"""
Dataset configuration for CareerMatch AI synthetic dataset generator.
Defines roles, seniority levels, degrees, project archetypes, responsibilities,
and controlled semantic scoring parameters.
"""

from typing import Dict, List, Any

DATASET_SEED = 42
TARGET_RECORD_COUNT = 6000

ROLES: List[str] = [
    "Machine Learning Engineer",
    "Data Scientist",
    "Data Analyst",
    "AI Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Data Engineer",
    "Cloud Engineer",
    "DevOps Engineer",
    "Business Analyst"
]

ROLE_CLUSTERS: Dict[str, str] = {
    "Machine Learning Engineer": "AI_ML",
    "Data Scientist": "AI_ML",
    "AI Engineer": "AI_ML",
    "NLP Engineer": "AI_ML",
    "Computer Vision Engineer": "AI_ML",
    "Data Analyst": "DATA_ANALYTICS",
    "Business Analyst": "DATA_ANALYTICS",
    "Data Engineer": "DATA_ENGINEERING",
    "Backend Developer": "BACKEND",
    "Software Engineer": "SOFTWARE",
    "Frontend Developer": "FRONTEND",
    "Cloud Engineer": "CLOUD_DEVOPS",
    "DevOps Engineer": "CLOUD_DEVOPS"
}

EXPERIENCE_LEVELS: List[Dict[str, Any]] = [
    {"label": "Fresher", "min_years": 0.0, "max_years": 0.0, "weight": 0.15},
    {"label": "Intern", "min_years": 0.2, "max_years": 0.8, "weight": 0.10},
    {"label": "0-1 years", "min_years": 0.5, "max_years": 1.0, "weight": 0.15},
    {"label": "1-2 years", "min_years": 1.0, "max_years": 2.0, "weight": 0.15},
    {"label": "2-3 years", "min_years": 2.0, "max_years": 3.0, "weight": 0.15},
    {"label": "3-5 years", "min_years": 3.0, "max_years": 5.0, "weight": 0.15},
    {"label": "5+ years", "min_years": 5.0, "max_years": 9.0, "weight": 0.15}
]

EDUCATION_LEVELS: List[Dict[str, Any]] = [
    {"degree": "B.Tech in Computer Science & Engineering", "tier": "Tech_UG", "score_weight": 0.90},
    {"degree": "B.Tech in Artificial Intelligence & Data Science", "tier": "Tech_UG", "score_weight": 0.95},
    {"degree": "B.E. in Information Technology", "tier": "Tech_UG", "score_weight": 0.88},
    {"degree": "B.S. in Computer Science", "tier": "Tech_UG", "score_weight": 0.90},
    {"degree": "B.S. in Mathematics & Statistics", "tier": "Math_UG", "score_weight": 0.85},
    {"degree": "M.Tech in Artificial Intelligence", "tier": "Tech_PG", "score_weight": 1.00},
    {"degree": "M.S. in Computer Science", "tier": "Tech_PG", "score_weight": 1.00},
    {"degree": "M.S. in Data Science", "tier": "Tech_PG", "score_weight": 1.00},
    {"degree": "Ph.D. in Machine Learning & NLP", "tier": "Doctorate", "score_weight": 1.00},
    {"degree": "B.B.A in Business Analytics", "tier": "Business_UG", "score_weight": 0.70},
    {"degree": "B.Com / Non-Tech Degree with Online AI Certifications", "tier": "Non_Tech", "score_weight": 0.60}
]

UNIVERSITIES: List[str] = [
    "Indian Institute of Technology (IIT) Bombay",
    "Indian Institute of Technology (IIT) Delhi",
    "National Institute of Technology (NIT) Trichy",
    "Birla Institute of Technology and Science (BITS) Pilani",
    "Vellore Institute of Technology (VIT)",
    "Stanford University Online Professional Education",
    "Carnegie Mellon University",
    "University of California, Berkeley",
    "Anna University",
    "Delhi Technological University (DTU)",
    "Pune Institute of Computer Technology (PICT)",
    "International Institute of Information Technology (IIIT) Hyderabad"
]

ROLE_CORE_CAPABILITIES: Dict[str, List[str]] = {
    "Machine Learning Engineer": [
        "Machine Learning", "Deep Learning", "Python Programming", "Scikit-Learn",
        "MLOps & Model Deployment", "PyTorch", "XGBoost & Gradient Boosting",
        "Cloud Computing & AWS", "Docker & Containerization", "FastAPI & REST APIs"
    ],
    "Data Scientist": [
        "Machine Learning", "Data Analysis & Pandas", "SQL & Relational Databases",
        "Scikit-Learn", "Explainable AI & SHAP", "Python Programming",
        "Deep Learning", "Natural Language Processing", "Agile & Team Collaboration"
    ],
    "Data Analyst": [
        "Data Analysis & Pandas", "SQL & Relational Databases", "Python Programming",
        "Data Pipelines & ETL", "Agile & Team Collaboration"
    ],
    "AI Engineer": [
        "Large Language Models & Transformers", "Deep Learning", "PyTorch",
        "FastAPI & REST APIs", "MLOps & Model Deployment", "Python Programming",
        "Docker & Containerization", "Cloud Computing & AWS"
    ],
    "NLP Engineer": [
        "Natural Language Processing", "Large Language Models & Transformers",
        "PyTorch", "Python Programming", "Deep Learning", "Scikit-Learn", "FastAPI & REST APIs"
    ],
    "Computer Vision Engineer": [
        "Computer Vision", "Deep Learning", "PyTorch", "TensorFlow & Keras",
        "Python Programming", "Docker & Containerization", "MLOps & Model Deployment"
    ],
    "Software Engineer": [
        "Python Programming", "Backend Development", "SQL & Relational Databases",
        "Git & Version Control", "Software Testing & QA", "System Design & Architecture",
        "Docker & Containerization", "Agile & Team Collaboration"
    ],
    "Backend Developer": [
        "Backend Development", "FastAPI & REST APIs", "Python Programming",
        "SQL & Relational Databases", "NoSQL & MongoDB", "Docker & Containerization",
        "System Design & Architecture", "CI/CD & DevOps Automation"
    ],
    "Frontend Developer": [
        "Frontend Web Development", "React & TypeScript", "Tailwind CSS & Styling",
        "Git & Version Control", "Software Testing & QA", "Agile & Team Collaboration"
    ],
    "Data Engineer": [
        "Data Pipelines & ETL", "Distributed Computing & Big Data", "SQL & Relational Databases",
        "Python Programming", "NoSQL & MongoDB", "Docker & Containerization",
        "Cloud Computing & AWS", "Git & Version Control"
    ],
    "Cloud Engineer": [
        "Cloud Computing & AWS", "Docker & Containerization", "Kubernetes & Container Orchestration",
        "CI/CD & DevOps Automation", "System Design & Architecture", "Git & Version Control"
    ],
    "DevOps Engineer": [
        "CI/CD & DevOps Automation", "Docker & Containerization", "Kubernetes & Container Orchestration",
        "Cloud Computing & AWS", "Git & Version Control", "Software Testing & QA"
    ],
    "Business Analyst": [
        "Data Analysis & Pandas", "SQL & Relational Databases", "Agile & Team Collaboration",
        "System Design & Architecture"
    ]
}

PROJECT_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "AI_ML": [
        {
            "name": "End-to-End Customer Churn Predictor with SHAP",
            "desc": "Engineered an XGBoost classification pipeline on 500K customer records. Implemented cross-validation, hyperparameter grid search, and SHAP TreeExplainer for feature attribution, achieving an AUC-ROC of 0.89.",
            "skills": ["Machine Learning", "XGBoost & Gradient Boosting", "Explainable AI & SHAP", "Python Programming", "Scikit-Learn"]
        },
        {
            "name": "Semantic Neural Document Search & Retrieval Engine",
            "desc": "Built a vector search pipeline using sentence-transformers (all-MiniLM-L6-v2) and FAISS indexing to index 100k research papers. Integrated semantic re-ranking and deployed as an async FastAPI service.",
            "skills": ["Natural Language Processing", "Large Language Models & Transformers", "FastAPI & REST APIs", "Python Programming"]
        },
        {
            "name": "Automated Defect Detection via Deep Convolutional Networks",
            "desc": "Developed a PyTorch-based image segmentation network for real-time manufacturing defect identification. Integrated data augmentations and TensorRT optimization, achieving 94.2% mAP at 45 FPS.",
            "skills": ["Computer Vision", "Deep Learning", "PyTorch", "Python Programming"]
        },
        {
            "name": "Production MLOps Pipeline on AWS EC2 & Docker",
            "desc": "Containerized ML inference services using Docker and deployed to AWS EC2 behind an Application Load Balancer. Configured MLflow experiment tracking and automated GitHub Actions CI/CD tests.",
            "skills": ["MLOps & Model Deployment", "Docker & Containerization", "Cloud Computing & AWS", "CI/CD & DevOps Automation"]
        }
    ],
    "DATA_ENGINEERING": [
        {
            "name": "Real-Time Clickstream Streaming Lakehouse",
            "desc": "Architected an Apache Spark and Kafka streaming pipeline ingesting 15,000 events/sec into Delta Lake. Optimized partition pruning and vacuuming routines, cutting analytical query latency by 40%.",
            "skills": ["Distributed Computing & Big Data", "Data Pipelines & ETL", "SQL & Relational Databases", "Python Programming"]
        },
        {
            "name": "Automated Enterprise Data Warehouse Orchestration",
            "desc": "Constructed Airflow DAGs orchestrating daily ETL extractions from MongoDB and PostgreSQL into an analytical warehouse. Integrated automated Great Expectations data quality validation checks.",
            "skills": ["Data Pipelines & ETL", "SQL & Relational Databases", "NoSQL & MongoDB", "Python Programming"]
        }
    ],
    "BACKEND": [
        {
            "name": "High-Throughput Microservice API Gateway",
            "desc": "Engineered an asynchronous FastAPI microservice gateway handling 3,500 RPS with JWT authentication, Redis token caching, and Pydantic request validation models.",
            "skills": ["FastAPI & REST APIs", "Backend Development", "Python Programming", "Docker & Containerization"]
        },
        {
            "name": "Distributed Job Queue & Worker System",
            "desc": "Implemented an asynchronous background worker architecture for document processing using Celery and Redis with PostgreSQL persistence and exponential retry logic.",
            "skills": ["Backend Development", "SQL & Relational Databases", "System Design & Architecture", "Python Programming"]
        }
    ],
    "FRONTEND": [
        {
            "name": "Enterprise Analytics Dashboard in React & TypeScript",
            "desc": "Built a modular single-page SaaS dashboard using React 18, TypeScript, Tailwind CSS, and Recharts. Implemented client-side caching, virtualized data tables, and dark mode theming.",
            "skills": ["Frontend Web Development", "React & TypeScript", "Tailwind CSS & Styling", "Software Testing & QA"]
        }
    ],
    "CLOUD_DEVOPS": [
        {
            "name": "Automated Multi-Environment Kubernetes GitOps Pipeline",
            "desc": "Designed and deployed Kubernetes clusters on AWS EKS using Terraform Infrastructure as Code. Configured ArgoCD GitOps pipelines, Prometheus metrics scraping, and Grafana alert managers.",
            "skills": ["Kubernetes & Container Orchestration", "Cloud Computing & AWS", "Docker & Containerization", "CI/CD & DevOps Automation"]
        }
    ],
    "DATA_ANALYTICS": [
        {
            "name": "Executive Sales & Customer Churn BI Portal",
            "desc": "Constructed complex multi-table SQL queries and window aggregations across 2M transaction records. Delivered actionable cohort analysis identifying $420K in revenue leakages.",
            "skills": ["Data Analysis & Pandas", "SQL & Relational Databases", "Agile & Team Collaboration"]
        }
    ]
}

COMPANY_NAMES: List[str] = [
    "NovaTech AI Labs", "QuantumScale Cloud", "DataPulse Analytics",
    "Apex Global Software", "Cerebral Health AI", "Hyperion FinTech",
    "Synapse Dynamics", "CloudMatrix Solutions", "VectorFlow Systems",
    "OmniData Platforms", "Aether Robotics", "CognitiveEdge AI"
]

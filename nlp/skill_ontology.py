"""
Skill Ontology & Relationship Knowledge Graph for CareerMatch AI.
Provides structured skill hierarchies, directional transferability confidences,
parent-child inheritance, and framework specificity mapping.
Strictly separates explicit competencies from inferred/transferable knowledge.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set


# Configurable Ontology Confidence Weights
ONTOLOGY_PARENT_CONFIDENCE = 0.95
ONTOLOGY_STRONG_RELATED_CONFIDENCE = 0.85
ONTOLOGY_MODERATE_RELATED_CONFIDENCE = 0.70
ONTOLOGY_FRAMEWORK_TRANSFER_CONFIDENCE = 0.40  # Crucial: Concept -> Framework does not guarantee specific tool

# Thresholds for classification
EXPLICIT_CONFIDENCE_THRESHOLD = 0.99
RELATED_CONFIDENCE_THRESHOLD = 0.38  # Below this is considered a True Gap


# The Skill Ontology Graph
SKILL_ONTOLOGY: Dict[str, Dict[str, Any]] = {
    # -----------------------------
    # Deep Learning & Neural Networks
    # -----------------------------
    "deep learning": {
        "canonical": "Deep Learning",
        "aliases": ["dl", "deep neural networks", "dnn"],
        "parents": {
            "machine learning": 0.95,
            "neural networks": 0.95,
            "artificial intelligence": 0.95
        },
        "related": {
            "python": 0.80,
            "numpy": 0.75,
            "pandas": 0.65,
            "model training": 0.90,
            "model evaluation": 0.80,
            "data science": 0.75,
            "gpu computing": 0.60
        },
        "frameworks": {
            "keras": 0.40,
            "tensorflow": 0.40,
            "pytorch": 0.40,
            "jax": 0.35
        }
    },
    "neural networks": {
        "canonical": "Neural Networks",
        "aliases": ["ann", "artificial neural networks", "neural nets"],
        "parents": {
            "machine learning": 0.95,
            "artificial intelligence": 0.95
        },
        "related": {
            "deep learning": 0.90,
            "python": 0.80,
            "numpy": 0.75,
            "model training": 0.85,
            "model evaluation": 0.80
        },
        "frameworks": {
            "keras": 0.40,
            "tensorflow": 0.40,
            "pytorch": 0.40
        }
    },
    "tensorflow": {
        "canonical": "TensorFlow",
        "aliases": ["tf", "tensorflow 2", "tf2"],
        "parents": {
            "deep learning": 0.95,
            "machine learning": 0.90,
            "neural networks": 0.90
        },
        "related": {
            "python": 0.85,
            "model training": 0.85,
            "numpy": 0.80,
            "keras": 0.80,
            "tensorboard": 0.75
        },
        "frameworks": {
            "keras": 0.80
        }
    },
    "keras": {
        "canonical": "Keras",
        "aliases": ["tf.keras"],
        "parents": {
            "deep learning": 0.95,
            "machine learning": 0.90,
            "neural networks": 0.90,
            "tensorflow": 0.85
        },
        "related": {
            "python": 0.85,
            "model training": 0.85,
            "numpy": 0.80
        },
        "frameworks": {}
    },
    "pytorch": {
        "canonical": "PyTorch",
        "aliases": ["torch"],
        "parents": {
            "deep learning": 0.95,
            "machine learning": 0.90,
            "neural networks": 0.90
        },
        "related": {
            "python": 0.90,
            "model training": 0.85,
            "numpy": 0.80,
            "torchvision": 0.80
        },
        "frameworks": {
            "torchvision": 0.80,
            "pytorch lightning": 0.65
        }
    },

    # -----------------------------
    # Machine Learning & Tabular
    # -----------------------------
    "machine learning": {
        "canonical": "Machine Learning",
        "aliases": ["ml", "predictive modeling", "statistical modeling"],
        "parents": {
            "artificial intelligence": 0.95,
            "data science": 0.90
        },
        "related": {
            "python": 0.85,
            "scikit-learn": 0.80,
            "statistics": 0.85,
            "model training": 0.90,
            "model evaluation": 0.85,
            "data analysis": 0.80,
            "data preprocessing": 0.80,
            "numpy": 0.75,
            "pandas": 0.75,
            "supervised learning": 0.90,
            "unsupervised learning": 0.85
        },
        "frameworks": {
            "xgboost": 0.45,
            "lightgbm": 0.40,
            "catboost": 0.40,
            "scikit-learn": 0.75
        }
    },
    "scikit-learn": {
        "canonical": "Scikit-Learn",
        "aliases": ["sklearn", "scikit learn"],
        "parents": {
            "machine learning": 0.95,
            "data science": 0.90
        },
        "related": {
            "python": 0.90,
            "model training": 0.85,
            "model evaluation": 0.85,
            "data preprocessing": 0.85,
            "numpy": 0.80,
            "pandas": 0.80,
            "supervised learning": 0.85
        },
        "frameworks": {}
    },
    "xgboost": {
        "canonical": "XGBoost",
        "aliases": ["extreme gradient boosting", "xgb"],
        "parents": {
            "machine learning": 0.95,
            "gradient boosting": 0.95,
            "supervised learning": 0.90
        },
        "related": {
            "python": 0.85,
            "model training": 0.85,
            "model evaluation": 0.85,
            "scikit-learn": 0.75,
            "pandas": 0.70
        },
        "frameworks": {}
    },

    # -----------------------------
    # Data Analysis & Python Ecosystem
    # -----------------------------
    "pandas": {
        "canonical": "Pandas",
        "aliases": ["pd"],
        "parents": {
            "data analysis": 0.90,
            "data science": 0.85,
            "python": 0.95
        },
        "related": {
            "python": 0.95,
            "data preprocessing": 0.85,
            "data manipulation": 0.90,
            "numpy": 0.80,
            "sql": 0.65
        },
        "frameworks": {}
    },
    "numpy": {
        "canonical": "NumPy",
        "aliases": ["np"],
        "parents": {
            "numerical computing": 0.90,
            "data science": 0.80,
            "python": 0.95
        },
        "related": {
            "python": 0.95,
            "mathematics": 0.80,
            "linear algebra": 0.85,
            "data preprocessing": 0.75,
            "pandas": 0.80
        },
        "frameworks": {}
    },
    "python": {
        "canonical": "Python",
        "aliases": ["python3", "python programming"],
        "parents": {
            "programming languages": 0.95,
            "software engineering": 0.85
        },
        "related": {
            "scripting": 0.90,
            "object-oriented programming": 0.85,
            "clean code": 0.80
        },
        "frameworks": {
            "fastapi": 0.40,
            "django": 0.40,
            "flask": 0.40,
            "pandas": 0.50,
            "numpy": 0.50
        }
    },
    "data science": {
        "canonical": "Data Science",
        "aliases": ["ds"],
        "parents": {
            "artificial intelligence": 0.85
        },
        "related": {
            "python": 0.90,
            "data analysis": 0.95,
            "machine learning": 0.90,
            "pandas": 0.85,
            "numpy": 0.80,
            "sql": 0.80,
            "statistics": 0.85,
            "data visualization": 0.80
        },
        "frameworks": {}
    },
    "data analysis": {
        "canonical": "Data Analysis",
        "aliases": ["eda", "exploratory data analysis", "data analytics"],
        "parents": {
            "data science": 0.90
        },
        "related": {
            "sql": 0.85,
            "pandas": 0.85,
            "python": 0.85,
            "excel": 0.70,
            "data visualization": 0.80
        },
        "frameworks": {}
    },

    # -----------------------------
    # Computer Vision & NLP
    # -----------------------------
    "computer vision": {
        "canonical": "Computer Vision",
        "aliases": ["cv", "vision ai"],
        "parents": {
            "machine learning": 0.85,
            "artificial intelligence": 0.90
        },
        "related": {
            "deep learning": 0.90,
            "image processing": 0.95,
            "neural networks": 0.90,
            "cnn": 0.90,
            "python": 0.80
        },
        "frameworks": {
            "opencv": 0.55
        }
    },
    "cnn": {
        "canonical": "CNN",
        "aliases": ["convolutional neural networks", "convnet"],
        "parents": {
            "deep learning": 0.95,
            "neural networks": 0.95,
            "computer vision": 0.90
        },
        "related": {
            "image processing": 0.85,
            "python": 0.80,
            "machine learning": 0.90
        },
        "frameworks": {}
    },
    "natural language processing": {
        "canonical": "Natural Language Processing",
        "aliases": ["nlp", "text mining", "text analytics"],
        "parents": {
            "machine learning": 0.85,
            "artificial intelligence": 0.90
        },
        "related": {
            "deep learning": 0.80,
            "text processing": 0.95,
            "python": 0.80,
            "transformers": 0.75,
            "tokenization": 0.90
        },
        "frameworks": {
            "huggingface": 0.50,
            "spacy": 0.50,
            "nltk": 0.50
        }
    },
    "transformers": {
        "canonical": "Transformers",
        "aliases": ["transformer models", "llm", "large language models", "bert", "gpt"],
        "parents": {
            "deep learning": 0.95,
            "natural language processing": 0.90
        },
        "related": {
            "python": 0.85,
            "attention mechanisms": 0.90,
            "model fine-tuning": 0.85
        },
        "frameworks": {
            "huggingface": 0.70
        }
    },

    # -----------------------------
    # Web, Backend & APIs
    # -----------------------------
    "fastapi": {
        "canonical": "FastAPI",
        "aliases": ["fast-api"],
        "parents": {
            "backend development": 0.90,
            "rest apis": 0.95,
            "web development": 0.85
        },
        "related": {
            "python": 0.95,
            "api development": 0.95,
            "microservices": 0.80,
            "asyncio": 0.80
        },
        "frameworks": {}
    },
    "django": {
        "canonical": "Django",
        "aliases": ["django rest framework", "drf"],
        "parents": {
            "backend development": 0.90,
            "web development": 0.90
        },
        "related": {
            "python": 0.95,
            "relational databases": 0.80,
            "rest apis": 0.80
        },
        "frameworks": {}
    },
    "flask": {
        "canonical": "Flask",
        "aliases": [],
        "parents": {
            "backend development": 0.90,
            "web development": 0.85
        },
        "related": {
            "python": 0.95,
            "rest apis": 0.85
        },
        "frameworks": {}
    },
    "rest apis": {
        "canonical": "REST APIs",
        "aliases": ["restful api", "rest api", "web apis", "restful services", "api development"],
        "parents": {
            "backend development": 0.90,
            "web development": 0.85
        },
        "related": {
            "http": 0.90,
            "json": 0.90,
            "microservices": 0.80
        },
        "frameworks": {
            "fastapi": 0.40,
            "flask": 0.35,
            "express": 0.35
        }
    },
    "backend development": {
        "canonical": "Backend Development",
        "aliases": ["backend", "server-side development", "backend engineering"],
        "parents": {
            "software engineering": 0.95
        },
        "related": {
            "rest apis": 0.90,
            "databases": 0.85,
            "microservices": 0.80,
            "server-side": 0.90
        },
        "frameworks": {
            "fastapi": 0.40,
            "django": 0.40,
            "node.js": 0.40
        }
    },
    "react": {
        "canonical": "React",
        "aliases": ["reactjs", "react.js"],
        "parents": {
            "frontend development": 0.95,
            "web development": 0.90
        },
        "related": {
            "javascript": 0.95,
            "html": 0.85,
            "css": 0.85,
            "typescript": 0.75,
            "ui development": 0.90
        },
        "frameworks": {
            "next.js": 0.45,
            "redux": 0.50
        }
    },
    "javascript": {
        "canonical": "JavaScript",
        "aliases": ["js", "es6"],
        "parents": {
            "web development": 0.90,
            "programming languages": 0.95
        },
        "related": {
            "frontend development": 0.85,
            "html": 0.80,
            "css": 0.80,
            "typescript": 0.70
        },
        "frameworks": {
            "react": 0.40,
            "node.js": 0.45,
            "vue": 0.35
        }
    },
    "typescript": {
        "canonical": "TypeScript",
        "aliases": ["ts"],
        "parents": {
            "javascript": 0.95,
            "programming languages": 0.95
        },
        "related": {
            "web development": 0.85,
            "frontend development": 0.85
        },
        "frameworks": {
            "react": 0.45,
            "angular": 0.40
        }
    },

    # -----------------------------
    # Databases & SQL
    # -----------------------------
    "sql": {
        "canonical": "SQL",
        "aliases": ["structured query language", "relational databases"],
        "parents": {
            "relational databases": 0.95,
            "database management": 0.90
        },
        "related": {
            "data analysis": 0.80,
            "queries": 0.95,
            "data modeling": 0.85,
            "rdbms": 0.90
        },
        "frameworks": {
            "postgresql": 0.45,
            "mysql": 0.45,
            "sqlite": 0.45,
            "oracle": 0.40
        }
    },
    "postgresql": {
        "canonical": "PostgreSQL",
        "aliases": ["postgres", "pgsql"],
        "parents": {
            "sql": 0.95,
            "relational databases": 0.95
        },
        "related": {
            "database management": 0.90,
            "data modeling": 0.85
        },
        "frameworks": {}
    },
    "mongodb": {
        "canonical": "MongoDB",
        "aliases": ["mongo", "nosql"],
        "parents": {
            "nosql": 0.95,
            "databases": 0.90
        },
        "related": {
            "backend development": 0.80,
            "json": 0.85
        },
        "frameworks": {}
    },

    # -----------------------------
    # DevOps, Cloud & Tools
    # -----------------------------
    "docker": {
        "canonical": "Docker",
        "aliases": ["containerization", "containers", "docker containers"],
        "parents": {
            "containerization": 0.95,
            "devops": 0.85
        },
        "related": {
            "linux": 0.80,
            "cloud computing": 0.75,
            "ci/cd": 0.75
        },
        "frameworks": {
            "kubernetes": 0.50
        }
    },
    "kubernetes": {
        "canonical": "Kubernetes",
        "aliases": ["k8s", "container orchestration"],
        "parents": {
            "container orchestration": 0.95,
            "devops": 0.90,
            "cloud computing": 0.85
        },
        "related": {
            "docker": 0.90,
            "containerization": 0.95,
            "microservices": 0.85,
            "cloud infrastructure": 0.85
        },
        "frameworks": {}
    },
    "aws": {
        "canonical": "AWS",
        "aliases": ["amazon web services", "amazon aws", "cloud computing"],
        "parents": {
            "cloud computing": 0.95,
            "cloud infrastructure": 0.95
        },
        "related": {
            "devops": 0.80,
            "cloud storage": 0.85,
            "distributed systems": 0.80,
            "docker": 0.70
        },
        "frameworks": {
            "aws ec2": 0.80,
            "aws s3": 0.80,
            "aws lambda": 0.75
        }
    },
    "git": {
        "canonical": "Git",
        "aliases": ["github", "gitlab", "version control", "vcs"],
        "parents": {
            "version control": 0.98,
            "software engineering": 0.85
        },
        "related": {
            "collaboration": 0.85,
            "ci/cd": 0.80,
            "github": 0.90
        },
        "frameworks": {}
    },
    "ci/cd": {
        "canonical": "CI/CD",
        "aliases": ["continuous integration", "continuous deployment", "github actions", "jenkins"],
        "parents": {
            "devops": 0.95,
            "software engineering": 0.90
        },
        "related": {
            "git": 0.85,
            "docker": 0.80,
            "automated testing": 0.85
        },
        "frameworks": {}
    }
}


# Precompute lookup index for fast canonical and alias resolution
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for key, data in SKILL_ONTOLOGY.items():
    ALIAS_TO_CANONICAL[key.lower()] = key
    ALIAS_TO_CANONICAL[data["canonical"].lower()] = key
    for alias in data.get("aliases", []):
        ALIAS_TO_CANONICAL[alias.lower()] = key


def normalize_skill_name(raw_name: str) -> str:
    """Normalizes any skill string to its canonical ontology key if known."""
    cleaned = re.sub(r"[^\w\s\.\+#/-]", " ", raw_name).strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if cleaned in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[cleaned]
    return cleaned


def extract_explicit_skills_from_text(
    resume_text: str,
    project_text: str = ""
) -> Dict[str, Dict[str, Any]]:
    """
    Extracts all explicit technical skills recognized in the resume or project text.
    Records context: in_general_text, in_project_text, occurrence_count.
    """
    detected_skills: Dict[str, Dict[str, Any]] = {}
    lower_resume = resume_text.lower()
    lower_projects = project_text.lower()

    for key, data in SKILL_ONTOLOGY.items():
        canonical = data["canonical"]
        aliases_to_check = [key, canonical.lower()] + [a.lower() for a in data.get("aliases", [])]
        
        found_in_resume = False
        found_in_project = False
        match_phrase = ""

        for phrase in aliases_to_check:
            # Word boundary matching
            escaped = re.escape(phrase)
            # Handling special characters like c++, c#, .net
            if not phrase.endswith(("+", "#")):
                pattern = rf"(?:\b|_){escaped}(?:\b|_)"
            else:
                pattern = rf"(?:\b|_){escaped}"
            
            if re.search(pattern, lower_resume):
                found_in_resume = True
                match_phrase = phrase
                if lower_projects and re.search(pattern, lower_projects):
                    found_in_project = True
                break

        if found_in_resume:
            detected_skills[key] = {
                "key": key,
                "canonical": canonical,
                "matched_as": match_phrase,
                "in_projects": found_in_project,
                "confidence": 1.0
            }

    return detected_skills


def evaluate_skill_against_candidate(
    required_skill_str: str,
    candidate_skills: Dict[str, Dict[str, Any]],
    resume_text: str = "",
    project_text: str = "",
    semantic_sim_score: float = 0.0,
    evidence_sentence: str = ""
) -> Dict[str, Any]:
    """
    Evaluates a single required skill against candidate's profile.
    Classifies into exactly one of three categories:
      A. EXPLICIT MATCH (Confidence: 1.0)
      B. RELATED / INFERRED MATCH (Ontology relationship or strong semantic alignment)
      C. TRUE GAP (No explicit or sufficiently strong related skill)

    Guarantees:
      - Does NOT over-claim specific frameworks (e.g. Deep Learning != Keras).
      - Provides transparent, human-readable reasoning explaining WHY it was classified.
    """
    norm_req = normalize_skill_name(required_skill_str)
    req_display = SKILL_ONTOLOGY.get(norm_req, {}).get("canonical", required_skill_str.strip())

    # ----------------------------------------------------
    # Category A: EXPLICIT MATCH
    # ----------------------------------------------------
    if norm_req in candidate_skills:
        cand_item = candidate_skills[norm_req]
        in_proj_msg = " (backed by hands-on project evidence)" if cand_item.get("in_projects") else ""
        return {
            "required_skill": req_display,
            "status": "EXPLICIT MATCH",
            "match_category": "EXPLICIT MATCH",
            "confidence": 1.0,
            "inferred_from": None,
            "relationship_type": "explicit",
            "is_explicit": True,
            "is_gap": False,
            "reason": f"'{req_display}' is explicitly listed in candidate's resume/profile{in_proj_msg}.",
            "best_evidence": evidence_sentence if evidence_sentence else f"Explicit mention of {req_display}"
        }

    # Also check direct word regex in resume text if ontology didn't catch an obscure variant
    escaped_req = re.escape(required_skill_str.strip().lower())
    if len(required_skill_str.strip()) >= 3 and re.search(rf"\b{escaped_req}\b", resume_text.lower()):
        return {
            "required_skill": req_display,
            "status": "EXPLICIT MATCH",
            "match_category": "EXPLICIT MATCH",
            "confidence": 1.0,
            "inferred_from": None,
            "relationship_type": "explicit",
            "is_explicit": True,
            "is_gap": False,
            "reason": f"'{req_display}' is explicitly mentioned in the resume text.",
            "best_evidence": evidence_sentence if evidence_sentence else f"Candidate explicitly mentions {req_display}"
        }

    # ----------------------------------------------------
    # Category B: RELATED / INFERRED MATCH (via Skill Ontology)
    # ----------------------------------------------------
    best_relation_conf = 0.0
    best_source_skill = None
    best_source_display = None
    relationship_kind = None
    relation_reason = ""

    # Check relationships from each candidate skill to the required skill
    for cand_key, cand_info in candidate_skills.items():
        cand_data = SKILL_ONTOLOGY.get(cand_key, {})
        cand_disp = cand_info.get("canonical", cand_key)

        # 1. Is required_skill a PARENT of candidate skill?
        # e.g. candidate has 'tensorflow', required is 'deep learning' (confidence = 0.95)
        # or candidate has 'scikit-learn', required is 'machine learning' (confidence = 0.95)
        parents = cand_data.get("parents", {})
        if norm_req in parents:
            conf = float(parents[norm_req])
            if conf > best_relation_conf:
                best_relation_conf = conf
                best_source_skill = cand_key
                best_source_display = cand_disp
                relationship_kind = "parent_concept"
                relation_reason = (
                    f"Candidate has hands-on {cand_disp} experience, which directly demonstrates "
                    f"mastery of {req_display} concepts."
                )

        # 2. Is required_skill a RELATED adjacent skill of candidate skill?
        # e.g. candidate has 'deep learning', required is 'neural networks' (0.95), 'python' (0.80), 'numpy' (0.75)
        related = cand_data.get("related", {})
        if norm_req in related:
            conf = float(related[norm_req])
            if conf > best_relation_conf:
                best_relation_conf = conf
                best_source_skill = cand_key
                best_source_display = cand_disp
                relationship_kind = "related_adjacent"
                relation_reason = (
                    f"Candidate has {cand_disp} experience, which inherently involves "
                    f"hands-on usage of {req_display} ({int(conf * 100)}% transferable alignment)."
                )

        # 3. Is required_skill a FRAMEWORK of candidate skill?
        # e.g. candidate has 'deep learning', required is 'keras' (0.40), 'tensorflow' (0.40), 'pytorch' (0.40)
        # CRUCIAL REQUIREMENT: Must NOT say candidate knows Keras explicitly! Classify as related/transferable.
        frameworks = cand_data.get("frameworks", {})
        if norm_req in frameworks:
            conf = float(frameworks[norm_req])
            if conf > best_relation_conf:
                best_relation_conf = conf
                best_source_skill = cand_key
                best_source_display = cand_disp
                relationship_kind = "framework_transferable"
                relation_reason = (
                    f"Candidate has {cand_disp} experience, which is strongly related to {req_display} "
                    f"(transferable conceptual knowledge), but {req_display} is not explicitly listed."
                )

        # 4. Inverse Lookup: Is candidate skill a specific framework that implements the required concept?
        # e.g. required is 'machine learning' (broad), candidate has 'xgboost' or 'scikit-learn' (specific framework)
        req_data = SKILL_ONTOLOGY.get(norm_req, {})
        if req_data:
            req_frameworks = req_data.get("frameworks", {})
            if cand_key in req_frameworks:
                conf = 0.95  # Candidate knows specific tool, which demonstrates practical mastery of the broader field!
                if conf > best_relation_conf:
                    best_relation_conf = conf
                    best_source_skill = cand_key
                    best_source_display = cand_disp
                    relationship_kind = "framework_to_parent"
                    relation_reason = (
                        f"Candidate has hands-on {cand_disp} experience, demonstrating practical "
                        f"mastery of {req_display}."
                    )

    # If ontology relationship meets or exceeds threshold
    if best_relation_conf >= RELATED_CONFIDENCE_THRESHOLD:
        return {
            "required_skill": req_display,
            "status": "RELATED MATCH",
            "match_category": "RELATED / INFERRED MATCH",
            "confidence": round(best_relation_conf, 2),
            "inferred_from": best_source_display,
            "relationship_type": relationship_kind,
            "is_explicit": False,
            "is_gap": False,
            "reason": relation_reason,
            "best_evidence": evidence_sentence if evidence_sentence else f"Inferred via {best_source_display} background"
        }

    # ----------------------------------------------------
    # Check for Compound / Sentence Requirements
    # (e.g. "Demonstrated experience in Python, Scikit-Learn, XGBoost, and PyTorch")
    # ----------------------------------------------------
    req_sub_skills = extract_explicit_skills_from_text(required_skill_str)
    if req_sub_skills and len(req_sub_skills) > 1:
        explicit_found = [s for s in req_sub_skills if s in candidate_skills]
        related_found = []
        for s in req_sub_skills:
            if s not in explicit_found:
                # check if any candidate skill relates to s
                for c_k in candidate_skills:
                    c_d = SKILL_ONTOLOGY.get(c_k, {})
                    if s in c_d.get("parents", {}) or s in c_d.get("related", {}) or s in c_d.get("frameworks", {}):
                        related_found.append((s, c_k))
                        break

        if explicit_found:
            disp_exp = [SKILL_ONTOLOGY.get(s, {}).get("canonical", s) for s in explicit_found]
            conf = 1.0 if len(explicit_found) == len(req_sub_skills) else 0.85
            return {
                "required_skill": req_display,
                "status": "EXPLICIT MATCH" if len(explicit_found) >= len(req_sub_skills) / 2 else "RELATED MATCH",
                "match_category": "EXPLICIT MATCH" if len(explicit_found) >= len(req_sub_skills) / 2 else "RELATED / INFERRED MATCH",
                "confidence": conf,
                "inferred_from": None,
                "relationship_type": "compound_explicit",
                "is_explicit": True,
                "is_gap": False,
                "reason": f"Candidate explicitly demonstrates required competencies in {', '.join(disp_exp)}.",
                "best_evidence": evidence_sentence if evidence_sentence else f"Verified {', '.join(disp_exp)}"
            }
        elif related_found:
            disp_rel = [SKILL_ONTOLOGY.get(s[0], {}).get("canonical", s[0]) for s in related_found]
            return {
                "required_skill": req_display,
                "status": "RELATED MATCH",
                "match_category": "RELATED / INFERRED MATCH",
                "confidence": 0.70,
                "inferred_from": ", ".join([SKILL_ONTOLOGY.get(s[1], {}).get("canonical", s[1]) for s in related_found]),
                "relationship_type": "compound_related",
                "is_explicit": False,
                "is_gap": False,
                "reason": f"Candidate demonstrates transferable competencies in {', '.join(disp_rel)} via adjacent technical experience.",
                "best_evidence": evidence_sentence if evidence_sentence else f"Related to {', '.join(disp_rel)}"
            }

    # ----------------------------------------------------
    # Category B (Fallback): Sentence-BERT Semantic Alignment
    # ----------------------------------------------------
    # If Sentence-BERT cosine similarity is moderate or strong (>= 0.48)
    if semantic_sim_score >= 0.48:
        return {
            "required_skill": req_display,
            "status": "RELATED MATCH",
            "match_category": "RELATED / INFERRED MATCH",
            "confidence": round(semantic_sim_score, 2),
            "inferred_from": "Semantic Context",
            "relationship_type": "semantic_similarity",
            "is_explicit": False,
            "is_gap": False,
            "reason": (
                f"Candidate resume demonstrates contextual semantic alignment "
                f"({int(semantic_sim_score * 100)}%) with {req_display} in project or experience narratives."
            ),
            "best_evidence": evidence_sentence
        }

    # ----------------------------------------------------
    # Category C: TRUE GAP
    # ----------------------------------------------------
    return {
        "required_skill": req_display,
        "status": "TRUE GAP",
        "match_category": "TRUE GAP",
        "confidence": round(max(best_relation_conf, semantic_sim_score), 2),
        "inferred_from": None,
        "relationship_type": "unmatched",
        "is_explicit": False,
        "is_gap": True,
        "reason": f"No explicit or sufficiently related {req_display} skill was detected in candidate's profile.",
        "best_evidence": "No direct contextual evidence or transferable background identified in candidate resume."
    }

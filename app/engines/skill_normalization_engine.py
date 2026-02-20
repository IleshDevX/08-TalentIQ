"""
TalentIQ — Engine #5: Skill Normalization Engine
Maps skill variations, abbreviations, and synonyms to canonical skill names.
"""

import logging

import pandas as pd
from app.config import settings

logger = logging.getLogger(__name__)


# Comprehensive synonym → canonical mapping for real-world resume variations
BUILTIN_SYNONYMS: dict[str, str] = {
    # Programming Languages
    "js": "javascript",
    "javascript": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "py": "python",
    "python3": "python",
    "python 3": "python",
    "golang": "go",
    "go lang": "go",
    "c sharp": "c#",
    "csharp": "c#",
    "c plus plus": "c++",
    "cpp": "c++",
    "objective c": "objective-c",
    "obj-c": "objective-c",
    "r lang": "r",
    "r programming": "r",
    "visual basic": "vb.net",
    "vb": "vb.net",

    # Frontend
    "react js": "react",
    "reactjs": "react",
    "react.js": "react",
    "next js": "next.js",
    "nextjs": "next.js",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "vue js": "vue.js",
    "angular js": "angular",
    "angularjs": "angular",
    "sveltejs": "svelte",
    "svelte js": "svelte",
    "html5": "html",
    "css3": "css",
    "tailwind": "tailwind css",
    "bootstrap css": "bootstrap",
    "sass": "scss",

    # Backend
    "node": "node.js",
    "node js": "node.js",
    "nodejs": "node.js",
    "express": "express.js",
    "expressjs": "express.js",
    "express js": "express.js",
    "fastapi": "fastapi",
    "fast api": "fastapi",
    "flask": "flask",
    "django rest framework": "django rest framework",
    "drf": "django rest framework",
    "spring": "spring boot",
    "springboot": "spring boot",
    "spring-boot": "spring boot",
    "dot net": ".net",
    "dotnet": ".net",
    ".net core": ".net",
    "asp.net": ".net",
    "rails": "ruby on rails",
    "ror": "ruby on rails",
    "ruby on rails": "ruby on rails",
    "laravel": "laravel",

    # Databases
    "mongo": "mongodb",
    "mongo db": "mongodb",
    "postgres": "postgresql",
    "psql": "postgresql",
    "mysql": "mysql",
    "ms sql": "sql server",
    "mssql": "sql server",
    "sql server": "sql server",
    "dynamodb": "dynamodb",
    "dynamo db": "dynamodb",
    "redis": "redis",
    "elastic search": "elasticsearch",
    "elasticsearch": "elasticsearch",
    "cassandra": "cassandra",
    "sqlite": "sqlite",
    "mariadb": "mariadb",
    "neo4j": "neo4j",
    "firebase": "firebase",
    "firestore": "firebase",
    "supabase": "supabase",
    "cockroachdb": "cockroachdb",

    # Cloud & DevOps
    "amazon web services": "aws",
    "aws": "aws",
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "azure": "azure",
    "microsoft azure": "azure",
    "k8s": "kubernetes",
    "kube": "kubernetes",
    "kubernetes": "kubernetes",
    "docker": "docker",
    "docker compose": "docker compose",
    "terraform": "terraform",
    "ansible": "ansible",
    "jenkins": "jenkins",
    "ci cd": "ci/cd",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "github actions": "github actions",
    "gitlab ci": "gitlab ci",
    "circleci": "circleci",
    "argocd": "argocd",
    "argo cd": "argocd",
    "helm": "helm",
    "prometheus": "prometheus",
    "grafana": "grafana",
    "datadog": "datadog",
    "new relic": "new relic",

    # AI / ML / Data
    "ml": "machine learning",
    "machine learning": "machine learning",
    "dl": "deep learning",
    "deep learning": "deep learning",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "cv": "computer vision",
    "computer vision": "computer vision",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "gen ai": "generative ai",
    "genai": "generative ai",
    "generative ai": "generative ai",
    "llm": "large language models",
    "llms": "large language models",
    "large language models": "large language models",
    "tf": "tensorflow",
    "tensor flow": "tensorflow",
    "pytorch": "pytorch",
    "py torch": "pytorch",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "huggingface": "hugging face",
    "hugging face": "hugging face",
    "hf": "hugging face",
    "opencv": "opencv",
    "open cv": "opencv",
    "pandas": "pandas",
    "numpy": "numpy",
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "keras": "keras",
    "spacy": "spacy",
    "nltk": "nltk",
    "faiss": "faiss",
    "mlflow": "mlflow",
    "ml flow": "mlflow",
    "wandb": "weights & biases",
    "weights and biases": "weights & biases",

    # Data Engineering
    "spark": "apache spark",
    "apache spark": "apache spark",
    "pyspark": "apache spark",
    "kafka": "apache kafka",
    "apache kafka": "apache kafka",
    "airflow": "apache airflow",
    "apache airflow": "apache airflow",
    "hadoop": "hadoop",
    "hive": "apache hive",
    "dbt": "dbt",
    "snowflake": "snowflake",
    "redshift": "aws redshift",
    "bigquery": "bigquery",
    "big query": "bigquery",
    "etl": "etl",
    "elt": "elt",
    "data warehouse": "data warehousing",
    "data lake": "data lake",
    "delta lake": "delta lake",

    # Tools & Practices
    "git": "git",
    "github": "github",
    "gitlab": "gitlab",
    "bitbucket": "bitbucket",
    "jira": "jira",
    "confluence": "confluence",
    "slack": "slack",
    "figma": "figma",
    "postman": "postman",
    "swagger": "swagger",
    "vscode": "visual studio code",
    "vs code": "visual studio code",
    "vim": "vim",
    "linux": "linux",
    "ubuntu": "linux",
    "bash": "bash",
    "powershell": "powershell",
    "rest": "rest api",
    "rest api": "rest api",
    "restful": "rest api",
    "graphql": "graphql",
    "grpc": "grpc",
    "websocket": "websockets",
    "websockets": "websockets",
    "oauth": "oauth",
    "jwt": "jwt",
    "json web token": "jwt",
    "agile": "agile",
    "scrum": "scrum",
    "kanban": "kanban",
    "tdd": "tdd",
    "bdd": "bdd",
    "oop": "oop",
    "solid": "solid principles",
    "design patterns": "design patterns",
    "microservices": "microservices",
    "micro services": "microservices",
    "monorepo": "monorepo",
    "api gateway": "api gateway",
    "message queue": "message queuing",

    # BI / Analytics
    "power bi": "power bi",
    "powerbi": "power bi",
    "tableau": "tableau",
    "looker": "looker",
    "excel": "excel",
    "google sheets": "google sheets",
    "dax": "dax",

    # Testing
    "selenium": "selenium",
    "cypress": "cypress",
    "playwright": "playwright",
    "jest": "jest",
    "pytest": "pytest",
    "junit": "junit",
    "mocha": "mocha",
    "chai": "chai",

    # Mobile
    "react native": "react native",
    "rn": "react native",
    "flutter": "flutter",
    "swift": "swift",
    "swiftui": "swiftui",
    "kotlin": "kotlin",
    "jetpack compose": "jetpack compose",
    "ios development": "ios",
    "android development": "android",

    # Soft Skills
    "leadership": "leadership",
    "communication": "communication",
    "teamwork": "teamwork",
    "team work": "teamwork",
    "problem solving": "problem solving",
    "critical thinking": "critical thinking",
    "time management": "time management",
    "project management": "project management",
    "pm": "project management",
    "stakeholder management": "stakeholder management",
    "mentoring": "mentoring",
    "presentation": "presentation skills",
    "public speaking": "presentation skills",
}


class SkillNormalizationEngine:

    def __init__(self):
        # Load CSV synonyms as supplementary mappings
        csv_path = settings.DATASETS_DIR / "skill_synonyms.csv"
        self.csv_synonyms: dict[str, str] = {}
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                orig = str(row["original_term"]).strip().lower()
                canon = str(row["normalized_skill_name"]).strip().lower()
                if orig and canon and orig != canon:
                    self.csv_synonyms[orig] = canon
        except Exception:
            logger.warning("Could not load skill_synonyms.csv — using built-in map only")

        # Merge: built-in takes priority, CSV fills gaps
        self.synonym_map: dict[str, str] = {**self.csv_synonyms}
        for key, val in BUILTIN_SYNONYMS.items():
            self.synonym_map[key.lower()] = val.lower()

    def normalize(self, skills: list[str]) -> list[str]:
        """Normalize a list of extracted skills to canonical names."""
        normalized = set()
        for skill in skills:
            canon = self.synonym_map.get(skill.lower().strip(), skill.lower().strip())
            normalized.add(canon)
        return sorted(normalized)

    def normalize_single(self, skill: str) -> str:
        """Normalize a single skill string."""
        return self.synonym_map.get(skill.lower().strip(), skill.lower().strip())

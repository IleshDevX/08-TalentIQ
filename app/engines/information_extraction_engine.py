"""
TalentIQ — Engine 4: Information Extraction Engine
Extracts structured candidate profile from ACTUAL resume text:
  - skills (matched against 300+ built-in + CSV + role-DB entries)
  - education (degrees, institutions, fields of study)
  - experience (years, job titles, date ranges)
  - keywords (domain-specific terms from the resume itself)

Design principle: extract what is ACTUALLY in the resume, never fabricate.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# Comprehensive built-in skill vocabulary  (PRIMARY source)
# Covers programming languages, frameworks, databases, cloud, DevOps,
# AI/ML, data, tools, methodologies — 300+ entries.
# The CSV supplements this; it does NOT replace it.
# ═══════════════════════════════════════════════════════════════════════

_BUILTIN_SKILLS: set[str] = {
    # ── Programming Languages ─────────────────────────────────────
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
    "perl", "lua", "dart", "elixir", "haskell", "clojure", "groovy",
    "objective-c", "matlab", "fortran", "cobol", "vb.net", "assembly",
    "shell", "bash", "powershell", "sql", "plsql", "t-sql",

    # ── Frontend ──────────────────────────────────────────────────
    "react", "angular", "vue.js", "vue", "svelte", "next.js", "nuxt.js",
    "html", "css", "sass", "scss", "less", "tailwind css", "tailwind",
    "bootstrap", "material ui", "chakra ui", "jquery", "ember.js",
    "backbone.js", "web components", "webpack", "vite", "parcel",
    "babel", "eslint", "prettier", "storybook",

    # ── Backend ───────────────────────────────────────────────────
    "node.js", "express.js", "express", "fastapi", "flask", "django",
    "spring boot", "spring", ".net", "asp.net", "ruby on rails", "rails",
    "laravel", "symfony", "gin", "fiber", "actix", "rocket",
    "nestjs", "koa", "hapi", "strapi", "graphql", "grpc",
    "rest api", "rest apis", "restful", "websockets", "soap",

    # ── Databases ─────────────────────────────────────────────────
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "sqlite", "mariadb", "oracle", "sql server",
    "dynamodb", "couchdb", "neo4j", "firebase", "firestore",
    "supabase", "cockroachdb", "influxdb", "timescaledb",
    "memcached", "amazon rds",

    # ── Cloud Platforms ───────────────────────────────────────────
    "aws", "azure", "gcp", "google cloud", "google cloud platform",
    "heroku", "digitalocean", "vercel", "netlify", "cloudflare",
    "alibaba cloud", "oracle cloud", "ibm cloud",
    "aws lambda", "ec2", "s3", "cloudfront", "route 53", "iam",
    "sqs", "sns", "ecs", "eks", "fargate", "sagemaker",
    "azure devops", "azure functions", "azure pipelines",
    "cloud functions", "cloud run", "cloud storage", "bigquery",

    # ── DevOps / CI-CD / Infra ────────────────────────────────────
    "docker", "kubernetes", "k8s", "terraform", "ansible", "puppet",
    "chef", "vagrant", "packer", "consul", "vault",
    "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
    "argocd", "helm", "istio", "envoy", "nginx", "apache",
    "ci/cd", "cicd", "continuous integration", "continuous deployment",
    "linux", "unix", "ubuntu", "centos", "debian", "rhel",
    "prometheus", "grafana", "datadog", "new relic", "splunk",
    "elk stack", "logstash", "kibana", "fluentd",
    "nagios", "zabbix", "pagerduty",

    # ── AI / ML / Data Science ────────────────────────────────────
    "machine learning", "deep learning",
    "natural language processing", "nlp", "computer vision",
    "artificial intelligence", "generative ai", "large language models",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "catboost",
    "hugging face", "transformers", "langchain", "llamaindex",
    "opencv", "spacy", "nltk", "gensim",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "mlflow", "wandb", "weights & biases", "dvc",
    "faiss", "pinecone", "weaviate", "chroma",
    "jupyter", "colab", "kaggle",
    "neural networks", "cnn", "rnn", "lstm", "attention",
    "reinforcement learning", "transfer learning", "fine-tuning",
    "feature engineering", "hyperparameter tuning",
    "regression", "classification", "clustering",
    "random forest", "decision tree", "svm", "naive bayes",
    "gradient boosting", "ensemble methods",

    # ── Data Engineering ──────────────────────────────────────────
    "apache spark", "spark", "pyspark", "apache kafka", "kafka",
    "apache airflow", "airflow", "apache flink", "flink",
    "hadoop", "hive", "presto", "trino",
    "dbt", "snowflake", "redshift", "aws redshift",
    "databricks", "delta lake", "data lake",
    "etl", "elt", "data pipeline", "data warehouse",
    "data modeling", "data governance",

    # ── Testing / QA ──────────────────────────────────────────────
    "selenium", "cypress", "playwright", "puppeteer",
    "jest", "pytest", "junit", "mocha", "chai", "jasmine",
    "testng", "robot framework", "appium",
    "unit testing", "integration testing", "e2e testing",
    "tdd", "bdd", "test automation",

    # ── Mobile ────────────────────────────────────────────────────
    "react native", "flutter", "swift", "swiftui",
    "kotlin", "jetpack compose", "xamarin", "ionic", "cordova",
    "ios", "android", "mobile development",

    # ── Tools / Platforms ─────────────────────────────────────────
    "git", "github", "gitlab", "bitbucket", "svn",
    "jira", "confluence", "trello", "asana", "notion",
    "slack", "teams", "figma", "sketch", "adobe xd",
    "postman", "swagger", "insomnia",
    "visual studio code", "vscode", "intellij", "eclipse", "vim",
    "npm", "yarn", "pip", "conda", "maven", "gradle",

    # ── Methodologies / Practices ─────────────────────────────────
    "agile", "scrum", "kanban", "lean", "waterfall", "safe",
    "devops", "devsecops", "sre", "gitops",
    "oop", "functional programming",
    "solid principles", "design patterns",
    "microservices", "monolithic", "serverless",
    "event-driven", "domain-driven design", "ddd",
    "api gateway", "service mesh", "message queue",
    "cqrs", "event sourcing",

    # ── Security ──────────────────────────────────────────────────
    "oauth", "jwt", "saml", "openid", "ldap",
    "ssl", "tls", "https", "encryption",
    "owasp", "penetration testing", "vulnerability assessment",
    "soc 2", "gdpr", "hipaa", "pci dss",
    "iam", "rbac", "zero trust",

    # ── BI / Analytics ────────────────────────────────────────────
    "power bi", "tableau", "looker", "metabase",
    "google analytics", "mixpanel", "amplitude",
    "excel", "google sheets", "dax",
    "data visualization", "business intelligence",
    "statistics", "a/b testing", "hypothesis testing",

    # ── Architecture / Concepts ───────────────────────────────────
    "system design", "distributed systems", "high availability",
    "load balancing", "caching", "cdn",
    "api design", "database design", "schema design",
    "concurrency", "multithreading", "async programming",
    "data structures", "algorithms",
    "version control", "code review",

    # ── Soft Skills (also recognized as skills) ───────────────────
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "time management", "project management",
    "stakeholder management", "mentoring", "presentation skills",
    "collaboration", "adaptability", "analytical thinking",
}


def _load_role_skills() -> set[str]:
    """Load required + preferred skills from roles_database.json.
    
    NOTE: We deliberately exclude role 'keywords' — those are generic 
    domain terms (e.g. 'deployment', 'compliance', 'operations') that 
    would match too broadly and produce false-positive skill detections.
    """
    extra: set[str] = set()
    try:
        json_path = settings.DATASETS_DIR / "roles_database.json"
        if json_path.exists():
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            for _key, info in data.get("roles", {}).items():
                for s in info.get("required_skills", []):
                    extra.add(s.lower().strip())
                for s in info.get("preferred_skills", []):
                    extra.add(s.lower().strip())
    except Exception:
        logger.warning("Could not load role skills from roles_database.json")
    return extra


class InformationExtractionEngine:
    """
    Extract skills, education, experience, and keywords
    from the ACTUAL text of the uploaded resume.
    """

    def __init__(self) -> None:
        # 1. Start with comprehensive built-in skill list
        all_skills: set[str] = set(_BUILTIN_SKILLS)

        # 2. Add skills from roles_database.json (so we can match them)
        all_skills.update(_load_role_skills())

        # 3. Supplement with CSV (if anything extra there)
        skills_path = settings.DATASETS_DIR / "skills_master.csv"
        try:
            df = pd.read_csv(skills_path)
            csv_skills = df["skill_name"].dropna().str.lower().str.strip().unique()
            all_skills.update(s for s in csv_skills if len(s) > 1)
        except Exception:
            pass

        # Filter and separate
        clean = {s for s in all_skills if s and len(s) > 1}

        # Separate: multi-word matched with regex, single-word via set intersection
        self.multi_word_skills = sorted(
            [s for s in clean if " " in s or "/" in s or "-" in s],
            key=len,
            reverse=True,  # match longer phrases first
        )
        self.single_word_skills = set(
            s for s in clean if " " not in s and "/" not in s and "-" not in s
        )

        # Also keep special-char skills that need exact matching (c++, c#, .net)
        self.special_skills = sorted(
            [s for s in clean if any(c in s for c in "#+.")],
            key=len,
            reverse=True,
        )

        logger.info(
            "InformationExtraction: %d single + %d multi + %d special skills ready",
            len(self.single_word_skills),
            len(self.multi_word_skills),
            len(self.special_skills),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, text: str) -> dict:
        """
        Extract structured profile from resume text.

        Returns
        -------
        dict
            skills   : list[str] — actual skills found in the text
            education: dict      — {"degrees": [...], "institutions": [...], "fields": [...]}
            experience: dict     — {"max_years", "years_mentioned", "job_titles", "date_ranges"}
            keywords : list[str] — domain keywords actually present in the text
        """
        text_lower = text.lower()
        return {
            "skills": self._extract_skills(text, text_lower),
            "education": self._extract_education(text),
            "experience": self._extract_experience(text),
            "keywords": self._extract_keywords(text, text_lower),
        }

    # ── Skills ───────────────────────────────────────────────────────────

    # Words that appear in _BUILTIN_SKILLS or role databases but are too
    # generic to be treated as standalone skills on a resume.
    _SKILL_BLACKLIST: set[str] = {
        "deployment", "testing", "teams", "production", "delivery",
        "operations", "planning", "quality", "performance", "security",
        "compliance", "monitoring", "reporting", "research", "execution",
        "integration", "migration", "automation", "innovation", "lifecycle",
        "governance", "reliability", "standards", "insights", "portfolio",
        "hiring", "mentoring", "velocity", "scale-up", "completion",
        "roadmap", "budgeting", "metrics", "kpis", "ceremonies",
        "timeline", "stability", "efficiency", "safety",
        "sprint planning", "design patterns",
    }

    def _extract_skills(self, text: str, text_lower: str) -> list[str]:
        """Find skills actually mentioned in the resume text."""
        found: set[str] = set()

        # 1. Special-char skills (c++, c#, .net, node.js, etc.)
        for skill in self.special_skills:
            escaped = re.escape(skill)
            if re.search(r"(?<![a-zA-Z])" + escaped + r"(?![a-zA-Z])", text_lower):
                found.add(skill)

        # 2. Multi-word skills — regex boundary match (longer first)
        for skill in self.multi_word_skills:
            # Allow flexible separators: "ci/cd", "ci cd", "ci-cd" all match
            pattern_str = re.escape(skill)
            # Make / and - and space interchangeable
            pattern_str = pattern_str.replace(r"\-", r"[\s/\-]")
            pattern_str = pattern_str.replace(r"\/", r"[\s/\-]")
            pattern_str = pattern_str.replace(r"\ ", r"[\s/\-]+")
            if re.search(r"(?<![a-zA-Z])" + pattern_str + r"(?![a-zA-Z])", text_lower):
                found.add(skill)

        # 3. Single-word skills — tokenize text and intersect
        tokens = set(re.findall(r"\b[a-z][a-z+#.]{1,}\b", text_lower))
        found.update(tokens & self.single_word_skills)

        # 4. Also catch ALL-CAPS / mixed-case tokens (AWS, SQL, GCP, etc.)
        upper_tokens = set(re.findall(r"\b[A-Z][A-Z+#./]{1,}\b", text))
        for tok in upper_tokens:
            low = tok.lower()
            if low in self.single_word_skills or low in {s for s in _BUILTIN_SKILLS}:
                found.add(low)

        # 5. Remove blacklisted generic terms
        found -= self._SKILL_BLACKLIST

        return sorted(found)

    # ── Education ────────────────────────────────────────────────────────

    DEGREE_PATTERNS: list[tuple[str, str]] = [
        (r"\b(?:ph\.?d\.?|doctorate|doctor of philosophy)\b", "Ph.D."),
        (r"\bm\.?s\.?\s+(?:in|of)\s+\w+", "M.S."),
        (r"\b(?:master(?:'?s)?)\s+(?:of|in|degree)\s+\w+", "Master's"),
        (r"\bm\.?b\.?a\.?\b", "MBA"),
        (r"\bm\.?tech\.?\b", "M.Tech"),
        (r"\bm\.?c\.?a\.?\b", "MCA"),
        (r"\bb\.?s\.?\s+(?:in|of)\s+\w+", "B.S."),
        (r"\b(?:bachelor(?:'?s)?)\s+(?:of|in|degree)\s+\w+", "Bachelor's"),
        (r"\bb\.?tech\.?\b", "B.Tech"),
        (r"\bb\.?e\.?\b", "B.E."),
        (r"\bb\.?c\.?a\.?\b", "BCA"),
        (r"\bassociate(?:'?s)?\s+(?:of|in|degree)\s+\w+", "Associate's"),
        (r"\bdiploma\s+(?:in|of)\s+\w+", "Diploma"),
        (r"\bhigh\s*school\s*diploma\b", "High School"),
    ]

    INSTITUTION_PATTERNS = [
        r"\b(?:university|college|institute|academy)\s+(?:of\s+)?[A-Z][\w\s,]{2,40}",
        r"\b(?:IIT|NIT|BITS|MIT|Stanford|Harvard|Berkeley|CMU|Georgia\s+Tech)\b"
        r"(?:\s+[A-Z][\w]*){0,3}",
    ]

    # Terms that indicate non-educational entities (competitions, clubs, events, etc.)
    NON_INSTITUTION_KEYWORDS = {
        "competition", "contest", "championship", "tournament", "fest", "festival",
        "event", "club", "society", "committee", "team", "league", "conference",
        "workshop", "seminar", "hackathon", "olympiad", "quiz", "debate",
        "cultural", "sports", "athletic", "drama", "music", "dance", "art",
        "project", "program", "course", "training", "bootcamp", "meetup"
    }

    FIELD_PATTERNS = [
        r"(?:computer\s+science|information\s+technology|software\s+engineering)",
        r"(?:electrical\s+engineering|mechanical\s+engineering|civil\s+engineering)",
        r"(?:data\s+science|mathematics|statistics|physics|chemistry|biology)",
        r"(?:business\s+administration|economics|finance|marketing|management)",
        r"(?:artificial\s+intelligence|machine\s+learning|cybersecurity)",
    ]

    def _extract_education(self, text: str) -> dict:
        """Extract degrees, institutions, and fields of study."""
        degrees: list[str] = []
        for pattern, label in self.DEGREE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                degrees.append(label)

        # De-duplicate while preserving order
        seen: set[str] = set()
        unique_degrees: list[str] = []
        for d in degrees:
            if d not in seen:
                unique_degrees.append(d)
                seen.add(d)

        institutions: list[str] = []
        for pattern in self.INSTITUTION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                match_lower = match.strip().lower()
                # Filter out non-educational entities (competitions, clubs, events, etc.)
                if not any(keyword in match_lower for keyword in self.NON_INSTITUTION_KEYWORDS):
                    institutions.append(match.strip())

        fields: list[str] = []
        for pattern in self.FIELD_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            fields.extend(m.strip().title() for m in matches)

        return {
            "degrees": unique_degrees,
            "institutions": sorted(set(institutions)),
            "fields": sorted(set(fields)),
        }

    # ── Experience ───────────────────────────────────────────────────────

    EXPERIENCE_YEAR_PATTERNS = [
        r"(\d{1,2})\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp|work)?",
        r"(?:experience|exp)\s*[:\-]?\s*(\d{1,2})\+?\s*(?:years?|yrs?)?",
        r"over\s+(\d{1,2})\s*(?:years?|yrs?)",
    ]

    JOB_TITLE_PATTERNS = [
        r"(?:^|\n)\s*((?:senior|junior|lead|staff|principal|chief|head|associate|"
        r"vp|director|manager|intern)\s+)?"
        r"(software\s+engineer(?:ing)?|developer|architect|analyst|designer|"
        r"scientist|administrator|consultant|coordinator|specialist|"
        r"devops\s+engineer|data\s+engineer|ml\s+engineer|"
        r"product\s+manager|project\s+manager|scrum\s+master|"
        r"full[\s-]?stack\s+developer|front[\s-]?end\s+developer|"
        r"back[\s-]?end\s+developer|qa\s+engineer|test\s+engineer|"
        r"site\s+reliability\s+engineer|platform\s+engineer|"
        r"cloud\s+engineer|security\s+engineer|solutions\s+architect|"
        r"technical\s+lead|tech\s+lead|engineering\s+manager)\b",
    ]

    # Comprehensive date range pattern with month support
    DATE_RANGE_PATTERN = (
        r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?"
        r"(20\d{2}|19\d{2})"
        r"\s*(?:–|—|-|to)\s*"
        r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?"
        r"(20\d{2}|19\d{2}|present|current|now|ongoing)"
    )
    
    # Section headers that indicate work experience
    EXPERIENCE_SECTION_HEADERS = [
        r"(?:^|\n)\s*(?:professional\s+)?(?:work\s+)?experience",
        r"(?:^|\n)\s*employment\s+(?:history|record)",
        r"(?:^|\n)\s*work\s+history",
        r"(?:^|\n)\s*career\s+(?:history|summary)",
    ]
    
    # Section headers to EXCLUDE (not work experience)
    EXCLUDE_SECTION_HEADERS = [
        r"(?:^|\n)\s*education",
        r"(?:^|\n)\s*(?:academic\s+)?projects?",
        r"(?:^|\n)\s*certifications?",
        r"(?:^|\n)\s*publications?",
        r"(?:^|\n)\s*courses?",
        r"(?:^|\n)\s*training",
        r"(?:^|\n)\s*(?:technical\s+)?skills?",
        r"(?:^|\n)\s*(?:extra[\s-]?curricular|activities)",
        r"(?:^|\n)\s*(?:references?|awards?|honors?|achievements?)",
        r"(?:^|\n)\s*(?:summary|objective|profile)",
    ]

    def _extract_experience(self, text: str) -> dict:
        """
        Extract work experience with section-aware parsing.
        
        Strategy:
        1. Isolate the EXPERIENCE section from resume
        2. Extract date ranges ONLY from that section
        3. Use contextual validation (job titles, keywords)
        4. Merge overlapping ranges
        """
        current_year = datetime.now().year
        
        # ─── Step 1: Extract explicit year mentions ───────────────────────
        years: list[int] = []
        for pattern in self.EXPERIENCE_YEAR_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend(int(y) for y in matches if y.isdigit() and int(y) <= 50)
        unique_years = sorted(set(years), reverse=True)

        # ─── Step 2: Isolate EXPERIENCE section ──────────────────────────
        experience_text = self._extract_experience_section(text)
        
        # ─── Step 3: Extract date ranges from experience section only ────
        work_ranges = self._extract_work_date_ranges(experience_text, current_year)
        
        # ─── Step 4: Extract job titles ──────────────────────────────────
        job_titles: list[str] = []
        for pattern in self.JOB_TITLE_PATTERNS:
            matches = re.finditer(pattern, experience_text, re.IGNORECASE)
            for m in matches:
                title = m.group(0).strip()
                if title and len(title) > 3:
                    job_titles.append(title.title())

        # ─── Step 5: Compute total experience ────────────────────────────
        date_intervals = [(start, end) for start, end, _ in work_ranges]
        date_range_strs = [range_str for _, _, range_str in work_ranges]
        
        implied_years = self._compute_total_experience_years(date_intervals)
        max_explicit = max(unique_years) if unique_years else 0
        best_years = max(max_explicit, implied_years)

        return {
            "years_mentioned": unique_years,
            "max_years": best_years,
            "implied_years_from_dates": implied_years,
            "job_titles": sorted(set(job_titles)),
            "date_ranges": sorted(set(date_range_strs)),
        }

    def _extract_experience_section(self, text: str) -> str:
        """
        Isolate the EXPERIENCE/WORK section from the resume.
        Returns the text between EXPERIENCE header and the next major section.
        """
        # Find experience section start
        exp_start = -1
        for pattern in self.EXPERIENCE_SECTION_HEADERS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                exp_start = match.end()
                break
        
        if exp_start == -1:
            # No explicit experience section found — conservative fallback
            # Only look for date ranges with strong job context
            return ""
        
        # Find where experience section ends (next major section)
        exp_end = len(text)
        remaining_text = text[exp_start:]
        
        # Look for the next section header (using all exclude patterns)
        for pattern in self.EXCLUDE_SECTION_HEADERS:
            match = re.search(pattern, remaining_text, re.IGNORECASE)
            if match:
                candidate_end = exp_start + match.start()
                # Take the earliest section boundary
                exp_end = min(exp_end, candidate_end)
        
        experience_section = text[exp_start:exp_end]
        return experience_section

    def _extract_work_date_ranges(
        self, experience_text: str, current_year: int
    ) -> list[tuple[int, int, str]]:
        """
        Extract and validate work experience date ranges.
        Returns list of (start_year, end_year, range_string) tuples.
        """
        work_ranges: list[tuple[int, int, str]] = []
        
        # Find all date range matches
        for match in re.finditer(self.DATE_RANGE_PATTERN, experience_text, re.IGNORECASE):
            start_yr = int(match.group(1))
            end_str = match.group(2).lower()
            end_yr = current_year if end_str in (
                "present", "current", "now", "ongoing"
            ) else int(end_str)
            
            # Basic sanity checks
            if not (1980 <= start_yr <= end_yr <= 2030):
                continue
            
            span = end_yr - start_yr
            
            # Contextual validation: look at surrounding text (±200 chars)
            match_start = max(0, match.start() - 200)
            match_end = min(len(experience_text), match.end() + 200)
            context = experience_text[match_start:match_end].lower()
            
            # Check for job-related keywords in context
            job_keywords = [
                "intern", "engineer", "developer", "analyst", "manager",
                "specialist", "consultant", "coordinator", "assistant",
                "lead", "architect", "designer", "administrator",
                "scientist", "technician", "officer", "executive",
            ]
            
            has_job_keyword = any(kw in context for kw in job_keywords)
            
            # Validation rules:
            # 1. Single position shouldn't exceed 10 years (likely education or projects)
            # 2. Must have job-related keywords nearby OR end date is recent (active work)
            # 3. Start date should be recent for early-career candidates
            
            is_recent_work = end_yr >= current_year - 3
            is_reasonable_span = span <= 10
            
            # Special logic for early-career resumes (most recent date is 2020+)
            if start_yr >= 2020:
                # Likely student/early career — accept only recent short-term roles
                if span <= 6 and end_yr >= 2020:
                    work_ranges.append((start_yr, end_yr, f"{start_yr}-{end_str}"))
            else:
                # Normal career — standard validation
                if is_reasonable_span and (has_job_keyword or is_recent_work):
                    work_ranges.append((start_yr, end_yr, f"{start_yr}-{end_str}"))
        
        return work_ranges

    @staticmethod
    def _compute_total_experience_years(intervals: list[tuple[int, int]]) -> int:
        """
        Merge overlapping date intervals and compute total experience years.
        
        Example:
            [(2020, 2022), (2021, 2024), (2025, 2026)] 
            → merged: [(2020, 2024), (2025, 2026)]
            → total: (2024-2020) + (2026-2025) = 5 years
        """
        if not intervals:
            return 0
        
        # Sort by start year
        sorted_intervals = sorted(intervals)
        merged: list[tuple[int, int]] = []
        
        for start, end in sorted_intervals:
            if not merged or merged[-1][1] < start:
                # No overlap with previous — add new interval
                merged.append((start, end))
            else:
                # Overlap detected — extend the previous interval's end
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        
        # Sum the lengths of all non-overlapping merged intervals
        total = sum(end - start for start, end in merged)
        return total

    # ── Keywords ─────────────────────────────────────────────────────────

    DOMAIN_KEYWORDS: set[str] = {
        # Development domains
        "full-stack", "full stack", "front-end", "front end", "frontend",
        "back-end", "back end", "backend", "devops", "devsecops", "sre",
        "cloud native", "cloud computing", "serverless", "edge computing",

        # AI/ML/Data
        "machine learning", "deep learning", "natural language processing",
        "computer vision", "data science", "data engineering", "data analytics",
        "big data", "data mining", "data modeling", "data pipeline",
        "predictive modeling", "recommendation systems",
        "generative ai", "large language models", "prompt engineering",

        # Architecture
        "microservices", "monolithic", "distributed systems",
        "event-driven architecture", "domain-driven design",
        "system design", "high availability", "scalability",
        "load balancing", "caching", "api design",

        # Process keywords
        "agile", "scrum", "kanban", "lean", "waterfall", "safe",
        "tdd", "bdd", "oop", "functional programming",
        "code review", "pair programming", "mob programming",
        "continuous integration", "continuous deployment", "ci/cd",
        "infrastructure as code", "configuration management",
        "site reliability", "incident management",

        # Security
        "cybersecurity", "information security", "application security",
        "penetration testing", "vulnerability assessment", "threat modeling",
        "zero trust", "identity management",

        # Other domains
        "blockchain", "web3", "iot", "embedded systems",
        "game development", "mobile development", "cross-platform",
        "ecommerce", "fintech", "healthtech", "edtech",
        "real-time", "streaming", "batch processing",
        "etl", "elt", "data warehouse", "data lake",
        "version control", "release management",
    }

    _KEYWORD_STOP = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "shall",
        "can", "need", "must", "it", "its", "this", "that", "these",
        "i", "we", "you", "he", "she", "they", "me", "us", "my", "our",
        "your", "his", "her", "their", "not", "no", "so", "as", "if",
        "then", "than", "too", "very", "also", "just", "about", "all",
        "any", "some", "such", "each", "few", "more", "most", "other",
        "new", "used", "using", "work", "working", "worked", "able",
        "well", "part", "good", "best", "first", "last", "get", "got",
        "make", "made", "take", "took", "come", "came", "know", "see",
        "including", "based", "within", "across", "along", "etc",
    }

    def _extract_keywords(self, text: str, text_lower: str) -> list[str]:
        """
        Extract domain keywords that are ACTUALLY in the resume text.
        Combines pattern-matching for known domain terms with extraction
        of meaningful multi-word phrases.
        """
        found: set[str] = set()

        # 1. Match known domain keywords
        for kw in self.DOMAIN_KEYWORDS:
            escaped = re.escape(kw)
            escaped = escaped.replace(r"\ ", r"[\s\-/]+")
            escaped = escaped.replace(r"\-", r"[\s\-/]+")
            if re.search(r"(?<![a-zA-Z])" + escaped + r"(?![a-zA-Z])", text_lower):
                found.add(kw)

        # 2. Extract meaningful bigrams from the text itself
        words = re.findall(r"\b[a-z]{3,}\b", text_lower)
        for i in range(len(words) - 1):
            if words[i] not in self._KEYWORD_STOP and words[i + 1] not in self._KEYWORD_STOP:
                bigram = f"{words[i]} {words[i + 1]}"
                if bigram in self.DOMAIN_KEYWORDS:
                    found.add(bigram)

        return sorted(found)

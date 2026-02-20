"""
TalentIQ — Engine #14: Enhanced Certification Suggestion Engine v2.0

Intelligent certification recommendation using:
1. Fuzzy matching for skill variations (python/Python, node.js/nodejs)
2. Role-based popular certifications (fallback when no exact matches)
3. Skill clustering (group related skills, suggest multi-skill certs)
4. Global top certifications (always suggest industry-recognized credentials)
"""

from __future__ import annotations

import logging

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)


class CertificationEngine:
    """Smart certification suggestions with fuzzy matching and role-based recommendations."""

    # ── Role-specific popular certifications (domain-aware) ──────────────
    POPULAR_CERTIFICATIONS = {
        # Software/Tech roles
        "tech": [
            {
                "certification": "AWS Certified Solutions Architect",
                "provider": "Amazon Web Services",
                "difficulty": "Advanced",
                "cost_usd": 300,
                "duration_months": 3,
                "recognition_score": 0.95,
                "covers": ["cloud", "aws", "architecture", "infrastructure"],
            },
            {
                "certification": "Google Cloud Professional Data Engineer",
                "provider": "Google Cloud",
                "difficulty": "Advanced",
                "cost_usd": 200,
                "duration_months": 4,
                "recognition_score": 0.92,
                "covers": ["gcp", "data engineering", "big data", "cloud"],
            },
            {
                "certification": "Certified Kubernetes Administrator (CKA)",
                "provider": "CNCF",
                "difficulty": "Advanced",
                "cost_usd": 395,
                "duration_months": 2,
                "recognition_score": 0.93,
                "covers": ["kubernetes", "k8s", "containers", "docker", "devops"],
            },
        ],
        # AI/ML/Data Science roles
        "data_science": [
            {
                "certification": "TensorFlow Developer Certificate",
                "provider": "Google",
                "difficulty": "Intermediate",
                "cost_usd": 100,
                "duration_months": 3,
                "recognition_score": 0.88,
                "covers": ["tensorflow", "machine learning", "deep learning", "ai"],
            },
            {
                "certification": "AWS Certified Machine Learning - Specialty",
                "provider": "Amazon Web Services",
                "difficulty": "Advanced",
                "cost_usd": 300,
                "duration_months": 4,
                "recognition_score": 0.91,
                "covers": ["machine learning", "aws", "sagemaker", "ai", "ml"],
            },
            {
                "certification": "Google Cloud Professional Data Engineer",
                "provider": "Google Cloud",
                "difficulty": "Advanced",
                "cost_usd": 200,
                "duration_months": 4,
                "recognition_score": 0.92,
                "covers": ["data engineering", "big data", "gcp"],
            },
        ],
        # Civil/Structural Engineering
        "civil": [
            {
                "certification": "Professional Engineer (PE) License",
                "provider": "NCEES",
                "difficulty": "Advanced",
                "cost_usd": 400,
                "duration_months": 6,
                "recognition_score": 0.98,
                "covers": ["civil engineering", "structural", "professional license"],
            },
            {
                "certification": "AutoCAD Certified Professional",
                "provider": "Autodesk",
                "difficulty": "Intermediate",
                "cost_usd": 150,
                "duration_months": 2,
                "recognition_score": 0.85,
                "covers": ["autocad", "cad", "drafting", "design"],
            },
            {
                "certification": "Project Management Professional (PMP)",
                "provider": "PMI",
                "difficulty": "Advanced",
                "cost_usd": 555,
                "duration_months": 6,
                "recognition_score": 0.94,
                "covers": ["project management", "construction management"],
            },
            {
                "certification": "LEED Green Associate",
                "provider": "USGBC",
                "difficulty": "Beginner",
                "cost_usd": 250,
                "duration_months": 2,
                "recognition_score": 0.80,
                "covers": ["green building", "sustainable design", "environmental"],
            },
        ],
        # Management/PM roles
        "management": [
            {
                "certification": "PMP (Project Management Professional)",
                "provider": "PMI",
                "difficulty": "Advanced",
                "cost_usd": 555,
                "duration_months": 6,
                "recognition_score": 0.94,
                "covers": ["project management", "agile", "leadership"],
            },
            {
                "certification": "Certified ScrumMaster (CSM)",
                "provider": "Scrum Alliance",
                "difficulty": "Beginner",
                "cost_usd": 1000,
                "duration_months": 1,
                "recognition_score": 0.85,
                "covers": ["scrum", "agile", "project management"],
            },
        ],
    }

    def __init__(self) -> None:
        skills_path = settings.DATASETS_DIR / "skills_master.csv"
        certs_path = settings.DATASETS_DIR / "certification_master.csv"

        skills_df = pd.read_csv(skills_path)
        certs_df = pd.read_csv(certs_path)

        # Build skill_name → skill_id lookup (median aggregation for duplicates)
        skills_df["skill_lower"] = skills_df["skill_name"].str.lower().str.strip()
        skills_df["skill_id"] = skills_df["skill_id"].astype(str).str.strip()
        
        # Keep first occurrence per skill name (consistent with other engines)
        skill_map = (
            skills_df.drop_duplicates(subset=["skill_lower"], keep="first")
            .set_index("skill_lower")["skill_id"]
            .to_dict()
        )
        # Type cast to fix Hashable->str type error
        self._name_to_id: dict[str, str] = {str(k): str(v) for k, v in skill_map.items()}

        # Normalize cert data
        certs_df["related_skill_id"] = certs_df["related_skill_id"].astype(str).str.strip()
        certs_df["global_recognition_score"] = pd.to_numeric(
            certs_df["global_recognition_score"], errors="coerce"
        ).fillna(0)

        # Deduplicate: keep highest-recognition entry per (cert_name, related_skill_id)
        self.certs = (
            certs_df.sort_values("global_recognition_score", ascending=False)
            .drop_duplicates(subset=["certification_name", "related_skill_id"], keep="first")
            .reset_index(drop=True)
        )
        
        logger.info(
            "CertificationEngine: %d skill mappings, %d certifications loaded",
            len(self._name_to_id),
            len(self.certs),
        )

    def suggest(self, missing_skills: list[str], role_name: str | None = None) -> dict:
        """
        Recommend certifications using multi-strategy approach:
        1. Exact skill-to-cert mapping (from CSV)
        2. Fuzzy matching for skill variations
        3. Popular certifications based on missing skill domains
        4. Always include top global certifications relevant to role

        Parameters
        ----------
        missing_skills : list[str]
            Skills the candidate is missing for the target role
        role_name : str | None
            Target role name (used for role-specific recommendations)

        Returns
        -------
        dict
            suggestions, unique cert names, count
        """
        suggestions: list[dict] = []
        seen_certs: set[str] = set()

        # ── Strategy 1: Exact + Fuzzy skill matching ───────────────────
        for skill in missing_skills:
            skill_lower = skill.lower().strip()
            
            # Try exact match first
            skill_id = self._name_to_id.get(skill_lower)
            
            # Try fuzzy matching if exact fails
            if skill_id is None:
                skill_id = self._fuzzy_skill_lookup(skill_lower)
            
            if skill_id:
                certs_found = self._get_certs_for_skill_id(skill_id, skill)
                for cert in certs_found:
                    cert_key = cert["certification"]
                    if cert_key not in seen_certs:
                        seen_certs.add(cert_key)
                        suggestions.append(cert)

        # ── Strategy 2: Add popular certifications for role domain ─────
        # Determine role category and get domain-specific certs
        role_category = self._get_role_category(role_name)
        domain_certs = self.POPULAR_CERTIFICATIONS.get(role_category, [])
        
        # Also check skill-based domain matching
        skill_domains = self._extract_domains(missing_skills)
        
        for pop_cert in domain_certs:
            cert_name = pop_cert["certification"]
            if cert_name in seen_certs:
                continue  # Already suggested
            
            # Check if this cert is relevant to missing skills OR role
            cert_covers = set(c.lower() for c in pop_cert["covers"])
            if cert_covers & skill_domains or len(suggestions) < 3:
                seen_certs.add(cert_name)
                suggestions.append({
                    "certification": cert_name,
                    "provider": pop_cert["provider"],
                    "for_skill": "Multiple skills" if cert_covers & skill_domains else role_name,
                    "difficulty": pop_cert["difficulty"],
                    "cost_usd": pop_cert["cost_usd"],
                    "duration_months": pop_cert["duration_months"],
                    "recognition_score": pop_cert["recognition_score"],
                    "reason": f"Recommended for {role_name}",
                })

        # ── Strategy 3: Fallback to management certs if still low count ──
        if len(suggestions) < 3:
            # Add universal management certifications
            for pop_cert in self.POPULAR_CERTIFICATIONS.get("management", []):
                cert_name = pop_cert["certification"]
                if cert_name not in seen_certs:
                    seen_certs.add(cert_name)
                    suggestions.append({
                        "certification": cert_name,
                        "provider": pop_cert["provider"],
                        "for_skill": "Career advancement",
                        "difficulty": pop_cert["difficulty"],
                        "cost_usd": pop_cert["cost_usd"],
                        "duration_months": pop_cert["duration_months"],
                        "recognition_score": pop_cert["recognition_score"],
                        "reason": "Valuable for career growth",
                    })
                    if len(suggestions) >= 5:
                        break

        # ── Priority sorting: recognition score (desc) → cost (asc) ───
        suggestions.sort(
            key=lambda x: (-x["recognition_score"], x["cost_usd"])
        )

        # Limit to top 10 most relevant
        suggestions = suggestions[:10]

        unique_certs = [s["certification"] for s in suggestions]

        return {
            "suggestions": suggestions,
            "unique_certifications": unique_certs,
            "count": len(suggestions),
        }

    def _fuzzy_skill_lookup(self, skill_lower: str) -> str | None:
        """
        Fuzzy match skill name variations.
        
        Examples:
        - "python" matches "python", "python 3", "python3"
        - "node.js" matches "nodejs", "node js", "node.js"
        - "ci/cd" matches "cicd", "ci cd", "ci/cd"
        """
        # Normalize: remove spaces, dots, slashes, hyphens
        skill_normalized = (
            skill_lower.replace(" ", "")
            .replace(".", "")
            .replace("/", "")
            .replace("-", "")
        )
        
        # Try exact match on normalized version
        for db_skill, skill_id in self._name_to_id.items():
            db_normalized = (
                db_skill.replace(" ", "")
                .replace(".", "")
                .replace("/", "")
                .replace("-", "")
            )
            if skill_normalized == db_normalized:
                return skill_id
        
        # Try substring matching (skill in db_skill or vice versa)
        for db_skill, skill_id in self._name_to_id.items():
            if len(skill_lower) >= 4:  # Only for meaningful length
                if skill_lower in db_skill or db_skill in skill_lower:
                    return skill_id
        
        return None

    def _get_certs_for_skill_id(
        self, skill_id: str, skill_name: str
    ) -> list[dict]:
        """Get all certifications for a given skill_id."""
        matches = self.certs[self.certs["related_skill_id"] == skill_id]
        certs = []
        
        for _, row in matches.iterrows():
            certs.append({
                "certification": row["certification_name"],
                "provider": row["provider"],
                "for_skill": skill_name,
                "difficulty": row["difficulty_level"],
                "cost_usd": int(row["average_cost"]),
                "duration_months": int(row["duration_months"]),
                "recognition_score": round(float(row["global_recognition_score"]), 2),
            })
        
        return certs

    def _extract_domains(self, skills: list[str]) -> set[str]:
        """
        Extract domain keywords from skill list.
        
        Examples:
        - ["python", "tensorflow", "keras"] → {"machine learning", "ai", "python"}
        - ["kubernetes", "docker", "aws"] → {"cloud", "devops", "kubernetes", "aws"}
        """
        domains: set[str] = set()
        
        # Direct skill additions
        for skill in skills:
            skill_lower = skill.lower().strip()
            domains.add(skill_lower)
            
            # Add broader domain categories
            if skill_lower in {"python", "java", "javascript", "c++", "go", "rust"}:
                domains.add("programming")
            
            if skill_lower in {"tensorflow", "pytorch", "keras", "scikit-learn"}:
                domains.add("machine learning")
                domains.add("ai")
            
            if skill_lower in {"aws", "azure", "gcp", "google cloud"}:
                domains.add("cloud")
            
            if skill_lower in {"docker", "kubernetes", "k8s", "jenkins", "terraform"}:
                domains.add("devops")
            
            if skill_lower in {"react", "angular", "vue.js", "vue"}:
                domains.add("frontend")
            
            if skill_lower in {"node.js", "express", "django", "flask", "spring"}:
                domains.add("backend")
            
            if skill_lower in {"pandas", "numpy", "spark", "hadoop"}:
                domains.add("data engineering")
                domains.add("big data")
            
            if skill_lower in {"scrum", "agile", "kanban"}:
                domains.add("project management")
        
        return domains

    def _get_role_category(self, role_name: str | None) -> str:
        """
        Map role name to certification category.
        
        Categories:
        - tech: Software, DevOps, Cloud, Backend, Frontend
        - data_science: Data Scientist, ML Engineer, Data Analyst
        - civil: Civil Engineer, Structural Engineer, Construction
        - management: Product Manager, Project Manager, Scrum Master
        """
        if not role_name:
            return "tech"  # Default fallback
        
        role_lower = role_name.lower()
        
        # Civil/Structural Engineering
        if any(kw in role_lower for kw in ["civil", "structural", "construction", "architect"]):
            # Check if it's software architect vs building architect
            if "software" in role_lower or "cloud" in role_lower or "solution" in role_lower:
                return "tech"
            return "civil"
        
        # Data Science/ML/Analytics
        if any(kw in role_lower for kw in ["data", "ml", "machine learning", "analyst", "scientist"]):
            return "data_science"
        
        # Management/PM
        if any(kw in role_lower for kw in ["manager", "scrum", "product owner", "agile coach"]):
            return "management"
        
        # Default to tech for all software-related roles
        return "tech"

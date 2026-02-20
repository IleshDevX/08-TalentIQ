"""
TalentIQ — Central Orchestration Service ("The Brain")
Connects ALL engines into a single end-to-end analysis pipeline.

Redesigned Pipeline (v3 — Stabilized):
    1.  Extract text              (FileProcessingEngine)
    2.  Preprocess                (TextPreprocessingEngine)
    3.  Extract skills/info       (InformationExtractionEngine)
    4.  Normalize skills          (SkillNormalizationEngine)
    5.  Generate resume embedding (via SemanticMatchingEngine)
    6.  Match job roles           (SemanticMatchingEngine → FAISS)
    7.  Resolve target role       (user-selected or top semantic match)
    8.  Resolve JD                (user-provided or default from DB)
    9.  Compute ATS score         (ATSScoringEngine)
    10. JD vs Resume comparison   (JDComparisonEngine)
    11. ATS simulation scan       (ATSSimulationEngine)
    12. Detect skill gaps         (SkillGapEngine)
    13. Analyze soft skills       (SoftSkillEngine)
    14. Analyze resume writing    (ResumeImprovementEngine)
    15. Calculate industry demand (IndustryInsightEngine)
    16. Suggest certifications    (CertificationEngine)
    17. Generate explanation      (RoleExplanationEngine)
    18. Suggest career paths      (CareerPathEngine)
    19. Compile final report      (FeedbackEngine)

Error Handling:
    Every engine call is wrapped in try/except. If an engine fails, a
    safe default is used so the pipeline never crashes entirely.
"""

from __future__ import annotations

import logging
import os
import shutil
import time
import traceback

from fastapi import UploadFile

from app.config import settings
from app.core import vector_store

# Engines
from app.engines.file_processing_engine import FileProcessingEngine
from app.engines.preprocessing_engine import TextPreprocessingEngine
from app.engines.information_extraction_engine import InformationExtractionEngine
from app.engines.skill_normalization_engine import SkillNormalizationEngine
from app.engines.semantic_matching_engine import SemanticMatchingEngine
from app.engines.ats_scoring_engine import ATSScoringEngine
from app.engines.skill_gap_engine import SkillGapEngine
from app.engines.soft_skill_engine import SoftSkillEngine
from app.engines.resume_improvement_engine import ResumeImprovementEngine
from app.engines.industry_insight_engine import IndustryInsightEngine
from app.engines.certification_engine import CertificationEngine
from app.engines.role_explanation_engine import RoleExplanationEngine
from app.engines.career_path_engine import CareerPathEngine
from app.engines.feedback_engine import FeedbackEngine
from app.engines.jd_comparison_engine import JDComparisonEngine
from app.engines.ats_simulation_engine import ATSSimulationEngine

logger = logging.getLogger(__name__)

# Upload directory — created on demand
UPLOAD_DIR = os.path.join(str(settings.BASE_DIR), "uploads")


def _safe_call(engine_name: str, fn, *args, **kwargs) -> dict:
    """Call an engine function and return a safe fallback on failure."""
    try:
        result = fn(*args, **kwargs)
        return result if isinstance(result, dict) else {}
    except Exception as exc:
        logger.error(
            "Engine [%s] failed: %s\n%s",
            engine_name, exc, traceback.format_exc(),
        )
        return {"_error": f"{engine_name} failed: {exc}"}


class AnalysisService:
    """The Brain — orchestrates every TalentIQ engine in one call."""

    def __init__(self) -> None:
        self.file_processor = FileProcessingEngine()
        self.preprocessor = TextPreprocessingEngine()
        self.extractor = InformationExtractionEngine()
        self.normalizer = SkillNormalizationEngine()
        self.matcher = SemanticMatchingEngine()
        self.ats_scorer = ATSScoringEngine()
        self.skill_gap = SkillGapEngine()
        self.soft_skill = SoftSkillEngine()
        self.improvement = ResumeImprovementEngine()
        self.industry = IndustryInsightEngine()
        self.certifications = CertificationEngine()
        self.explainer = RoleExplanationEngine()
        self.career_path = CareerPathEngine()
        self.feedback = FeedbackEngine()
        self.jd_comparer = JDComparisonEngine()
        self.ats_simulator = ATSSimulationEngine()

        logger.info("AnalysisService initialised — all 19 engines ready.")

    # ------------------------------------------------------------------
    # Public API — from UploadFile
    # ------------------------------------------------------------------

    async def process(
        self,
        file: UploadFile,
        target_role: str | None = None,
        jd_text: str | None = None,
    ) -> dict:
        filename = file.filename or "resume"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return {
                "error": (
                    f"Invalid file type '{ext}'. "
                    f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                ),
            }

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        logger.info("process: saved %s → %s", filename, file_path)
        return self.analyze_file(file_path, target_role=target_role, jd_text=jd_text)

    # ------------------------------------------------------------------
    # Public API — from file path
    # ------------------------------------------------------------------

    def analyze_file(
        self,
        file_path: str,
        top_k: int = 5,
        target_role: str | None = None,
        jd_text: str | None = None,
    ) -> dict:
        logger.info("analyze_file: %s (target_role=%s)", file_path, target_role)
        raw_text = self.file_processor.extract_text(file_path)
        return self._run_pipeline(
            raw_text, top_k=top_k, target_role=target_role, jd_text=jd_text,
        )

    # ------------------------------------------------------------------
    # Public API — from raw text
    # ------------------------------------------------------------------

    def analyze_text(
        self,
        raw_text: str,
        top_k: int = 5,
        target_role: str | None = None,
        jd_text: str | None = None,
    ) -> dict:
        return self._run_pipeline(
            raw_text, top_k=top_k, target_role=target_role, jd_text=jd_text,
        )

    # ------------------------------------------------------------------
    # Internal pipeline
    # ------------------------------------------------------------------

    def _run_pipeline(
        self,
        raw_text: str,
        top_k: int = 5,
        target_role: str | None = None,
        jd_text: str | None = None,
    ) -> dict:
        t0 = time.perf_counter()
        errors: list[str] = []

        # ── 1-2. Preprocess ──────────────────────────────────────
        try:
            cleaned = self.preprocessor.clean(raw_text)
            tokens = self.preprocessor.tokenize(cleaned)
        except Exception as exc:
            logger.error("Preprocessing failed: %s", exc)
            cleaned = raw_text
            tokens = raw_text.split()
            errors.append(f"Preprocessing: {exc}")

        # ── 3. Information extraction ────────────────────────────
        try:
            profile = self.extractor.extract(raw_text)
        except Exception as exc:
            logger.error("Information extraction failed: %s", exc)
            profile = {
                "skills": [],
                "education": {"degrees": []},
                "experience": {"years_mentioned": [], "max_years": 0},
                "keywords": [],
            }
            errors.append(f"InfoExtraction: {exc}")

        raw_skills = profile.get("skills", [])
        education = profile.get("education", {"degrees": []})
        experience = profile.get("experience", {"years_mentioned": [], "max_years": 0})
        keywords = profile.get("keywords", [])
        max_years = experience.get("max_years", 0) if isinstance(experience, dict) else 0

        # Ensure education is a dict with "degrees" key
        if isinstance(education, list):
            education = {"degrees": education}
        elif not isinstance(education, dict):
            education = {"degrees": []}

        # ── 4. Normalize skills ──────────────────────────────────
        try:
            normalized_skills = self.normalizer.normalize(raw_skills)
        except Exception as exc:
            logger.error("Skill normalization failed: %s", exc)
            normalized_skills = raw_skills
            errors.append(f"SkillNorm: {exc}")

        # ── 5-6. Semantic role matching (HYBRID v2.0) ────────────
        # Pass candidate data to enable skill/experience/keyword boosting
        role_matches = _safe_call(
            "SemanticMatching",
            self.matcher.match,
            resume_text=raw_text,
            candidate_skills=normalized_skills,
            candidate_experience=experience.get("max_years", 0) if isinstance(experience, dict) else 0,
            candidate_keywords=keywords,
            top_k=top_k,
        )
        top_roles = role_matches.get("top_roles", [])

        if not top_roles:
            return {
                "error": "No matching roles found.",
                "candidate_profile": {
                    "skills_raw": raw_skills,
                    "skills_normalized": normalized_skills,
                    "education": education,
                    "experience": experience,
                    "keywords": keywords,
                    "token_count": len(tokens),
                },
            }

        # ── 7. Resolve target role ───────────────────────────────
        if target_role:
            role_name = target_role
            semantic_score = 0.0
            for r in top_roles:
                if r["role_name"].lower() == target_role.lower():
                    semantic_score = r["score"]
                    break
            if semantic_score == 0.0:
                semantic_score = top_roles[0]["score"] * 0.7
        else:
            role_name = top_roles[0]["role_name"]
            semantic_score = top_roles[0]["score"]

        role_obj = self._find_role(role_name)
        role_min_exp = int(role_obj.years_experience_min) if role_obj else 0
        role_max_exp = int(role_obj.years_experience_max) if role_obj else 0
        role_id = role_obj.role_id if role_obj else ""

        # ── 8. Resolve JD ────────────────────────────────────────
        if not jd_text or not jd_text.strip():
            jd_text = vector_store.get_default_jd(role_name)
            jd_source = "default"
        else:
            jd_source = "user_provided"

        # ── Get role skills from DB ──────────────────────────────
        role_required_skills = vector_store.get_role_skills(role_name)
        role_keywords = vector_store.get_role_keywords(role_name)
        if not role_required_skills:
            role_required_skills = self._get_fallback_skills(role_name)

        # ── 9. ATS score ─────────────────────────────────────────
        ats_result = _safe_call(
            "ATSScoring",
            self.ats_scorer.calculate,
            candidate_skills=normalized_skills,
            role_required_skills=role_required_skills,
            candidate_experience=max_years,
            role_min_exp=role_min_exp,
            semantic_score=semantic_score,
            role_max_exp=role_max_exp,
        )

        # ── 10. JD comparison ────────────────────────────────────
        jd_comparison: dict = {}
        if jd_text:
            jd_comparison = _safe_call(
                "JDComparison",
                self.jd_comparer.compare,
                resume_text=raw_text,
                jd_text=jd_text,
                resume_skills=normalized_skills,
            )

        # ── 11. ATS simulation ───────────────────────────────────
        ats_simulation = _safe_call(
            "ATSSimulation",
            self.ats_simulator.simulate,
            resume_text=raw_text,
            target_keywords=role_required_skills + role_keywords,
        )

        # ── 12. Skill gap ────────────────────────────────────────
        gap_result = _safe_call(
            "SkillGap",
            self.skill_gap.identify,
            candidate_skills=normalized_skills,
            role_required_skills=role_required_skills,
        )

        # ── 13. Soft skills ──────────────────────────────────────
        soft_result = _safe_call("SoftSkill", self.soft_skill.analyze, raw_text)

        # ── 14. Resume improvements (v2.0: role-aware) ───────────
        improvement_result = _safe_call(
            "ResumeImprovement",
            self.improvement.analyze,
            text=raw_text,
            candidate_skills=normalized_skills,
            role_required_skills=role_required_skills,
            role_name=role_name,
            skill_match_percent=semantic_score,
        )

        # ── 15. Industry alignment ───────────────────────────────
        industry_result = _safe_call(
            "IndustryInsight",
            self.industry.calculate_alignment,
            normalized_skills,
            role_required_skills,
        )

        # ── 16. Certifications ───────────────────────────────────
        cert_result = _safe_call(
            "Certifications",
            self.certifications.suggest,
            gap_result.get("missing_skills", []),
            role_name,
        )

        # ── 17. Role explanation ─────────────────────────────────
        explanation = _safe_call(
            "RoleExplanation",
            self.explainer.generate,
            role_name=role_name,
            overlap_percent=gap_result.get("coverage_percent", 0),
            experience_years=max_years,
            matched_skills=gap_result.get("matched_skills", []),
            missing_skills=gap_result.get("missing_skills", []),
            semantic_score=semantic_score,
            ats_score=ats_result.get("final_score", 0),
        )

        # ── 18. Career paths ─────────────────────────────────────
        career_result = _safe_call(
            "CareerPath", self.career_path.suggest, str(role_id),
        )

        # ── 19. Compile final report ─────────────────────────────
        elapsed = round(time.perf_counter() - t0, 3)

        report = self.feedback.compile(
            ats_score=ats_result,
            skill_gap=gap_result,
            soft_skill=soft_result,
            improvements=improvement_result,
            industry_alignment=industry_result,
            certifications=cert_result,
            explanation=explanation,
            career_paths=career_result,
            role_matches=role_matches,
            candidate_profile={
                "skills_raw": raw_skills,
                "skills_normalized": normalized_skills,
                "education": education,
                "experience": experience,
                "keywords": keywords,
                "token_count": len(tokens),
            },
        )

        report["jd_comparison"] = jd_comparison
        report["ats_simulation"] = ats_simulation

        report["meta"] = {
            "pipeline_time_seconds": elapsed,
            "engines_executed": 19,
            "target_role": role_name,
            "jd_source": jd_source,
            "total_roles_available": len(vector_store.get_roles()),
        }

        # Include any engine errors for debugging
        if errors:
            report["meta"]["engine_warnings"] = errors

        logger.info(
            "Pipeline complete in %.3f s — target role: %s (jd_source: %s)",
            elapsed, role_name, jd_source,
        )
        return report

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_role(role_name: str):
        for r in vector_store.get_roles():
            if r.role_name.lower() == role_name.lower():
                return r
        return None

    @staticmethod
    def _get_fallback_skills(role_name: str) -> list[str]:
        FALLBACK: dict[str, list[str]] = {
            "software engineer": [
                "python", "java", "javascript", "sql", "git", "docker",
                "rest api", "data structures", "algorithms", "linux", "agile",
            ],
            "backend developer": [
                "python", "node.js", "sql", "postgresql", "docker",
                "rest api", "redis", "git", "linux", "microservices",
            ],
            "frontend developer": [
                "javascript", "typescript", "react", "html", "css",
                "git", "responsive design", "webpack", "testing",
            ],
            "devops engineer": [
                "docker", "kubernetes", "aws", "terraform", "linux",
                "ci/cd", "git", "python", "ansible", "monitoring",
            ],
            "ml engineer": [
                "python", "tensorflow", "pytorch", "scikit-learn",
                "docker", "mlflow", "sql", "deep learning",
            ],
            "data analyst": [
                "sql", "python", "excel", "tableau", "power bi",
                "pandas", "statistics", "data visualization",
            ],
        }
        return FALLBACK.get(role_name.lower(), [
            "python", "sql", "git", "docker", "communication",
        ])

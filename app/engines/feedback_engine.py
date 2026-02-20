"""
TalentIQ — Engine 16: Feedback Aggregation Engine
Compiles all intelligence outputs into a single structured response.

Key names are standardized to match exactly what the Streamlit dashboard expects:
    ats_score, skill_gap, soft_skill, improvements, industry_alignment,
    certifications, explanation, role_matches, career_paths, candidate_profile
"""

from __future__ import annotations


class FeedbackEngine:
    """Aggregate all engine outputs into one unified report."""

    def compile(
        self,
        ats_score: dict,
        skill_gap: dict,
        soft_skill: dict,
        improvements: dict,
        industry_alignment: dict,
        certifications: dict,
        explanation: dict,
        career_paths: dict | None = None,
        role_matches: dict | None = None,
        candidate_profile: dict | None = None,
    ) -> dict:
        """
        Merge every engine's output into a final report.

        Key names match the Streamlit dashboard expectations exactly.

        Returns
        -------
        dict
            The unified TalentIQ analysis report.
        """
        report: dict = {
            "ats_score": ats_score,
            "skill_gap": skill_gap,
            "soft_skill": soft_skill,
            "improvements": improvements,
            "industry_alignment": industry_alignment,
            "certifications": certifications,
            "explanation": explanation,
        }

        if role_matches is not None:
            report["role_matches"] = role_matches

        if career_paths is not None:
            report["career_paths"] = career_paths

        if candidate_profile is not None:
            report["candidate_profile"] = candidate_profile

        # Summary for the dashboard hero card
        report["summary"] = self._build_summary(ats_score, skill_gap, soft_skill)

        return report

    @staticmethod
    def _build_summary(ats: dict, gap: dict, soft: dict) -> dict:
        """Derive a top-level summary from key scores."""
        return {
            "overall_score": ats.get("final_score", 0),
            "skill_coverage": gap.get("coverage_percent", 0),
            "missing_skill_count": gap.get("missing_count", 0),
            "soft_skill_categories": len(soft.get("categories", [])),
            "soft_skill_score": soft.get("composite_score", 0),
        }

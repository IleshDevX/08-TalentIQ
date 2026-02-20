"""
TalentIQ — Engine 15: Role Explanation Engine (Explainable AI)
Generates human-readable explanations for role-fit recommendations.

Output contract:
    verdict: str          — human-readable verdict sentence
    verdict_key: str      — programmatic key (strong_match | moderate_match | growth_opportunity)
    reasoning: list[str]  — individual explanation sentences
    role_name: str
    highlights: dict
"""

from __future__ import annotations


class RoleExplanationEngine:
    """Produce natural-language role-fit explanations."""

    def generate(
        self,
        role_name: str,
        overlap_percent: float,
        experience_years: int | float,
        matched_skills: list[str] | None = None,
        missing_skills: list[str] | None = None,
        semantic_score: float | None = None,
        ats_score: float | None = None,
    ) -> dict:
        """
        Build an explainable summary for a role match.

        Returns
        -------
        dict
            verdict (str), verdict_key (str), reasoning (list[str]),
            role_name, highlights
        """
        matched_skills = matched_skills or []
        missing_skills = missing_skills or []

        try:
            # ── Build reasoning sentences ───────────────────────────
            reasoning: list[str] = []

            reasoning.append(
                f"You match {overlap_percent:.0f}% of the required skills for {role_name}."
            )
            
            # More realistic experience alignment messaging
            if experience_years == 0:
                reasoning.append("No professional experience detected — entry-level roles recommended.")
            elif overlap_percent >= 60:
                reasoning.append(
                    f"Your {experience_years} year{'s' if experience_years != 1 else ''} "
                    f"of experience align well with this role."
                )
            else:
                reasoning.append(
                    f"You have {experience_years} year{'s' if experience_years != 1 else ''} "
                    f"of experience, but your skills need development for this specific role."
                )

            if semantic_score is not None:
                pct = semantic_score * 100
                reasoning.append(f"Semantic profile similarity: {pct:.1f}%.")

            if ats_score is not None:
                reasoning.append(f"Overall ATS compatibility score: {ats_score:.1f}/100.")

            if matched_skills:
                top = ", ".join(matched_skills[:5])
                reasoning.append(f"Key matching skills: {top}.")

            if missing_skills:
                gaps = ", ".join(missing_skills[:5])
                reasoning.append(f"Skills to develop: {gaps}.")

            # ── Verdict ─────────────────────────────────────────────
            if overlap_percent >= 80:
                verdict_key = "strong_match"
                verdict = "Strong fit — you meet most of the role requirements."
            elif overlap_percent >= 50:
                verdict_key = "moderate_match"
                verdict = "Moderate fit — some upskilling would strengthen your profile."
            else:
                verdict_key = "growth_opportunity"
                verdict = "Growth opportunity — targeted learning can bridge the gap."

            return {
                "role_name": role_name,
                "verdict": verdict,
                "verdict_key": verdict_key,
                "reasoning": reasoning,
                "explanation": " ".join(reasoning),
                "highlights": {
                    "skill_overlap_percent": round(overlap_percent, 1),
                    "experience_years": experience_years,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                    "semantic_score": semantic_score,
                    "ats_score": ats_score,
                },
            }
        except Exception:
            return {
                "role_name": role_name,
                "verdict": "Unable to generate explanation.",
                "verdict_key": "unknown",
                "reasoning": [],
                "explanation": "",
                "highlights": {},
            }

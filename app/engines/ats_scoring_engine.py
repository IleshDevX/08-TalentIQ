"""
TalentIQ — Engine 8: ATS Scoring Engine (Enhanced v2.0)
Calculates an explainable, structured hiring score by combining:
    1. Skill coverage        (50 % weight) — with fuzzy matching
    2. Experience alignment  (20 % weight) — graduated curve
    3. Semantic similarity   (30 % weight) — from embeddings

Enhanced skill scoring includes:
  - Exact matches: 100% credit
  - Partial matches (substring): 70% credit
  - Related skills (candidates skills not in role but valuable): 30% credit bonus
"""

from __future__ import annotations


class ATSScoringEngine:
    """Explainable ATS score with enhanced skill matching."""

    WEIGHT_SKILL: float = 0.50
    WEIGHT_EXP: float = 0.20
    WEIGHT_SEMANTIC: float = 0.30

    def calculate(
        self,
        candidate_skills: list[str],
        role_required_skills: list[str],
        candidate_experience: int | float,
        role_min_exp: int | float,
        semantic_score: float,
        role_max_exp: int | float = 0,
    ) -> dict:
        """
        Compute a weighted ATS score (0–100) with enhanced skill matching.

        Returns
        -------
        dict
            final_score, breakdown {skill_score, experience_score, semantic_score},
            matched_skills, missing_skills, weights
        """
        try:
            # ── 1. Enhanced Skill Scoring (0-100) ────────────────────
            skill_result = self._compute_skill_score(
                candidate_skills, role_required_skills
            )
            skill_score = skill_result["score"]
            matched_skills = skill_result["matched"]
            missing_skills = skill_result["missing"]

            # ── 2. Experience alignment (0-100) ──────────────────────
            exp_score = self._compute_experience_score(
                candidate_experience, role_min_exp, role_max_exp
            )

            # ── 3. Semantic similarity (0-100) ───────────────────────
            sem_score = max(0.0, min(float(semantic_score), 1.0)) * 100

            # ── Weighted final score (0-100) ─────────────────────────
            final_score = (
                skill_score * self.WEIGHT_SKILL
                + exp_score * self.WEIGHT_EXP
                + sem_score * self.WEIGHT_SEMANTIC
            )

            return {
                "final_score": round(final_score, 2),
                "breakdown": {
                    "skill_score": round(skill_score, 2),
                    "experience_score": round(exp_score, 2),
                    "semantic_score": round(sem_score, 2),
                },
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "weights": {
                    "skill": self.WEIGHT_SKILL,
                    "experience": self.WEIGHT_EXP,
                    "semantic": self.WEIGHT_SEMANTIC,
                },
            }
        except Exception:
            return {
                "final_score": 0,
                "breakdown": {
                    "skill_score": 0,
                    "experience_score": 0,
                    "semantic_score": 0,
                },
                "matched_skills": [],
                "missing_skills": [],
                "weights": {
                    "skill": self.WEIGHT_SKILL,
                    "experience": self.WEIGHT_EXP,
                    "semantic": self.WEIGHT_SEMANTIC,
                },
            }

    # ------------------------------------------------------------------
    # Enhanced Skill Scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_skill_score(
        candidate_skills: list[str],
        role_required_skills: list[str],
    ) -> dict:
        """
        Enhanced skill scoring with fuzzy matching and partial credit.

        Scoring logic:
          - Exact match: 1.0 credit per skill
          - Partial match (substring): 0.7 credit per skill
          - Bonus for extra relevant skills: up to +10% bonus

        Returns dict with score (0-100), matched list, missing list.
        """
        if not role_required_skills:
            return {"score": 100.0, "matched": [], "missing": []}

        cand_set = {s.lower().strip() for s in candidate_skills}
        role_set = {s.lower().strip() for s in role_required_skills}

        exact_matches = cand_set & role_set
        matched_list = sorted(exact_matches)
        missing_list = sorted(role_set - cand_set)

        # Calculate skill credits
        total_credits = 0.0
        unmatched_role = role_set - exact_matches

        # 1. Exact matches: full credit
        total_credits += len(exact_matches)

        # 2. Partial/fuzzy matches: 70% credit
        for role_skill in list(unmatched_role):
            for cand_skill in cand_set:
                if role_skill in cand_skill or cand_skill in role_skill:
                    # Substring match
                    total_credits += 0.7
                    if role_skill in missing_list:
                        missing_list.remove(role_skill)
                    if cand_skill not in matched_list:
                        matched_list.append(cand_skill)
                    unmatched_role.discard(role_skill)
                    break

        # 3. Base coverage score
        coverage_score = (total_credits / len(role_set)) * 100

        # 4. Bonus for additional relevant skills (up to +10%)
        extra_skills = len(cand_set - role_set - exact_matches)
        bonus = min(extra_skills * 2, 10)  # 2% per extra skill, max 10%

        final_score = min(coverage_score + bonus, 100.0)

        return {
            "score": final_score,
            "matched": sorted(matched_list),
            "missing": sorted(missing_list),
        }

    # ------------------------------------------------------------------
    # Experience scoring helper
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_experience_score(
        candidate_exp: int | float,
        role_min: int | float,
        role_max: int | float,
    ) -> float:
        """
        Graduated experience scoring (0-100) using the role's min/max range.

        Scoring curve (conservative - rewards experience above minimum):
          - 0 years                        → 5   (minimal baseline)
          - Below min (partially)          → 5 + (candidate/min) * 10  (up to 15)
          - Exactly at min                 → 15  (just meeting requirement)
          - Between min and ideal midpoint → 15 → 70  (strong ramp)
          - At ideal (midpoint of range)   → 70
          - Between ideal and max          → 70 → 90  (continues to improve)
          - At or above max                → 90  (cap)
        """
        candidate_exp = max(0, float(candidate_exp))
        role_min = max(0, float(role_min))
        role_max = max(role_min, float(role_max)) if role_max > 0 else role_min * 2

        # If role requires 0 experience, give credit proportional to any exp
        if role_min <= 0:
            if candidate_exp == 0:
                return 50.0
            return min(50.0 + candidate_exp * 5, 90.0)

        # If candidate has 0 experience
        if candidate_exp <= 0:
            return 5.0

        # Below minimum
        if candidate_exp < role_min:
            ratio = candidate_exp / role_min
            return 5.0 + ratio * 10.0          # 5 → 15

        # Ideal = midpoint of min-max range
        ideal = (role_min + role_max) / 2

        # At or around min
        if candidate_exp <= role_min:
            return 15.0

        # Between min and ideal
        if candidate_exp <= ideal:
            progress = (candidate_exp - role_min) / max(ideal - role_min, 1)
            return 15.0 + progress * 55.0       # 15 → 70

        # Between ideal and max
        if candidate_exp <= role_max:
            progress = (candidate_exp - ideal) / max(role_max - ideal, 1)
            return 70.0 + progress * 20.0       # 70 → 90

        # Above max — over-qualification plateau
        return 90.0

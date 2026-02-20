"""
TalentIQ — Engine 13: Industry Demand Insight Engine
Measures skill-set alignment with current market demand.

Output contract (augmented):
    alignment_score: float
    aligned_skills: list[str]   — candidate skills with high demand
    trending_skills: list[str]  — emerging skills the candidate should learn
    emerging_skill_count: int
    breakdown: list[dict]
"""

from __future__ import annotations

import logging

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

# Demand threshold for a skill to be considered "in high demand"
_HIGH_DEMAND_THRESHOLD = 50
# Number of trending skills to suggest
_MAX_TRENDING_SUGGESTIONS = 15


class IndustryInsightEngine:
    """Calculate market-demand alignment for a candidate's skills."""

    def __init__(self) -> None:
        csv_path = settings.DATASETS_DIR / "skills_master.csv"
        self._skills_df: pd.DataFrame | None = None
        self._skills_lookup: dict[str, dict] = {}

        try:
            df = pd.read_csv(csv_path)
            df["skill_lower"] = df["skill_name"].str.lower().str.strip()
            df["demand_score"] = pd.to_numeric(df["demand_score"], errors="coerce").fillna(0)
            df["global_trend_score"] = pd.to_numeric(
                df["global_trend_score"], errors="coerce"
            ).fillna(0)
            df["is_emerging"] = df["is_emerging"].str.strip().str.lower() == "yes"

            # ── Deduplicate using MEDIAN demand score (not MAX) ──────────
            # Skills appear with many different demand scores in CSV
            # Taking max gives 100 to everyone; median is more realistic
            deduped = (
                df.groupby("skill_lower", as_index=False)
                .agg({
                    "skill_name": "first",
                    "demand_score": "median",  # Use median, not max
                    "global_trend_score": "median",
                    "is_emerging": lambda x: x.mode()[0] if len(x.mode()) > 0 else False
                })
            )
            self._skills_df = deduped
            self._skills_lookup = {
                row["skill_lower"]: {
                    "demand_score": float(row["demand_score"]),
                    "global_trend": float(row["global_trend_score"]),
                    "is_emerging": bool(row["is_emerging"]),
                    "name": row["skill_lower"],
                }
                for _, row in deduped.iterrows()
            }
            logger.info("IndustryInsightEngine: loaded %d unique skills", len(self._skills_lookup))
        except Exception:
            logger.warning("Could not load skills_master.csv — industry insight will be limited")

    def calculate_alignment(
        self,
        candidate_skills: list[str],
        role_required_skills: list[str] | None = None,
    ) -> dict:
        """
        Score how well a candidate's skills match industry demand AND
        the target role's requirements.

        Scoring formula (0-100):
          - Role skill coverage   (40%): % of role skills the candidate has
          - Industry demand       (30%): average normalized demand of candidate skills
          - Skill recognition     (20%): % of candidate skills found in industry DB
          - Emerging skill bonus  (10%): % of candidate's recognized skills that are emerging

        Returns
        -------
        dict
            alignment_score, aligned_skills, trending_skills,
            emerging_skill_count, breakdown
        """
        try:
            breakdown: list[dict] = []
            scores: list[float] = []
            emerging_count = 0
            aligned_skills: list[str] = []
            candidate_set = {s.lower().strip() for s in candidate_skills}

            for skill in candidate_skills:
                key = skill.lower().strip()
                info = self._skills_lookup.get(key)
                if info:
                    demand = info["demand_score"]
                    trend = info["global_trend"]
                    is_emerging = info["is_emerging"]

                    scores.append(demand)
                    if is_emerging:
                        emerging_count += 1
                    if demand >= _HIGH_DEMAND_THRESHOLD:
                        aligned_skills.append(skill)

                    breakdown.append({
                        "skill": skill,
                        "demand_score": round(demand, 2),
                        "global_trend": round(trend, 2),
                        "is_emerging": is_emerging,
                    })
                else:
                    breakdown.append({
                        "skill": skill,
                        "demand_score": 0,
                        "global_trend": 0,
                        "is_emerging": False,
                    })

            # ── Component 1: Role Skill Coverage (35%) ───────────────
            # How many of the role's required skills does the candidate have?
            role_coverage = 0.0
            if role_required_skills:
                role_set = {s.lower().strip() for s in role_required_skills}
                matched_role = candidate_set & role_set
                role_coverage = (len(matched_role) / len(role_set) * 100) if role_set else 0.0
            else:
                # No role info — fall back to demand-based only (shift weight)
                role_coverage = 55.0  # neutral default (more lenient)

            # ── Component 2: Industry Demand Quality (30%) ───────────
            # Average normalized demand of candidate's recognized skills
            if scores:
                # More lenient normalization: 5-100 range → 0-100 (less penalty for lower scores)
                normalized = [(s - 5) / 95 * 100 for s in scores]
                demand_quality = sum(normalized) / len(normalized)
            else:
                demand_quality = 0.0

            # ── Component 3: Skill Recognition Rate (25%) ────────────
            # What fraction of candidate's skills exist in the industry DB?
            total_candidate = len(candidate_skills)
            recognized = len(scores)
            recognition_rate = (recognized / total_candidate * 100) if total_candidate > 0 else 0.0

            # ── Component 4: Emerging Skills Bonus (10%) ─────────────
            # What fraction of recognized skills are emerging?
            emerging_rate = (emerging_count / recognized * 100) if recognized > 0 else 0.0

            # ── Final weighted score (more lenient) ──────────────────
            # Reduced role coverage from 40% → 35%
            # Increased recognition from 20% → 25%
            # This rewards having relevant skills with slightly less penalty for gaps
            W_ROLE = 0.35
            W_DEMAND = 0.30
            W_RECOGNITION = 0.25
            W_EMERGING = 0.10

            alignment = (
                role_coverage * W_ROLE
                + demand_quality * W_DEMAND
                + recognition_rate * W_RECOGNITION
                + emerging_rate * W_EMERGING
            )
            
            # Apply baseline boost for non-zero scores (makes scoring more lenient)
            if alignment > 0:
                alignment = min(alignment + 5.0, 100.0)  # +5 point boost, capped at 100
            
            alignment = max(0.0, min(100.0, round(alignment, 2)))

            # Trending skills — top emerging skills the candidate DOESN'T have
            trending_skills = self._get_trending_skills(candidate_set)

            return {
                "alignment_score": alignment,
                "aligned_skills": sorted(aligned_skills),
                "trending_skills": trending_skills,
                "skills_matched": recognized,
                "skills_total": total_candidate,
                "emerging_skill_count": emerging_count,
                "breakdown": breakdown,
            }
        except Exception as exc:
            logger.exception("Industry alignment calculation failed: %s", exc)
            return {
                "alignment_score": 0,
                "aligned_skills": [],
                "trending_skills": [],
                "skills_matched": 0,
                "skills_total": len(candidate_skills),
                "emerging_skill_count": 0,
                "breakdown": [],
            }

    def _get_trending_skills(self, candidate_set: set[str]) -> list[str]:
        """Return top emerging/high-demand skills the candidate doesn't have."""
        trending: list[tuple[str, float]] = []
        for name, info in self._skills_lookup.items():
            if name not in candidate_set and info["is_emerging"] and info["demand_score"] > 30:
                trending.append((name, info["demand_score"]))

        # Sort by demand score descending
        trending.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in trending[:_MAX_TRENDING_SUGGESTIONS]]

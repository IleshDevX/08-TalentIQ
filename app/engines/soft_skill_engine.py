"""
TalentIQ — Engine 10: Soft Skill Analysis Engine
Detects leadership, communication, teamwork, and adaptability signals.

Performance-optimized: pre-builds a dict lookup instead of iterating 50K rows.
Score is normalized to 0-100 scale for consistent dashboard display.

Output contract:
    composite_score: float (0-100)
    categories: list[str]
    detected: list[str]     — unique soft-skill type names (for skill chips)
    matches: list[dict]
    match_count: int
"""

from __future__ import annotations

import logging

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

# Reasonable number of indicator matches for a top-tier resume
_STRONG_RESUME_THRESHOLD = 12


class SoftSkillEngine:
    """Score soft-skill signals from resume text."""

    def __init__(self) -> None:
        # Start with comprehensive built-in indicators (always available)
        self._indicators: dict[str, dict] = {}
        self._load_builtin_defaults()

        # Supplement with CSV data (add any phrases we don't already have)
        csv_path = settings.DATASETS_DIR / "soft_skill_indicators.csv"
        try:
            df = pd.read_csv(csv_path)
            df["phrase_lower"] = df["phrase_pattern"].str.lower().str.strip()
            df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0.5)
            df["confidence_score"] = pd.to_numeric(
                df["confidence_score"], errors="coerce"
            ).fillna(0.5)

            deduped = (
                df.sort_values("confidence_score", ascending=False)
                .drop_duplicates(subset=["phrase_lower", "soft_skill_type"], keep="first")
            )

            csv_added = 0
            for _, row in deduped.iterrows():
                phrase = row["phrase_lower"]
                if phrase and len(phrase) > 2 and phrase not in self._indicators:
                    self._indicators[phrase] = {
                        "type": str(row["soft_skill_type"]).strip(),
                        "weight": max(float(row["weight"]), 0.3),  # floor low weights
                        "polarity": str(row.get("polarity", "positive")).strip().lower(),
                        "original": str(row["phrase_pattern"]).strip(),
                    }
                    csv_added += 1

            logger.info(
                "SoftSkillEngine: %d built-in + %d CSV = %d total indicators",
                len(self._indicators) - csv_added, csv_added, len(self._indicators),
            )
        except Exception:
            logger.info("SoftSkillEngine: using %d built-in indicators", len(self._indicators))

    def _load_builtin_defaults(self) -> None:
        """Comprehensive built-in indicators for real-world resume language."""
        defaults = {
            # Leadership
            "led a team": {"type": "Leadership", "weight": 1.0, "polarity": "positive", "original": "Led a team"},
            "managed a team": {"type": "Leadership", "weight": 1.0, "polarity": "positive", "original": "Managed a team"},
            "mentored": {"type": "Leadership", "weight": 0.8, "polarity": "positive", "original": "Mentored"},
            "supervised": {"type": "Leadership", "weight": 0.9, "polarity": "positive", "original": "Supervised"},
            "spearheaded": {"type": "Leadership", "weight": 1.0, "polarity": "positive", "original": "Spearheaded"},
            "directed": {"type": "Leadership", "weight": 0.9, "polarity": "positive", "original": "Directed"},
            "guided": {"type": "Leadership", "weight": 0.7, "polarity": "positive", "original": "Guided"},
            "coached": {"type": "Leadership", "weight": 0.8, "polarity": "positive", "original": "Coached"},
            "oversaw": {"type": "Leadership", "weight": 0.9, "polarity": "positive", "original": "Oversaw"},
            # Teamwork
            "collaborated": {"type": "Teamwork", "weight": 0.8, "polarity": "positive", "original": "Collaborated"},
            "cross-functional": {"type": "Teamwork", "weight": 0.9, "polarity": "positive", "original": "Cross-functional"},
            "cross functional": {"type": "Teamwork", "weight": 0.9, "polarity": "positive", "original": "Cross functional"},
            "team player": {"type": "Teamwork", "weight": 0.7, "polarity": "positive", "original": "Team player"},
            "worked closely with": {"type": "Teamwork", "weight": 0.7, "polarity": "positive", "original": "Worked closely with"},
            "partnered with": {"type": "Teamwork", "weight": 0.8, "polarity": "positive", "original": "Partnered with"},
            "coordinated with": {"type": "Teamwork", "weight": 0.8, "polarity": "positive", "original": "Coordinated with"},
            "collaborated with": {"type": "Teamwork", "weight": 0.8, "polarity": "positive", "original": "Collaborated with"},
            # Communication
            "communicated": {"type": "Communication", "weight": 0.8, "polarity": "positive", "original": "Communicated"},
            "presented": {"type": "Communication", "weight": 0.9, "polarity": "positive", "original": "Presented"},
            "stakeholder": {"type": "Communication", "weight": 0.7, "polarity": "positive", "original": "Stakeholder"},
            "documentation": {"type": "Communication", "weight": 0.6, "polarity": "positive", "original": "Documentation"},
            "articulated": {"type": "Communication", "weight": 0.8, "polarity": "positive", "original": "Articulated"},
            "reported to": {"type": "Communication", "weight": 0.6, "polarity": "positive", "original": "Reported to"},
            "facilitated": {"type": "Communication", "weight": 0.8, "polarity": "positive", "original": "Facilitated"},
            # Adaptability
            "adapted": {"type": "Adaptability", "weight": 0.8, "polarity": "positive", "original": "Adapted"},
            "fast-paced": {"type": "Adaptability", "weight": 0.7, "polarity": "positive", "original": "Fast-paced"},
            "fast paced": {"type": "Adaptability", "weight": 0.7, "polarity": "positive", "original": "Fast paced"},
            "agile environment": {"type": "Adaptability", "weight": 0.7, "polarity": "positive", "original": "Agile environment"},
            "dynamic environment": {"type": "Adaptability", "weight": 0.7, "polarity": "positive", "original": "Dynamic environment"},
            "quickly learned": {"type": "Adaptability", "weight": 0.8, "polarity": "positive", "original": "Quickly learned"},
            "flexible": {"type": "Adaptability", "weight": 0.6, "polarity": "positive", "original": "Flexible"},
            # Problem Solving
            "problem solving": {"type": "Problem Solving", "weight": 0.9, "polarity": "positive", "original": "Problem solving"},
            "resolved": {"type": "Problem Solving", "weight": 0.8, "polarity": "positive", "original": "Resolved"},
            "troubleshot": {"type": "Problem Solving", "weight": 0.9, "polarity": "positive", "original": "Troubleshot"},
            "debugged": {"type": "Problem Solving", "weight": 0.8, "polarity": "positive", "original": "Debugged"},
            "diagnosed": {"type": "Problem Solving", "weight": 0.8, "polarity": "positive", "original": "Diagnosed"},
            "identified and fixed": {"type": "Problem Solving", "weight": 0.9, "polarity": "positive", "original": "Identified and fixed"},
            "root cause": {"type": "Problem Solving", "weight": 0.8, "polarity": "positive", "original": "Root cause"},
            # Ownership / Initiative
            "initiative": {"type": "Ownership", "weight": 0.9, "polarity": "positive", "original": "Initiative"},
            "ownership": {"type": "Ownership", "weight": 1.0, "polarity": "positive", "original": "Ownership"},
            "drove": {"type": "Ownership", "weight": 0.8, "polarity": "positive", "original": "Drove"},
            "delivered": {"type": "Ownership", "weight": 0.7, "polarity": "positive", "original": "Delivered"},
            "championed": {"type": "Ownership", "weight": 0.9, "polarity": "positive", "original": "Championed"},
            "launched": {"type": "Ownership", "weight": 0.8, "polarity": "positive", "original": "Launched"},
            "established": {"type": "Ownership", "weight": 0.8, "polarity": "positive", "original": "Established"},
            "pioneered": {"type": "Ownership", "weight": 0.9, "polarity": "positive", "original": "Pioneered"},
            "built from scratch": {"type": "Ownership", "weight": 1.0, "polarity": "positive", "original": "Built from scratch"},
            # Time Management
            "deadline": {"type": "Time Management", "weight": 0.7, "polarity": "positive", "original": "Deadline"},
            "on time": {"type": "Time Management", "weight": 0.7, "polarity": "positive", "original": "On time"},
            "ahead of schedule": {"type": "Time Management", "weight": 0.9, "polarity": "positive", "original": "Ahead of schedule"},
            "prioritized": {"type": "Time Management", "weight": 0.8, "polarity": "positive", "original": "Prioritized"},
            "multitasked": {"type": "Time Management", "weight": 0.7, "polarity": "positive", "original": "Multitasked"},
        }
        self._indicators = defaults

    def analyze(self, text: str) -> dict:
        """
        Scan resume text for soft-skill indicator phrases.

        Returns
        -------
        dict
            composite_score (0-100), categories, detected, matches, match_count
        """
        try:
            text_lower = text.lower()
            raw_score: float = 0.0
            categories: set[str] = set()
            detected: set[str] = set()
            matches: list[dict] = []

            for phrase, info in self._indicators.items():
                if phrase in text_lower:
                    weight = info["weight"]
                    skill_type = info["type"]
                    polarity = info["polarity"]

                    effective = weight if polarity == "positive" else -weight
                    raw_score += effective
                    categories.add(skill_type)
                    detected.add(skill_type)
                    matches.append({
                        "phrase": info["original"],
                        "type": skill_type,
                        "weight": round(weight, 2),
                        "polarity": polarity,
                    })

            # Normalize to 0-100 scale
            # A strong resume might hit ~12 indicators → 100%
            match_count = len(matches)
            composite_score = min(
                (match_count / _STRONG_RESUME_THRESHOLD) * 100,
                100.0,
            )
            # Adjust by average weight quality
            if matches:
                avg_weight = sum(m["weight"] for m in matches) / len(matches)
                composite_score *= min(avg_weight / 0.8, 1.2)  # boost/penalize by quality
            composite_score = max(0, min(100, composite_score))

            return {
                "composite_score": round(composite_score, 2),
                "categories": sorted(categories),
                "detected": sorted(detected),
                "matches": matches,
                "match_count": match_count,
            }
        except Exception as exc:
            logger.exception("Soft skill analysis failed: %s", exc)
            return {
                "composite_score": 0,
                "categories": [],
                "detected": [],
                "matches": [],
                "match_count": 0,
            }

"""
TalentIQ — Engine 12: Career Path Recommendation Engine
Suggests career progression paths based on the candidate's matched role.

Rebuilt to generate paths directly from roles_database.json using
category/level/domain relationships, instead of the legacy CSV which
had incompatible numeric IDs.

Output contract:
    current_role: str
    paths: list[dict]  — each has from_role, to_role, transition_type,
                          difficulty, skills_needed, salary_growth, similarity
    count: int
"""

from __future__ import annotations

import logging

from app.core import vector_store

logger = logging.getLogger(__name__)

# Level hierarchy for career progression
LEVEL_ORDER = [
    "Junior", "Mid", "Senior", "Lead", "Staff",
    "Principal", "Architect", "Manager", "Director", "VP",
]
_LEVEL_RANK = {level: i for i, level in enumerate(LEVEL_ORDER)}


class CareerPathEngine:
    """Recommend career progression from a given role using the roles database."""

    def suggest(self, current_role_id: str, top_k: int = 5) -> dict:
        """
        Return career progression paths for a role.

        Parameters
        ----------
        current_role_id : str
            The role_id (snake_case key) from the roles database.
        top_k : int
            Max number of path suggestions.

        Returns
        -------
        dict
            current_role, paths, count
        """
        try:
            roles_db = vector_store.get_roles_db()
            if not roles_db:
                return {"current_role": current_role_id, "paths": [], "count": 0}

            # Find the current role info
            current_info = roles_db.get(current_role_id)
            if not current_info:
                # Try matching by role_name
                for key, info in roles_db.items():
                    if info["role_name"].lower() == current_role_id.lower():
                        current_info = info
                        current_role_id = key
                        break

            if not current_info:
                return {"current_role": current_role_id, "paths": [], "count": 0}

            current_name = current_info["role_name"]
            current_category = current_info.get("category", "")
            current_level = current_info.get("level", "Mid")
            current_domain = current_info.get("domain", "")
            current_skills = set(
                s.lower()
                for s in current_info.get("required_skills", [])
                + current_info.get("preferred_skills", [])
            )
            current_rank = _LEVEL_RANK.get(current_level, 1)

            candidates: list[dict] = []

            for key, info in roles_db.items():
                if key == current_role_id:
                    continue

                target_name = info["role_name"]
                target_category = info.get("category", "")
                target_level = info.get("level", "Mid")
                target_domain = info.get("domain", "")
                target_skills = set(
                    s.lower()
                    for s in info.get("required_skills", [])
                    + info.get("preferred_skills", [])
                )
                target_rank = _LEVEL_RANK.get(target_level, 1)

                # ── Scoring logic ────────────────────────────────
                score = 0.0
                transition_type = ""

                # Same category, higher level → strong promotion path
                if target_category == current_category and target_rank > current_rank:
                    level_gap = target_rank - current_rank
                    if level_gap == 1:
                        score += 50
                        transition_type = "Promotion"
                    elif level_gap == 2:
                        score += 35
                        transition_type = "Advancement"
                    elif level_gap <= 3:
                        score += 20
                        transition_type = "Long-term Goal"

                # Same domain, different category → lateral move
                elif target_domain == current_domain and target_rank >= current_rank:
                    score += 30
                    transition_type = "Lateral Move"

                # Management track from senior technical
                elif (
                    target_category == "Management & Leadership"
                    and current_rank >= _LEVEL_RANK.get("Senior", 2)
                ):
                    score += 25
                    transition_type = "Management Track"

                # Related category at same or higher level
                elif target_rank >= current_rank and target_rank <= current_rank + 2:
                    score += 15
                    transition_type = "Career Pivot"

                if score <= 0:
                    continue

                # Skill similarity bonus
                if current_skills and target_skills:
                    overlap = current_skills & target_skills
                    similarity = len(overlap) / max(len(target_skills), 1)
                    score += similarity * 30
                else:
                    similarity = 0.0

                # Skills the candidate needs to develop
                new_skills = sorted(target_skills - current_skills)

                # Difficulty: higher for bigger level gaps and less skill overlap
                level_gap = max(target_rank - current_rank, 0)
                difficulty = min(
                    (level_gap * 0.2) + ((1 - similarity) * 0.5) + 0.1,
                    1.0,
                )

                # Estimated salary growth (rough heuristic)
                salary_growth = max(level_gap * 12, 5) + int(similarity * 10)

                candidates.append({
                    "from_role": current_name,
                    "to_role": target_name,
                    "transition_type": transition_type,
                    "difficulty": round(difficulty, 2),
                    "skills_needed": new_skills[:10],
                    "skill_overlap": round(similarity * 100, 1),
                    "salary_growth_percent": min(salary_growth, 60),
                    "score": round(score, 2),
                })

            # Sort by score descending
            candidates.sort(key=lambda x: x["score"], reverse=True)
            paths = candidates[:top_k]

            # Remove internal scoring field
            for p in paths:
                p.pop("score", None)

            return {
                "current_role": current_name,
                "paths": paths,
                "count": len(paths),
            }

        except Exception as exc:
            logger.exception("Career path suggestion failed: %s", exc)
            return {
                "current_role": str(current_role_id),
                "paths": [],
                "count": 0,
            }

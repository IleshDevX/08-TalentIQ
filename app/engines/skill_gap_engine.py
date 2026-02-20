"""
TalentIQ — Engine #9: Skill Gap Analysis Engine (Enhanced v2.0)
Identifies missing mandatory skills for a target role and quantifies
the candidate's coverage using fuzzy matching.

Enhanced features:
  - Exact matching: full credit
  - Partial/substring matching: 70% credit
  - Coverage calculation includes fuzzy matches

Powers downstream engines:
    - Certification suggestion
    - Career growth recommendations
    - Resume improvement hints
"""

from __future__ import annotations


class SkillGapEngine:
    """Compare candidate skills against role requirements with fuzzy matching."""

    def identify(
        self,
        candidate_skills: list[str],
        role_required_skills: list[str],
    ) -> dict:
        """
        Compute skill overlap and gaps with enhanced fuzzy matching.

        Parameters
        ----------
        candidate_skills : list[str]
            Normalized skills extracted from the resume.
        role_required_skills : list[str]
            Skills expected for the target role.

        Returns
        -------
        dict
            missing_skills, matched_skills, coverage_percent, extra_skills,
            partial_matches (new)
        """
        cand_set = {s.lower().strip() for s in candidate_skills}
        role_set = {s.lower().strip() for s in role_required_skills}

        exact_matched = sorted(cand_set & role_set)
        exact_missing = sorted(role_set - cand_set)
        extra = sorted(cand_set - role_set)

        # ── Enhanced: Find partial/fuzzy matches ─────────────────────
        partial_matches = []
        fuzzy_credits = 0.0
        still_missing = []

        for role_skill in exact_missing:
            found_partial = False
            for cand_skill in cand_set:
                # Substring match (either direction)
                if role_skill in cand_skill or cand_skill in role_skill:
                    partial_matches.append({
                        "required": role_skill,
                        "candidate_has": cand_skill,
                        "match_type": "partial",
                    })
                    fuzzy_credits += 0.7  # 70% credit for partial match
                    found_partial = True
                    break

            if not found_partial:
                still_missing.append(role_skill)

        # ── Coverage calculation ─────────────────────────────────────
        # Total credits = exact matches + fuzzy matches
        total_credits = len(exact_matched) + fuzzy_credits
        coverage = (total_credits / len(role_set) * 100) if role_set else 0.0

        return {
            "matched_skills": exact_matched,
            "missing_skills": still_missing,
            "partial_matches": partial_matches,
            "extra_skills": extra,
            "coverage_percent": round(coverage, 2),
            "matched_count": len(exact_matched),
            "partial_count": len(partial_matches),
            "missing_count": len(still_missing),
            "required_total": len(role_set),
        }

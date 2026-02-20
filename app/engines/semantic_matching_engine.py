"""
TalentIQ — Engine #7: Semantic Matching Engine (HYBRID v2.0)
Orchestrates intelligent resume → role-matching with multi-factor scoring:
    1. Semantic similarity (embedding-based)         — 40%
    2. Skill overlap (exact matches)                 — 35%
    3. Experience alignment (years match)            — 15%
    4. Keyword/domain relevance                      — 10%

This hybrid approach significantly improves match accuracy vs pure embeddings.
"""

from __future__ import annotations

import logging
import numpy as np

from app.core import vector_store
from app.engines.resume_embedding_engine import ResumeEmbeddingEngine

logger = logging.getLogger(__name__)


class SemanticMatchingEngine:
    """Hybrid role-matching engine with semantic + structural scoring."""

    # Scoring weights
    W_SEMANTIC = 0.40      # Base embedding similarity
    W_SKILLS = 0.35        # Skill overlap boost
    W_EXPERIENCE = 0.15    # Experience alignment boost
    W_KEYWORDS = 0.10      # Keyword/domain match boost

    def __init__(self) -> None:
        self._embedder = ResumeEmbeddingEngine()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(
        self,
        resume_text: str,
        candidate_skills: list[str] | None = None,
        candidate_experience: int | float = 0,
        candidate_keywords: list[str] | None = None,
        top_k: int = 5,
    ) -> dict:
        """
        Hybrid semantic + structural role matching.

        Parameters
        ----------
        resume_text : str
            Full resume text for embedding generation.
        candidate_skills : list[str], optional
            Extracted/normalized skills from resume.
        candidate_experience : int|float, optional
            Years of experience detected (default 0).
        candidate_keywords : list[str], optional
            Domain keywords extracted from resume.
        top_k : int
            Number of top matches to return (default 5).

        Returns
        -------
        dict
            {
                "top_roles": [{rank, role_name, score, breakdown}, ...],
                "embedding_dim": 384,
                "roles_searched": <total>,
                "matching_method": "hybrid",
            }
        """
        if not resume_text or not resume_text.strip():
            return {
                "top_roles": [],
                "embedding_dim": 0,
                "roles_searched": 0,
                "error": "Empty resume text provided.",
                "matching_method": "none",
            }

        # 1. Generate resume embedding
        embedding: np.ndarray = self._embedder.generate(resume_text)

        # 2. Get base semantic matches (top_k * 2 for re-ranking)
        search_k = min(top_k * 3, 20)  # Get more candidates for re-ranking
        base_matches = vector_store.search(embedding, top_k=search_k)

        # 3. Hybrid re-ranking with skill/experience/keyword boosts
        enhanced_matches = self._hybrid_rerank(
            base_matches=base_matches,
            candidate_skills=candidate_skills or [],
            candidate_experience=candidate_experience,
            candidate_keywords=candidate_keywords or [],
        )

        # 4. Return top_k after re-ranking
        final_matches = enhanced_matches[:top_k]

        return {
            "top_roles": final_matches,
            "embedding_dim": int(embedding.shape[0]),
            "roles_searched": len(vector_store.get_roles()),
            "matching_method": "hybrid",
        }

    # ------------------------------------------------------------------
    # Hybrid Scoring Logic
    # ------------------------------------------------------------------

    def _hybrid_rerank(
        self,
        base_matches: list[dict],
        candidate_skills: list[str],
        candidate_experience: int | float,
        candidate_keywords: list[str],
    ) -> list[dict]:
        """
        Re-rank initial semantic matches using skill/experience/keyword boosts.

        Scoring formula (0-1 scale):
          final_score = 0.40*semantic + 0.35*skills + 0.15*experience + 0.10*keywords

        Returns re-ranked list with updated scores and breakdown.
        """
        cand_skills_set = {s.lower().strip() for s in candidate_skills}
        cand_keywords_set = {k.lower().strip() for k in candidate_keywords}

        enhanced = []
        for match in base_matches:
            role_name = match["role_name"]
            semantic_score = match["score"]  # Already 0-1 from cosine similarity

            # ── Component 2: Skill Overlap ──
            role_skills = vector_store.get_role_skills(role_name)
            role_skills_set = {s.lower().strip() for s in role_skills}

            if role_skills_set:
                skill_overlap = len(cand_skills_set & role_skills_set) / len(role_skills_set)
            else:
                skill_overlap = 0.0

            # ── Component 3: Experience Alignment ──
            role_obj = next(
                (r for r in vector_store.get_roles() if r.role_name == role_name),
                None,
            )
            if role_obj:
                role_min = float(role_obj.years_experience_min) if role_obj.years_experience_min else 0
                role_max = float(role_obj.years_experience_max) if role_obj.years_experience_max else role_min * 2
            else:
                role_min = role_max = 0

            exp_score = self._compute_exp_alignment(candidate_experience, role_min, role_max)

            # ── Component 4: Keyword/Domain Match ──
            role_keywords = vector_store.get_role_keywords(role_name)
            role_keywords_set = {k.lower().strip() for k in role_keywords}

            if role_keywords_set:
                keyword_overlap = len(cand_keywords_set & role_keywords_set) / len(role_keywords_set)
            else:
                keyword_overlap = 0.0

            # ── Final Hybrid Score ──
            final_score = (
                self.W_SEMANTIC * semantic_score
                + self.W_SKILLS * skill_overlap
                + self.W_EXPERIENCE * exp_score
                + self.W_KEYWORDS * keyword_overlap
            )

            enhanced.append({
                **match,
                "score": round(final_score, 4),
                "breakdown": {
                    "semantic": round(semantic_score, 4),
                    "skills": round(skill_overlap, 4),
                    "experience": round(exp_score, 4),
                    "keywords": round(keyword_overlap, 4),
                },
            })

        # Sort by final hybrid score descending
        enhanced.sort(key=lambda x: x["score"], reverse=True)

        # Re-assign ranks
        for rank, match in enumerate(enhanced, start=1):
            match["rank"] = rank

        return enhanced

    @staticmethod
    def _compute_exp_alignment(
        candidate_exp: float,
        role_min: float,
        role_max: float,
    ) -> float:
        """
        Calculate experience alignment score (0-1).

        Logic:
          - Below min: scaled 0 → 0.7
          - Within range: 0.7 → 1.0
          - Above max: 1.0 (over-qualification is fine for matching)
        """
        if role_min <= 0:
            return 1.0  # No requirement — perfect match

        if candidate_exp < role_min:
            # Under-qualified: scale from 0 to 0.7
            return (candidate_exp / role_min) * 0.7

        if candidate_exp <= role_max:
            # Perfect fit: scale from 0.7 to 1.0
            if role_max == role_min:
                return 1.0
            progress = (candidate_exp - role_min) / (role_max - role_min)
            return 0.7 + progress * 0.3

        # Over-qualified: still 1.0 (for matching purposes)
        return 1.0

"""
TalentIQ — Engine 17: JD Comparison Engine
Side-by-side resume vs job description comparison.

Produces:
    - matched/missing keywords
    - section_scores (flat dict for immediate UI consumption)
    - overall_match_percent
"""

from __future__ import annotations

import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)


class JDComparisonEngine:
    """Compare resume text with a job description."""

    STOP_WORDS: set[str] = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "shall", "can", "need", "must",
        "it", "its", "this", "that", "these", "those", "i", "we", "you",
        "he", "she", "they", "me", "us", "him", "her", "them", "my", "our",
        "your", "his", "their", "mine", "ours", "yours", "theirs",
        "what", "which", "who", "whom", "where", "when", "why", "how",
        "not", "no", "nor", "so", "as", "if", "then", "than", "too", "very",
        "also", "just", "about", "above", "after", "again", "all", "am",
        "any", "because", "before", "below", "between", "both", "each",
        "few", "further", "here", "into", "more", "most", "other", "out",
        "own", "same", "some", "such", "through", "under", "until", "up",
        "while", "during", "over", "only", "once", "etc", "eg", "ie",
        "including", "using", "based", "within", "across", "along",
        "work", "working", "ability", "strong", "experience", "required",
        "preferred", "including", "well", "looking", "role", "team",
        "years", "year", "minimum", "plus", "least", "join", "responsible",
    }

    # -----------------------------------------------------------------

    def compare(
        self,
        resume_text: str,
        jd_text: str,
        resume_skills: list[str] | None = None,
    ) -> dict:
        """
        Enhanced resume-vs-JD comparison with fuzzy matching.

        Returns
        -------
        dict
            overall_match_percent, keyword_coverage_percent,
            matched_keywords, missing_keywords, partial_matches,
            section_scores (flat dict)
        """
        try:
            logger.info("Running enhanced JD comparison analysis")

            resume_lower = resume_text.lower()
            jd_lower = jd_text.lower()

            # Extract meaningful keywords
            jd_keywords = self._extract_keywords(jd_lower)
            resume_keywords = self._extract_keywords(resume_lower)

            # Exact matches
            exact_matched = sorted(jd_keywords & resume_keywords)
            exact_missing = sorted(jd_keywords - resume_keywords)
            extra_in_resume = sorted(resume_keywords - jd_keywords)

            # ── Enhanced: Fuzzy/partial matching ─────────────────────
            partial_matched = []
            still_missing = []
            fuzzy_credits = 0.0

            for jd_kw in exact_missing:
                found_partial = False
                for res_kw in resume_keywords:
                    # Substring match (either direction)
                    if jd_kw in res_kw or res_kw in jd_kw:
                        partial_matched.append({
                            "jd_keyword": jd_kw,
                            "resume_has": res_kw,
                        })
                        fuzzy_credits += 0.7  # 70% credit
                        found_partial = True
                        break
                
                if not found_partial:
                    still_missing.append(jd_kw)

            # Enhanced coverage calculation
            total_credits = len(exact_matched) + fuzzy_credits
            coverage = (total_credits / len(jd_keywords) * 100) if jd_keywords else 0.0

            # Section-wise analysis (with boost from actual resume_skills)
            sections = self._section_analysis(resume_lower, jd_lower, resume_skills)

            # Flat section_scores dict for immediate UI consumption
            section_scores = {
                k: v["relevance_percent"] for k, v in sections.items()
            }

            # Weighted overall match (slightly more generous)
            overall = self._compute_overall_match(coverage, sections)

            return {
                "overall_match_percent": round(overall, 2),
                "keyword_coverage_percent": round(coverage, 2),
                "matched_keywords": exact_matched,
                "missing_keywords": still_missing,
                "partial_matches": partial_matched,
                "extra_in_resume": extra_in_resume,
                "matched_count": len(exact_matched),
                "partial_count": len(partial_matched),
                "missing_count": len(still_missing),
                "jd_keyword_count": len(jd_keywords),
                "section_scores": section_scores,
                "sections": sections,
            }
        except Exception as exc:
            logger.exception("JD comparison failed: %s", exc)
            return {
                "overall_match_percent": 0,
                "keyword_coverage_percent": 0,
                "matched_keywords": [],
                "missing_keywords": [],
                "extra_in_resume": [],
                "matched_count": 0,
                "missing_count": 0,
                "jd_keyword_count": 0,
                "section_scores": {},
                "sections": {},
            }

    # -----------------------------------------------------------------

    def _extract_keywords(self, text: str) -> set[str]:
        """
        Extract meaningful keywords with enhanced matching.
        Now extracts more aggressive patterns and includes hyphenated terms.
        """
        keywords: set[str] = set()
        
        # Multi-word phrases (2-4 words) with more flexible patterns
        # Handles: "machine learning", "data structures", "rest api", "ci/cd"
        bigrams = re.findall(r"\b([a-z][a-z+#./\-]+(?:\s+[a-z][a-z+#./\-]+){1,3})\b", text)
        for bg in bigrams:
            tokens = bg.split()
            # More lenient: allow if ANY token is not a stop word
            if any(t not in self.STOP_WORDS for t in tokens):
                keywords.add(bg.strip())
        
        # Single meaningful words (more generous length)
        words = re.findall(r"\b[a-z][a-z+#./\-]{1,}\b", text)
        for w in words:
            if w not in self.STOP_WORDS and len(w) > 2:
                keywords.add(w)
        
        return keywords

    def _section_analysis(
        self,
        resume_lower: str,
        jd_lower: str,
        resume_skills: list[str] | None = None,
    ) -> dict:
        sections: dict = {}

        # Skills
        skill_patterns = [
            r"python", r"java\b", r"javascript", r"typescript", r"react",
            r"node\.?js", r"docker", r"kubernetes", r"aws", r"sql",
            r"linux", r"git", r"agile", r"scrum", r"rest\s*api",
            r"machine\s*learning", r"deep\s*learning", r"tensorflow",
            r"pytorch", r"html", r"css", r"angular", r"vue",
            r"mongodb", r"postgresql", r"redis", r"kafka",
            r"terraform", r"ci/?cd", r"microservices",
        ]
        jd_skill_count = sum(1 for p in skill_patterns if re.search(p, jd_lower))
        resume_skill_count = sum(1 for p in skill_patterns if re.search(p, resume_lower))
        skill_match = (
            min(resume_skill_count / jd_skill_count * 100, 100)
            if jd_skill_count > 0
            else (100.0 if resume_skill_count > 0 else 50.0)
        )
        sections["skills"] = {"relevance_percent": round(skill_match, 1)}

        # Experience
        exp_jd = self._extract_years(jd_lower)
        exp_resume = self._extract_years(resume_lower)
        if exp_jd > 0:
            exp_match = min(exp_resume / exp_jd * 100, 100) if exp_resume > 0 else 30.0
        else:
            exp_match = 80.0
        sections["experience"] = {
            "relevance_percent": round(exp_match, 1),
            "jd_years": exp_jd,
            "resume_years": exp_resume,
        }

        # Education
        edu_keywords = [
            "bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "m.e",
            "b.s", "m.s", "mba", "bca", "mca", "diploma", "degree",
        ]
        jd_edu = sum(1 for k in edu_keywords if k in jd_lower)
        resume_edu = sum(1 for k in edu_keywords if k in resume_lower)
        edu_match = min(resume_edu / jd_edu * 100, 100) if jd_edu > 0 else 80.0
        sections["education"] = {"relevance_percent": round(edu_match, 1)}

        # Tools
        tool_keywords = [
            "git", "jira", "docker", "jenkins", "terraform", "ansible",
            "webpack", "figma", "postman", "swagger", "confluence",
            "slack", "vscode", "vim", "linux",
        ]
        jd_tools = sum(1 for k in tool_keywords if k in jd_lower)
        resume_tools = sum(1 for k in tool_keywords if k in resume_lower)
        tool_match = min(resume_tools / jd_tools * 100, 100) if jd_tools > 0 else 80.0
        sections["tools"] = {"relevance_percent": round(tool_match, 1)}

        return sections

    @staticmethod
    def _extract_years(text: str) -> int:
        matches = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", text)
        years = [int(y) for y in matches if y.isdigit()]
        return max(years) if years else 0

    @staticmethod
    def _compute_overall_match(keyword_coverage: float, sections: dict) -> float:
        """
        Compute overall JD match with stricter weighting.
        
        Emphasizes keyword coverage more heavily to prevent false positives
        (e.g., Data Scientist matching 51% for Civil Engineer due to generic keywords).
        """
        section_avg = 0.0
        if sections:
            vals = [s["relevance_percent"] for s in sections.values()]
            section_avg = sum(vals) / len(vals)
        
        # Stricter weighting: 75% keywords, 25% sections
        # This ensures domain mismatch shows low scores
        return keyword_coverage * 0.75 + section_avg * 0.25

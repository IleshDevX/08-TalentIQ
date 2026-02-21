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

        # Skills - Use actual extracted skills instead of hardcoded patterns
        if resume_skills:
            # Convert resume skills to lowercase for matching
            resume_skills_lower = [s.lower().strip() for s in resume_skills]
            
            # Extract skill-like terms from JD (technical keywords)
            skill_patterns = [
                r"\b(python|java|javascript|typescript|c\+\+|c#|ruby|php|go|rust|swift|kotlin)\b",
                r"\b(react|angular|vue|node\.?js|express|django|flask|spring|laravel)\b",
                r"\b(docker|kubernetes|aws|azure|gcp|terraform|ansible|jenkins)\b",
                r"\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|cassandra)\b",
                r"\b(git|jira|confluence|slack|agile|scrum|ci/?cd|devops)\b",
                r"\b(machine\s*learning|deep\s*learning|nlp|computer\s*vision|ai)\b",
                r"\b(tensorflow|pytorch|scikit-learn|pandas|numpy|spark)\b",
                r"\b(html|css|sass|less|bootstrap|tailwind)\b",
                r"\b(rest\s*api|graphql|microservices|websockets|grpc)\b",
            ]
            
            jd_required_skills = set()
            for pattern in skill_patterns:
                matches = re.finditer(pattern, jd_lower)
                for match in matches:
                    jd_required_skills.add(match.group().strip())
            
            if jd_required_skills:
                # Count how many JD skills are covered by resume
                matched_skills = 0
                for jd_skill in jd_required_skills:
                    # Check if JD skill is in resume skills or resume text
                    if any(jd_skill in rs for rs in resume_skills_lower) or jd_skill in resume_lower:
                        matched_skills += 1
                
                skill_match = (matched_skills / len(jd_required_skills)) * 100
            else:
                # If JD has no clear technical skills, check general coverage
                skill_match = 70.0 if len(resume_skills) > 5 else 50.0
        else:
            # Fallback to basic keyword matching if no skills extracted
            skill_match = 50.0
        
        sections["skills"] = {"relevance_percent": round(skill_match, 1)}

        # Experience - More nuanced scoring
        exp_jd = self._extract_years(jd_lower)
        exp_resume = self._extract_years(resume_lower)
        
        if exp_jd > 0 and exp_resume > 0:
            # Calculate percentage, cap at 100%
            ratio = exp_resume / exp_jd
            if ratio >= 1.0:
                exp_match = 100.0
            elif ratio >= 0.8:
                exp_match = 90.0
            elif ratio >= 0.6:
                exp_match = 75.0
            elif ratio >= 0.4:
                exp_match = 50.0
            else:
                exp_match = 30.0
        elif exp_jd == 0 and exp_resume > 0:
            # JD doesn't specify experience, but resume has it
            exp_match = 85.0
        elif exp_jd > 0 and exp_resume == 0:
            # JD requires experience, resume has none
            exp_match = 20.0
        else:
            # Both have no specific years mentioned
            exp_match = 60.0
        
        sections["experience"] = {
            "relevance_percent": round(exp_match, 1),
            "jd_years": exp_jd,
            "resume_years": exp_resume,
        }

        # Education - More accurate matching
        edu_keywords = [
            "bachelor", "master", "phd", "doctorate", "b.tech", "m.tech", 
            "b.e", "m.e", "b.s", "m.s", "mba", "bca", "mca", 
            "diploma", "degree", "certification"
        ]
        
        jd_edu_found = [k for k in edu_keywords if k in jd_lower]
        resume_edu_found = [k for k in edu_keywords if k in resume_lower]
        
        if jd_edu_found:
            # Check how many JD education requirements are met
            matched_edu = sum(1 for jd_e in jd_edu_found if jd_e in resume_lower)
            edu_match = (matched_edu / len(jd_edu_found)) * 100
        else:
            # JD doesn't specify education
            edu_match = 75.0 if resume_edu_found else 60.0
        
        sections["education"] = {"relevance_percent": round(edu_match, 1)}

        # Tools - Check JD requirements vs resume tools
        tool_keywords = [
            "git", "github", "gitlab", "bitbucket",
            "jira", "confluence", "asana", "trello",
            "docker", "kubernetes", "jenkins", "circleci", "travis",
            "terraform", "ansible", "puppet", "chef",
            "webpack", "babel", "vite", "rollup",
            "figma", "sketch", "adobe xd",
            "postman", "swagger", "insomnia",
            "vscode", "intellij", "pycharm", "vim", "emacs",
            "linux", "unix", "bash", "powershell"
        ]
        
        jd_tools_found = [t for t in tool_keywords if t in jd_lower]
        resume_tools_found = [t for t in tool_keywords if t in resume_lower]
        
        if jd_tools_found:
            # Check how many JD tools are in resume
            matched_tools = sum(1 for jd_t in jd_tools_found if jd_t in resume_lower)
            tool_match = (matched_tools / len(jd_tools_found)) * 100
        else:
            # JD doesn't specify tools
            tool_match = 70.0 if resume_tools_found else 65.0
        
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

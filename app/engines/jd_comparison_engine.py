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
        """
        Analyze section-by-section match between resume and JD.
        Uses keyword extraction from both documents for accurate comparison.
        """
        sections: dict = {}

        # ═══════════════════════════════════════════════════════════════
        # SKILLS SECTION - Compare technical skills mentioned
        # ═══════════════════════════════════════════════════════════════
        
        # Extract ALL skill-like terms from JD
        jd_skill_keywords = self._extract_keywords(jd_lower)
        resume_skill_keywords = self._extract_keywords(resume_lower)
        
        # Also add explicit resume_skills if provided
        if resume_skills:
            for skill in resume_skills:
                resume_skill_keywords.add(skill.lower().strip())
        
        # Filter to skill-relevant terms (remove general words)
        skill_indicators = {
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php",
            "go", "golang", "rust", "swift", "kotlin", "scala", "perl", "r",
            "react", "angular", "vue", "nodejs", "node.js", "express", "django", "flask",
            "spring", "laravel", "rails", "nextjs", "next.js", "fastapi", "graphql",
            "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "terraform", "ansible",
            "jenkins", "circleci", "github actions", "gitlab ci", "ci/cd", "devops",
            "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch",
            "cassandra", "dynamodb", "firebase", "supabase", "oracle", "sqlite",
            "machine learning", "deep learning", "nlp", "computer vision", "ai", "ml",
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "spark",
            "html", "css", "sass", "less", "bootstrap", "tailwind", "webpack",
            "rest", "api", "microservices", "grpc", "websocket", "http", "json",
            "linux", "unix", "bash", "shell", "powershell", "git", "agile", "scrum",
            "testing", "jest", "pytest", "junit", "selenium", "cypress", "automation",
            "data science", "data analysis", "data engineering", "etl", "tableau", "power bi",
            "figma", "sketch", "adobe", "photoshop", "illustrator", "ui", "ux",
        }
        
        # Find skill terms in JD
        jd_skills = set()
        for kw in jd_skill_keywords:
            if any(ind in kw for ind in skill_indicators) or kw in skill_indicators:
                jd_skills.add(kw)
        
        # If no clear skills found, use general keyword match
        if not jd_skills:
            jd_skills = jd_skill_keywords
        
        # Count matches
        if jd_skills:
            matched_skills = 0
            for jd_skill in jd_skills:
                # Check for exact or partial match in resume
                if jd_skill in resume_skill_keywords:
                    matched_skills += 1
                elif any(jd_skill in rs or rs in jd_skill for rs in resume_skill_keywords):
                    matched_skills += 0.7  # Partial credit
            
            skill_match = (matched_skills / len(jd_skills)) * 100
        else:
            skill_match = 60.0  # Neutral if JD has no clear skills
        
        sections["skills"] = {"relevance_percent": round(min(100, skill_match), 1)}

        # ═══════════════════════════════════════════════════════════════
        # EXPERIENCE SECTION - Compare experience requirements
        # ═══════════════════════════════════════════════════════════════
        
        # Extract years from both
        exp_jd = self._extract_years(jd_lower)
        exp_resume = self._extract_years(resume_lower)
        
        # Also check for experience-related keywords
        exp_keywords = [
            "experience", "experienced", "worked", "developed", "managed",
            "led", "built", "created", "implemented", "designed", "architected",
            "senior", "junior", "lead", "principal", "staff", "intern",
            "project", "projects", "team", "teams", "company", "organization",
        ]
        
        jd_exp_mentions = sum(1 for k in exp_keywords if k in jd_lower)
        resume_exp_mentions = sum(1 for k in exp_keywords if k in resume_lower)
        
        # Calculate experience match
        if exp_jd > 0:
            if exp_resume >= exp_jd:
                exp_match = 100.0
            elif exp_resume > 0:
                ratio = exp_resume / exp_jd
                exp_match = max(20, ratio * 100)
            else:
                # No years in resume but check for experience keywords
                exp_match = min(50, resume_exp_mentions * 5) if resume_exp_mentions > 0 else 15.0
        else:
            # JD doesn't specify years
            if resume_exp_mentions > 0:
                exp_match = min(85, 50 + resume_exp_mentions * 5)
            else:
                exp_match = 50.0
        
        sections["experience"] = {
            "relevance_percent": round(min(100, exp_match), 1),
            "jd_years": exp_jd,
            "resume_years": exp_resume,
        }

        # ═══════════════════════════════════════════════════════════════
        # EDUCATION SECTION - Compare education requirements
        # ═══════════════════════════════════════════════════════════════
        
        edu_levels = {
            "phd": 5, "doctorate": 5, "ph.d": 5,
            "master": 4, "m.s": 4, "m.tech": 4, "m.e": 4, "mba": 4, "mca": 4, "ms": 4,
            "bachelor": 3, "b.s": 3, "b.tech": 3, "b.e": 3, "bca": 3, "bs": 3, "ba": 3,
            "degree": 2, "diploma": 1, "certificate": 1, "certification": 1,
        }
        
        # Find highest education level in JD
        jd_max_level = 0
        jd_edu_terms = []
        for term, level in edu_levels.items():
            if term in jd_lower:
                jd_edu_terms.append(term)
                jd_max_level = max(jd_max_level, level)
        
        # Find highest education level in resume
        resume_max_level = 0
        resume_edu_terms = []
        for term, level in edu_levels.items():
            if term in resume_lower:
                resume_edu_terms.append(term)
                resume_max_level = max(resume_max_level, level)
        
        # Also check field-specific education
        edu_fields = [
            "computer science", "engineering", "information technology", "data science",
            "mathematics", "statistics", "physics", "business", "management",
            "software", "electrical", "mechanical", "civil", "chemical",
        ]
        
        jd_fields = [f for f in edu_fields if f in jd_lower]
        resume_fields = [f for f in edu_fields if f in resume_lower]
        field_match_bonus = 10 if any(f in resume_fields for f in jd_fields) else 0
        
        # Calculate education match
        if jd_max_level > 0:
            if resume_max_level >= jd_max_level:
                edu_match = 100.0
            elif resume_max_level > 0:
                edu_match = (resume_max_level / jd_max_level) * 100
            else:
                edu_match = 20.0
        else:
            # JD doesn't specify education
            edu_match = 80.0 if resume_max_level > 0 else 60.0
        
        edu_match = min(100, edu_match + field_match_bonus)
        sections["education"] = {"relevance_percent": round(edu_match, 1)}

        # ═══════════════════════════════════════════════════════════════
        # TOOLS SECTION - Compare tools/technologies mentioned
        # ═══════════════════════════════════════════════════════════════
        
        tool_keywords = [
            "git", "github", "gitlab", "bitbucket", "svn",
            "jira", "confluence", "asana", "trello", "notion", "monday",
            "docker", "kubernetes", "jenkins", "circleci", "travis", "bamboo",
            "terraform", "ansible", "puppet", "chef", "vagrant",
            "webpack", "babel", "vite", "rollup", "parcel", "esbuild",
            "npm", "yarn", "pip", "maven", "gradle", "cargo",
            "figma", "sketch", "adobe xd", "invision", "zeplin",
            "postman", "swagger", "insomnia", "curl",
            "vscode", "visual studio", "intellij", "pycharm", "webstorm", "vim", "emacs",
            "linux", "ubuntu", "centos", "debian", "windows server",
            "nginx", "apache", "iis", "tomcat",
            "slack", "teams", "zoom", "discord",
            "aws", "s3", "ec2", "lambda", "cloudfront", "rds",
            "azure", "gcp", "heroku", "vercel", "netlify", "digitalocean",
        ]
        
        # Extract tools from JD
        jd_tools = set()
        for tool in tool_keywords:
            if tool in jd_lower:
                jd_tools.add(tool)
        
        # Extract tools from resume
        resume_tools = set()
        for tool in tool_keywords:
            if tool in resume_lower:
                resume_tools.add(tool)
        
        # Calculate match
        if jd_tools:
            matched_tools = len(jd_tools & resume_tools)
            tool_match = (matched_tools / len(jd_tools)) * 100
        else:
            # JD doesn't mention specific tools
            tool_match = 70.0 if resume_tools else 50.0
        
        sections["tools"] = {"relevance_percent": round(min(100, tool_match), 1)}

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

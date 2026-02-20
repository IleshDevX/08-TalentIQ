"""
TalentIQ — Engine 11: Enhanced Resume Improvement Engine v2.0

Intelligent resume enhancement suggestions that help candidates:
1. Align with target role requirements
2. Quantify achievements with metrics
3. Strengthen action verbs and impact statements
4. Add missing critical skills/keywords
5. Improve ATS compatibility

Output contract:
    suggestions: list[dict] — category, suggestion, priority, action_type, impact
    issue_count: int
    improvement_score: float (0-100)
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class ResumeImprovementEngine:
    """ Provide intelligent, role-specific resume improvement suggestions."""

    # ── Weak action verbs to flag ──────────────────────────────────────────
    WEAK_VERBS = {
        "worked", "did", "helped", "assisted", "involved", "tasked",
        "responsible", "handled", "managed", "used", "utilized",
    }
    
    # ── Strong action verbs by category ───────────────────────────────────
    STRONG_VERBS = {
        "leadership": ["led", "directed", "orchestrated", "spearheaded", "championed"],
        "achievement": ["achieved", "delivered", "accomplished", "exceeded", "completed"],
        "creation": ["designed", "developed", "engineered", "architected", "built"],
        "improvement": ["optimized", "enhanced", "improved", "increased", "reduced"],
        "analysis": ["analyzed", "evaluated", "assessed", "investigated", "researched"],
    }
    
    # ── Passive voice indicators ──────────────────────────────────────────
    PASSIVE_PATTERNS = [
        r"\bwas\s+\w+ed\b",  # was developed, was created
        r"\bwere\s+\w+ed\b",  # were implemented
        r"\bbeen\s+\w+ed\b",  # have been deployed
        r"\btasked\s+with\b",
        r"\bresponsible\s+for\b",
        r"\binvolved\s+in\b",
    ]

    def __init__(self) -> None:
        logger.info("ResumeImprovementEngine v2.0: Intelligent suggestion system ready")

    def analyze(
        self,
        text: str,
        candidate_skills: list[str] | None = None,
        role_required_skills: list[str] | None = None,
        role_name: str | None = None,
        skill_match_percent: float = 0,
    ) -> dict:
        """
        Generate intelligent, role-specific resume improvement suggestions.
        
        Parameters
        ----------
        text : str
            Resume text to analyze
        candidate_skills : list[str]
            Skills detected in resume
        role_required_skills : list[str]
            Skills required for target role
        role_name : str
            Target role name
        skill_match_percent : float
            Current skill match percentage
        
        Returns
        -------
        dict
            suggestions, issue_count, improvement_score
        """
        try:
            suggestions: list[dict] = []
            
            # ── Strategy 1: Skill Gap Suggestions ──────────────────────
            if role_required_skills and candidate_skills:
                missing = set(s.lower() for s in role_required_skills) - set(s.lower() for s in candidate_skills)
                if missing and len(missing) <= 5:
                    for skill in list(missing)[:3]:
                        suggestions.append({
                            "category": "skill_gap",
                            "priority": "high",
                            "action_type": "add_skill",
                            "suggestion": f"Add '{skill}' experience to align with {role_name or 'target role'}",
                            "impact": "Increases role match score by highlighting relevant experience",
                        })
            
            # ── Strategy 2: Quantification Suggestions ─────────────────
            if not self._has_sufficient_metrics(text):
                suggestions.append({
                    "category": "quantification",
                    "priority": "high",
                    "action_type": "add_metrics",
                    "suggestion": "Add quantifiable achievements (e.g., '↑30% performance', '500K+ users', '10+ projects')",
                    "impact": "Numbers make achievements concrete and memorable for recruiters",
                })
            
            # ── Strategy 3: Passive Voice Detection ───────────────────
            passive_count = self._detect_passive_voice(text)
            if passive_count > 2:
                suggestions.append({
                    "category": "writing_style",
                    "priority": "high",
                    "action_type": "fix_passive",
                    "suggestion": f"Replace {passive_count} passive phrases (e.g., 'Was responsible for' → 'Led', 'Tasked with' → 'Delivered')",
                    "impact": "Active voice shows ownership and leadership",
                })
            
            # ── Strategy 4: Weak Action Verbs ─────────────────────────
            weak_verbs = self._detect_weak_verbs(text)
            if weak_verbs:
                suggestions.append({
                    "category": "action_verbs",
                    "priority": "medium",
                    "action_type": "strengthen_verbs",
                    "suggestion": f"Replace weak verbs: {', '.join(list(weak_verbs)[:3])} with stronger alternatives",
                    "impact": "Strong action verbs demonstrate initiative and impact",
                })
            
            # ── Strategy 5: Role Alignment Suggestions ────────────────
            if skill_match_percent < 60 and role_name:
                suggestions.append({
                    "category": "role_alignment",
                    "priority": "high",
                    "action_type": "reframe_experience",
                    "suggestion": f"Reframe experience to highlight {role_name}-relevant projects and skills",
                    "impact": "Shows how your background directly applies to target role",
                })
            
            # ── Strategy 6: ATS Keywords ──────────────────────────────
            if role_required_skills:
                suggestions.append({
                    "category": "ats_optimization",
                    "priority": "medium",
                    "action_type": "add_keywords",
                    "suggestion": f"Naturally incorporate role keywords: {', '.join(role_required_skills[:5])}",
                    "impact": "Improves ATS scanning and keyword match scores",
                })
            
            # ── Strategy 7: Impact Statements ─────────────────────────
            if not self._has_impact_statements(text):
                suggestions.append({
                    "category": "impact",
                    "priority": "high",
                    "action_type": "add_impact",
                    "suggestion": "Add business impact statements (e.g., 'Reduced costs by $50K', 'Improved efficiency by 40%')",
                    "impact": "Demonstrates value and ROI you bring to employers",
                })
            
            # ── Strategy 8: Technical Depth ───────────────────────────
            if role_name and any(kw in role_name.lower() for kw in ["senior", "lead", "principal"]):
                suggestions.append({
                    "category": "technical_depth",
                    "priority": "medium",
                    "action_type": "add_depth",
                    "suggestion": "Add technical depth: architecture decisions, system design, mentorship experience",
                    "impact": "Shows senior-level technical leadership and strategic thinking",
                })
            
            # Calculate improvement score (100 - penalty per issue)
            issue_count = len(suggestions)
            improvement_score = max(100 - (issue_count * 8), 0)  # -8 points per issue
            
            return {
                "suggestions": suggestions[:10],  # Top 10 most impactful
                "issue_count": issue_count,
                "improvement_score": round(improvement_score, 1),
            }
        except Exception as exc:
            logger.exception("Resume improvement analysis failed: %s", exc)
            return {
                "suggestions": [],
                "issue_count": 0,
                "improvement_score": 100.0,
            }
    
    def _has_sufficient_metrics(self, text: str) -> bool:
        """Check if resume has enough quantifiable metrics."""
        # Look for numbers with %, $, +, K, M suffixes
        metrics = re.findall(r"\d+[%$]|\d+\+|\d+[KM]|\$\d+|\d+%|by \d+", text, re.IGNORECASE)
        return len(metrics) >= 3  # At least 3 metrics is good
    
    def _detect_passive_voice(self, text: str) -> int:
        """Count passive voice occurrences."""
        count = 0
        text_lower = text.lower()
        for pattern in self.PASSIVE_PATTERNS:
            count += len(re.findall(pattern, text_lower))
        return count
    
    def _detect_weak_verbs(self, text: str) -> set[str]:
        """Find weak action verbs in text."""
        text_lower = text.lower()
        found = set()
        for verb in self.WEAK_VERBS:
            if re.search(r"\b" + verb + r"\b", text_lower):
                found.add(verb)
        return found
    
    def _has_impact_statements(self, text: str) -> bool:
        """Check if resume has impact/result statements."""
        impact_keywords = [
            "increased", "reduced", "improved", "achieved", "delivered",
            "saved", "generated", "grew", "accelerated", "optimized"
        ]
        text_lower = text.lower()
        return sum(1 for kw in impact_keywords if kw in text_lower) >= 2

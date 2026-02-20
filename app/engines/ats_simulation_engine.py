"""
TalentIQ — Engine 18: ATS Simulation Engine
Simulates how an Applicant Tracking System parses and evaluates a resume.

Output format is flattened for direct UI consumption:
    - keyword_report: {found: [...], missing: [...], density, coverage_percent}
    - section_completeness: {section_name: bool, ...}
    - readability: {score, bullet_count, action_verb_count, quantified_achievements}
    - formatting_risks: [str, ...]
    - alerts: [str, ...]
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class ATSSimulationEngine:
    """Simulate ATS scanning behavior and produce a compatibility report."""

    EXPECTED_SECTIONS: dict[str, list[str]] = {
        "contact_info": [
            r"(?:email|e-mail)\s*[:|\-]?\s*\S+@\S+",
            r"\b\d{10}\b",
            r"(?:phone|mobile|cell|tel)\s*[:|\-]?\s*[\d\s\-+()]{7,}",
            r"linkedin\.com",
            r"github\.com",
        ],
        "professional_summary": [
            r"(?:summary|objective|profile|about\s*me)",
        ],
        "skills": [
            r"(?:skills|technical\s*skills|core\s*competencies|technologies)",
        ],
        "experience": [
            r"(?:experience|work\s*history|employment|professional\s*experience)",
        ],
        "education": [
            r"(?:education|academic|qualification|degree)",
        ],
        "certifications": [
            r"(?:certification|certified|license|accreditation)",
        ],
        "projects": [
            r"(?:projects?|portfolio|key\s*projects?)",
        ],
    }

    FORMATTING_RISKS: list[dict[str, str]] = [
        {
            "pattern": r"┌|┐|└|┘|│|─|═|╔|╗|╚|╝|║",
            "message": "Table/box-drawing characters detected — may confuse ATS parsers",
            "severity": "high",
        },
        {
            "pattern": r"\[image\]|\[logo\]|\[photo\]|\[picture\]",
            "message": "Image references detected — ATS cannot read images",
            "severity": "high",
        },
        {
            "pattern": r"_{10,}|={10,}|\-{10,}|\*{10,}",
            "message": "Long separator lines detected — may cause parsing issues",
            "severity": "medium",
        },
        {
            "pattern": r"(?:page\s*\d|footer|header)",
            "message": "Header/footer markers detected — content may be missed by ATS",
            "severity": "low",
        },
        {
            "pattern": r"[^\x00-\x7F]{5,}",
            "message": "Extended Unicode characters detected — some ATS may not handle correctly",
            "severity": "medium",
        },
    ]

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def simulate(
        self,
        resume_text: str,
        target_keywords: list[str] | None = None,
    ) -> dict:
        """
        Run a full ATS simulation on resume text.

        Returns
        -------
        dict
            ats_compatibility_score, keyword_report (flat),
            formatting_risks (list[str]), section_completeness (flat bool dict),
            readability (flat), alerts (list[str])
        """
        try:
            logger.info("Running ATS simulation")
            text_lower = resume_text.lower()

            keyword_report = self._keyword_analysis(text_lower, target_keywords or [])
            formatting = self._formatting_check(resume_text)
            sections = self._section_completeness(text_lower)
            readability = self._readability_analysis(resume_text)
            alerts = self._generate_alerts(keyword_report, formatting, sections, readability)
            ats_score = self._compute_ats_score(keyword_report, formatting, sections, readability)

            return {
                "ats_compatibility_score": round(ats_score, 2),
                "keyword_report": keyword_report,
                "formatting_risks": formatting,
                "section_completeness": sections,
                "readability": readability,
                "alerts": alerts,
                "alert_count": len(alerts),
            }
        except Exception as exc:
            logger.exception("ATS simulation failed: %s", exc)
            return {
                "ats_compatibility_score": 0,
                "keyword_report": {"found": [], "missing": [], "density": 0, "coverage_percent": 0},
                "formatting_risks": [],
                "section_completeness": {},
                "readability": {"score": 0, "bullet_count": 0, "action_verb_count": 0, "quantified_achievements": 0},
                "alerts": ["ATS simulation encountered an error"],
                "alert_count": 1,
            }

    # -----------------------------------------------------------------
    # Keyword Analysis — returns flat format
    # -----------------------------------------------------------------

    def _keyword_analysis(self, text: str, target_keywords: list[str]) -> dict:
        """
        Returns
        -------
        dict
            found: list[str], missing: list[str], density: float,
            coverage_percent: float
        """
        word_count = max(len(text.split()), 1)
        found: list[str] = []
        missing: list[str] = []
        total_kw_occurrences = 0

        for kw in target_keywords:
            kw_lower = kw.lower().strip()
            if not kw_lower:
                continue
            count = len(re.findall(re.escape(kw_lower), text))
            if count > 0:
                found.append(kw)
                total_kw_occurrences += count
            else:
                missing.append(kw)

        coverage = (len(found) / len(target_keywords) * 100) if target_keywords else 0.0
        density = round(total_kw_occurrences / word_count * 100, 2)

        return {
            "found": sorted(found),
            "missing": sorted(missing),
            "density": density,
            "coverage_percent": round(coverage, 2),
            "total_keywords": len(target_keywords),
            "word_count": word_count,
        }

    # -----------------------------------------------------------------
    # Formatting Check — returns flat list of strings
    # -----------------------------------------------------------------

    def _formatting_check(self, text: str) -> list[str]:
        """Return list of risk description strings."""
        risks: list[str] = []
        for check in self.FORMATTING_RISKS:
            if re.search(check["pattern"], text, re.IGNORECASE):
                risks.append(check["message"])
        return risks

    # -----------------------------------------------------------------
    # Section Completeness — returns flat {name: bool} dict
    # -----------------------------------------------------------------

    def _section_completeness(self, text: str) -> dict[str, bool]:
        """Return {section_name: present_bool} flat dict."""
        result: dict[str, bool] = {}
        for section, patterns in self.EXPECTED_SECTIONS.items():
            result[section] = any(
                re.search(p, text, re.IGNORECASE) for p in patterns
            )
        return result

    # -----------------------------------------------------------------
    # Readability — returns flat dict with standard keys
    # -----------------------------------------------------------------

    def _readability_analysis(self, text: str) -> dict:
        """
        Returns
        -------
        dict
            score, bullet_count, action_verb_count, quantified_achievements,
            word_count, sentence_count, avg_sentence_length
        """
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        words = text.split()
        word_count = len(words)

        avg_sentence_len = (
            round(word_count / len(sentences), 1) if sentences else 0
        )
        long_sentences = sum(1 for s in sentences if len(s.split()) > 25)

        bullet_count = len(
            re.findall(r"^[\s]*[•\-\*\u2022\u25CF]", text, re.MULTILINE)
        )

        action_verbs = [
            "developed", "designed", "implemented", "managed", "led", "created",
            "built", "optimized", "delivered", "achieved", "improved", "reduced",
            "increased", "launched", "established", "coordinated", "analyzed",
            "automated", "streamlined", "spearheaded", "architected", "mentored",
        ]
        lines = [ln.strip().lower() for ln in text.split("\n") if ln.strip()]
        action_verb_count = sum(
            1 for line in lines
            if any(line.startswith(v) for v in action_verbs)
        )

        quantified = len(re.findall(
            r"\d+%|\$\d+|\d+\+?\s*(?:users|clients|projects|team|customers|revenue|sales)",
            text,
            re.IGNORECASE,
        ))

        # Score 0-100
        score = 70.0
        if avg_sentence_len > 30:
            score -= 10
        if avg_sentence_len < 10:
            score += 5
        if bullet_count > 5:
            score += 10
        if action_verb_count > 3:
            score += 5
        if quantified > 2:
            score += 5
        if long_sentences > 5:
            score -= 10
        score = max(0, min(100, score))

        return {
            "score": round(score, 2),
            "bullet_count": bullet_count,
            "action_verb_count": action_verb_count,
            "quantified_achievements": quantified,
            "word_count": word_count,
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_sentence_len,
        }

    # -----------------------------------------------------------------
    # Alerts — returns flat list of strings
    # -----------------------------------------------------------------

    def _generate_alerts(
        self,
        keyword_report: dict,
        formatting_risks: list[str],
        sections: dict[str, bool],
        readability: dict,
    ) -> list[str]:
        alerts: list[str] = []

        if keyword_report.get("coverage_percent", 100) < 50:
            alerts.append(
                f"Low keyword coverage ({keyword_report['coverage_percent']}%) "
                f"— add more role-specific keywords."
            )

        for sec_name, present in sections.items():
            if not present:
                alerts.append(
                    f"Missing section: {sec_name.replace('_', ' ').title()} — consider adding it."
                )

        for risk in formatting_risks:
            alerts.append(risk)

        if readability.get("score", 100) < 50:
            alerts.append(
                "Low readability score — simplify sentences and use more bullet points."
            )
        if readability.get("bullet_count", 0) < 3:
            alerts.append(
                "Consider using more bullet points for better ATS parsing."
            )
        if readability.get("quantified_achievements", 0) < 2:
            alerts.append(
                "Add quantifiable achievements (numbers, percentages, metrics)."
            )

        return alerts

    # -----------------------------------------------------------------
    # Overall Score
    # -----------------------------------------------------------------

    @staticmethod
    def _compute_ats_score(
        keyword_report: dict,
        formatting_risks: list[str],
        sections: dict[str, bool],
        readability: dict,
    ) -> float:
        kw_score = keyword_report.get("coverage_percent", 50) * 0.35

        total_sections = max(len(sections), 1)
        present_count = sum(1 for v in sections.values() if v)
        sec_pct = present_count / total_sections * 100
        sec_score = sec_pct * 0.25

        read_score = readability.get("score", 50) * 0.25

        # Formatting penalty
        fmt_penalty = min(len(formatting_risks) * 8, 30)
        fmt_score = (100 - fmt_penalty) * 0.15

        raw = kw_score + sec_score + read_score + fmt_score
        return max(0, min(100, raw))

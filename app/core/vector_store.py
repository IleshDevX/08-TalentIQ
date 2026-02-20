"""
TalentIQ — FAISS Vector Store
Precomputes job-role embeddings from roles_database.json (primary) and
job_roles_master.csv (legacy fallback) then builds a FAISS index for
fast cosine-similarity search.

Call ``initialise()`` once at application startup.
After that, use ``search(query_vector, top_k)`` from any engine.
"""

from __future__ import annotations

import csv
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from app.config import settings
from app.core.model_loader import model

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data container for a single job role
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class JobRole:
    role_id: str
    role_name: str
    role_category: str
    role_level: str
    domain: str
    description: str
    industry_sector: str
    education_required: str
    years_experience_min: str
    years_experience_max: str


# ---------------------------------------------------------------------------
# Module-level globals — populated once by ``initialise()``
# ---------------------------------------------------------------------------

_index: faiss.IndexFlatIP | None = None      # FAISS inner-product index
_roles: list[JobRole] = []                    # parallel list (index ↔ role)
_embeddings: np.ndarray | None = None         # (N, 384) matrix kept for debug
_ready: bool = False
_roles_db: dict = {}                          # Full roles_database.json data


# ---------------------------------------------------------------------------
# Helper — build a single embedding-friendly sentence for a role
# ---------------------------------------------------------------------------

def _compose_text(role: JobRole) -> str:
    """
    Merge all meaningful fields into one sentence so the encoder captures
    as much semantics as possible.
    """
    parts: list[str] = [role.role_name]

    desc = role.description.strip()
    if desc and desc.lower() not in ("auto generated role", "n/a", "-", ""):
        parts.append(desc)

    parts.append(f"Category: {role.role_category}")
    parts.append(f"Domain: {role.domain}")
    parts.append(f"Level: {role.role_level}")
    parts.append(f"Industry: {role.industry_sector}")
    parts.append(f"Education: {role.education_required}")
    parts.append(
        f"Experience: {role.years_experience_min}–{role.years_experience_max} years"
    )
    return ". ".join(parts)


# ---------------------------------------------------------------------------
# Load roles from JSON (primary source — 85 roles with rich data)
# ---------------------------------------------------------------------------

def _load_roles_json(json_path: Path) -> list[JobRole]:
    """Load roles from roles_database.json — the comprehensive role DB."""
    with open(json_path, encoding="utf-8") as fh:
        data = json.load(fh)

    global _roles_db  # noqa: PLW0603
    _roles_db = data.get("roles", {})

    roles: list[JobRole] = []
    for role_key, info in _roles_db.items():
        roles.append(JobRole(
            role_id=role_key,
            role_name=info["role_name"],
            role_category=info.get("category", "General"),
            role_level=info.get("level", "Mid"),
            domain=info.get("domain", "General"),
            description=info.get("description", ""),
            industry_sector=info.get("domain", "General"),
            education_required=info.get("education", ""),
            years_experience_min=str(info.get("min_experience", 0)),
            years_experience_max=str(info.get("max_experience", 15)),
        ))
    logger.info("Loaded %d roles from %s", len(roles), json_path.name)
    return roles


# ---------------------------------------------------------------------------
# Load & deduplicate CSV (legacy fallback)
# ---------------------------------------------------------------------------

def _load_roles_csv(csv_path: Path) -> list[JobRole]:
    """Read CSV and keep one representative row per unique ``role_name``."""
    seen: dict[str, JobRole] = {}
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = row["role_name"].strip()
            if name not in seen:
                seen[name] = JobRole(
                    role_id=row.get("role_id", ""),
                    role_name=name,
                    role_category=row.get("role_category", "General"),
                    role_level=row.get("role_level", "Mid"),
                    domain=row.get("domain", "General"),
                    description=row.get("description", ""),
                    industry_sector=row.get("industry_sector", "General"),
                    education_required=row.get("education_required", ""),
                    years_experience_min=row.get("years_experience_min", "0"),
                    years_experience_max=row.get("years_experience_max", "15"),
                )
    logger.info("Loaded %d unique roles from %s", len(seen), csv_path.name)
    return list(seen.values())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def initialise() -> None:
    """
    Load roles → encode → build FAISS index.
    Prefers roles_database.json; falls back to job_roles_master.csv.
    Safe to call multiple times; subsequent calls are no-ops.
    """
    global _index, _roles, _embeddings, _ready  # noqa: PLW0603

    if _ready:
        logger.info("Vector store already initialised — skipping.")
        return

    # Primary: roles_database.json (comprehensive 85-role DB)
    json_path = settings.DATASETS_DIR / "roles_database.json"
    csv_path = settings.DATASETS_DIR / "job_roles_master.csv"

    if json_path.exists():
        _roles = _load_roles_json(json_path)
    elif csv_path.exists():
        _roles = _load_roles_csv(csv_path)
    else:
        raise FileNotFoundError(
            f"No role dataset found. Expected {json_path} or {csv_path}"
        )

    if not _roles:
        raise ValueError("Role dataset contains no usable rows.")

    # 2. Compose text & encode
    texts = [_compose_text(r) for r in _roles]
    logger.info("Encoding %d role descriptions …", len(texts))
    t0 = time.perf_counter()
    _embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    _embeddings = np.asarray(_embeddings, dtype=np.float32)
    elapsed = time.perf_counter() - t0
    logger.info("Encoded %d roles in %.2f s → matrix %s", len(texts), elapsed, _embeddings.shape)

    # 3. Build FAISS inner-product index (cosine sim because vectors are L2-normed)
    dim = _embeddings.shape[1]
    _index = faiss.IndexFlatIP(dim)
    _index.add(_embeddings)  # type: ignore[call-arg]
    logger.info("FAISS index built — %d vectors, dim=%d", _index.ntotal, dim)

    _ready = True


def search(query_vector: np.ndarray, top_k: int | None = None) -> list[dict]:
    """
    Return the top-k most-similar job roles for a given resume embedding.

    Parameters
    ----------
    query_vector : np.ndarray
        1-D array of shape ``(384,)`` — the resume embedding.
    top_k : int, optional
        Number of results (default ``settings.TOP_K_ROLES``).

    Returns
    -------
    list[dict]
        Each dict has ``role``, ``score``, and ``rank`` keys.
    """
    if not _ready or _index is None:
        raise RuntimeError("Vector store not initialised. Call initialise() first.")

    if top_k is None:
        top_k = settings.TOP_K_ROLES
    top_k = min(top_k, _index.ntotal)

    # Normalise the query vector for cosine similarity via inner product
    qv = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
    faiss.normalize_L2(qv)

    scores, indices = _index.search(qv, top_k)  # type: ignore[call-arg]

    results: list[dict] = []
    for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
        role = _roles[int(idx)]
        results.append({
            "rank": rank,
            "role_name": role.role_name,
            "role_category": role.role_category,
            "role_level": role.role_level,
            "domain": role.domain,
            "industry_sector": role.industry_sector,
            "score": round(float(score), 4),
        })
    return results


def get_roles() -> list[JobRole]:
    """Return the deduplicated role list (for inspection / other engines)."""
    return list(_roles)


def get_embeddings() -> np.ndarray | None:
    """Return the (N, 384) embedding matrix (for debugging)."""
    return _embeddings


def is_ready() -> bool:
    """Check whether the vector store has been initialised."""
    return _ready


def get_roles_db() -> dict:
    """Return the full roles database dict (from JSON)."""
    return _roles_db


def get_role_names() -> list[str]:
    """Return a sorted list of all available role names."""
    return sorted(r.role_name for r in _roles)


def get_role_info(role_name: str) -> dict | None:
    """Look up a role's full info from the JSON database by name."""
    for _key, info in _roles_db.items():
        if info["role_name"].lower() == role_name.lower():
            return info
    return None


def get_default_jd(role_name: str) -> str:
    """Return the default job description for a role, or empty string."""
    info = get_role_info(role_name)
    return info.get("default_jd", "") if info else ""


def get_role_skills(role_name: str) -> list[str]:
    """Return required + preferred skills for a role from the JSON DB."""
    info = get_role_info(role_name)
    if not info:
        return []
    required = info.get("required_skills", [])
    preferred = info.get("preferred_skills", [])
    return list(dict.fromkeys(required + preferred))  # deduplicated, order preserved


def get_role_keywords(role_name: str) -> list[str]:
    """Return keywords for a role from the JSON DB."""
    info = get_role_info(role_name)
    return info.get("keywords", []) if info else []

"""
TalentIQ — Singleton Model Loader
Loads SentenceTransformer ONCE at startup and reuses across all engines.
"""

from sentence_transformers import SentenceTransformer
from app.config import settings

model = SentenceTransformer(settings.EMBEDDING_MODEL)

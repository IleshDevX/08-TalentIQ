"""
TalentIQ — Engine #6: Resume Embedding Engine
Generates 384-dimension vector embeddings from resume text.
"""

import numpy as np
from app.core.model_loader import model


class ResumeEmbeddingEngine:

    def generate(self, text: str) -> np.ndarray:
        """Generate a 384-dim embedding vector for the given resume text."""
        embedding = model.encode(text)
        return np.asarray(embedding)

"""
TalentIQ — Engine #3: Text Preprocessing Engine
Cleans and tokenizes raw resume text for downstream analysis.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Ensure required NLTK data is available
for resource in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    nltk.download(resource, quiet=True)


class TextPreprocessingEngine:

    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

    def clean(self, text: str) -> str:
        """Normalize whitespace and strip non-alphanumeric characters."""
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        return text.strip()

    def tokenize(self, text: str) -> list[str]:
        """Tokenize and lemmatize text, removing stopwords."""
        tokens = word_tokenize(text)
        return [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token.lower() not in self.stop_words and len(token) > 1
        ]

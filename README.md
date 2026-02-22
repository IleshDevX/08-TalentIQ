<p align="center">
  <img src="https://img.shields.io/badge/TalentIQ-AI%20Career%20Intelligence-6366F1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkw2LjUgMTEuNSAxMiA4bDUuNSAzLjVMMTIgMnoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=&logoColor=white" alt="TalentIQ" />
</p>

<h1 align="center">🧠 TalentIQ</h1>
<h3 align="center">AI-Powered Resume Analyzer & Career Intelligence Platform</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.129-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/NLP-Sentence%20Transformers-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/Vector%20Search-FAISS-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

<p align="center">
  <b>Smarter Careers Start Here.</b><br/>
  Upload your resume → Get instant AI-driven insights on role matching, ATS scoring, skill gaps, career paths, and actionable improvements.
</p>

---

## 📸 Screenshots

| Overview Dashboard | Role Match | Skills & Gaps |
|:---:|:---:|:---:|
| Multi-dimension radar + ATS breakdown | Hero card + scored grid with breakdowns | Matched, missing & trending skills |

| Career Paths | JD & ATS Analysis | Improvements |
|:---:|:---:|:---:|
| Timeline-based progression paths | Side-by-side JD comparison + ATS sim | Priority-ranked suggestions |

---

## ✨ Features

### 🎯 Core Intelligence
- **Hybrid Role Matching** — Combines semantic similarity (40%), skill overlap (35%), experience alignment (15%), and keyword relevance (10%) to rank the best-fit roles
- **ATS Scoring Engine** — Explainable ATS compatibility score with per-category breakdown (skills, experience, semantics)
- **ATS Simulation** — Simulates real ATS parsing: keyword coverage, section completeness, readability, formatting risks
- **Job Description Comparison** — Side-by-side resume vs. JD analysis with matched/missing keywords and per-section scores

### 🔬 Deep Analysis
- **Skill Gap Detection** — Identifies missing mandatory skills for target roles using exact + fuzzy matching
- **Skill Normalization** — Maps abbreviations & synonyms (e.g., "js" → "JavaScript", "py" → "Python") to canonical names
- **Soft Skill Detection** — NLP-based identification of leadership, communication, teamwork, and adaptability signals
- **Industry Insights** — Market demand alignment: high-demand skills you have + trending skills to learn

### 🚀 Career Growth
- **Career Path Suggestions** — AI-generated progression paths (promotion, lateral, pivot) based on role taxonomy
- **Certification Recommendations** — Smart cert suggestions using fuzzy skill matching and role-based popularity
- **Resume Improvement Engine** — Actionable, priority-ranked suggestions for quantification, action verbs, keywords, and formatting
- **Role Explanation (XAI)** — Human-readable verdicts explaining *why* you're a strong/moderate/growth match

### 🖥️ Premium Dashboard
- **7-Tab Layout** — Overview, Role Match, JD & ATS, Skills & Gaps, Career, Improve, Report
- **Glassmorphism UI** — Modern cards with depth layers, animated score rings, and micro-interactions
- **Responsive Design** — CSS Grid-based layouts optimized for all screen sizes
- **Full Report Export** — Download complete JSON analysis report

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Frontend                    │
│              (streamlit_app.py — Port 8501)             │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP (REST API)
┌─────────────────────▼───────────────────────────────────┐
│                   FastAPI Backend                       │
│               (app/main.py — Port 8000)                 │
├─────────────────────────────────────────────────────────┤
│  Routers:  /upload  ·  /analyze  ·  /roles  ·  /health  │
├─────────────────────────────────────────────────────────┤
│              Analysis Service (Orchestrator)            │
│         Connects all 17 engines in a pipeline           │
├─────────────────────────────────────────────────────────┤
│                    Engine Layer                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │Processing    │ │ Preprocessing│ │Info Extraction   │ │
│  └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │Resume Embed  │ │Semantic Match│ │ ATS Scoring      │ │
│  └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ Skill Gap    │ │Normalize     │ │ Soft Skills      │ │
│  └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │JD Comparison │ │ATS Simulation│ │ Career Paths     │ │
│  └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │Certification │ │Role Explain  │ │Resume Improve    │ │
│  └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐                      │
│  │Industry      │ │  Feedback    │                      │
│  └──────────────┘ └──────────────┘                      │
├─────────────────────────────────────────────────────────┤
│                     Core Layer                          │
│  ┌──────────────────┐  ┌─────────────────────────────┐  │
│  │ Model Loader     │  │ FAISS Vector Store          │  │
│  │(SentenceTransf.) │  │ (Role Embeddings Index)     │  │
│  └──────────────────┘  └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                   Datasets (20 files)                   │
│  roles_database.json · skills_master.csv  ...           │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit, Plotly, Custom HTML/CSS |
| **Backend** | FastAPI, Uvicorn |
| **NLP** | Sentence-Transformers (`all-MiniLM-L6-v2`), spaCy, NLTK |
| **Vector Search** | FAISS (Facebook AI Similarity Search) |
| **ML/DL** | PyTorch, scikit-learn, Transformers (HuggingFace) |
| **File Parsing** | pdfplumber, pdfminer, python-docx |
| **Data** | Pandas, NumPy |
| **Language** | Python 3.10+ |

---

## 📁 Project Structure

```
TalentIQ/
├── run.py                    # Single-command launcher (API + UI)
├── streamlit_app.py          # Streamlit frontend dashboard
├── requirements.txt          # Python dependencies
├── pyrightconfig.json        # Type checking config
│
├── app/
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Application settings & constants
│   │
│   ├── core/
│   │   ├── model_loader.py   # Singleton SentenceTransformer loader
│   │   └── vector_store.py   # FAISS index builder & searcher
│   │
│   ├── engines/
│   │   ├── file_processing_engine.py      # PDF/DOCX text extraction
│   │   ├── preprocessing_engine.py        # Text cleaning & tokenization
│   │   ├── information_extraction_engine.py # Structured profile extraction
│   │   ├── skill_normalization_engine.py   # Skill synonym resolution
│   │   ├── resume_embedding_engine.py      # Vector embedding generation
│   │   ├── semantic_matching_engine.py     # Hybrid role matching
│   │   ├── ats_scoring_engine.py           # ATS compatibility scoring
│   │   ├── ats_simulation_engine.py        # ATS parser simulation
│   │   ├── skill_gap_engine.py             # Missing skills detection
│   │   ├── jd_comparison_engine.py         # Resume vs. JD comparison
│   │   ├── soft_skill_engine.py            # Soft skill signal detection
│   │   ├── career_path_engine.py           # Career progression paths
│   │   ├── certification_engine.py         # Certification recommendations
│   │   ├── industry_insight_engine.py      # Market demand alignment
│   │   ├── role_explanation_engine.py      # Explainable AI verdicts
│   │   ├── resume_improvement_engine.py    # Improvement suggestions
│   │   └── feedback_engine.py              # Report aggregator
│   │
│   ├── routers/
│   │   ├── upload.py          # POST /upload endpoint
│   │   └── analyze.py         # POST /analyze & GET /roles endpoints
│   │
│   └── services/
│       └── analysis_service.py # Central pipeline orchestrator
│
├── datasets/                  # 20 curated data files
│   ├── roles_database.json    # Complete role definitions
│   ├── skills_master.csv      # Master skills taxonomy
│   ├── skill_synonyms.csv     # Skill abbreviation mappings
│   ├── job_roles_master.csv   # Role metadata
│   ├── role_skill_mapping.csv # Role → required skills
│   ├── role_keyword_mapping.csv # Role → domain keywords
│   ├── job_role_embeddings.csv # Precomputed role vectors
│   ├── career_path_mapping.csv # Career progression rules
│   ├── certification_master.csv # Certification database
│   ├── skill_demand_trends.csv # Market demand data
│   ├── soft_skill_indicators.csv # Soft skill keyword patterns
│   ├── action_verbs_master.csv # Strong action verb list
│   ├── weak_phrases_master.csv # Weak phrases to avoid
│   ├── scoring_weights_config.csv # ATS scoring weights
│   ├── resume_structure_rules.csv # Resume format rules
│   ├── domain_taxonomy.csv    # Domain classification
│   ├── tech_stack_combinations.csv # Technology groupings
│   ├── interview_question_bank.csv # Interview prep data
│   ├── resume_training_samples.csv # Training examples
│   └── model_metadata.csv     # Model configuration
│
├── uploads/                   # Uploaded resume files (gitignored)
└── logs/                      # Application logs (gitignored)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Git**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/TalentIQ.git
cd TalentIQ

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download spaCy model (required for NLP)
python -m spacy download en_core_web_sm
```

### Running the Application

#### Option 1: Single Command (Recommended)
```bash
python run.py
```
This starts **both** the FastAPI backend (port 8000) and Streamlit frontend (port 8501).

#### Option 2: Start Services Separately
```bash
# Terminal 1 — Backend API
python run.py --api

# Terminal 2 — Frontend Dashboard
python run.py --ui
```

#### Option 3: Manual Start
```bash
# Terminal 1 — Backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Frontend
streamlit run streamlit_app.py
```

### Access the Application

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8501 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

---

## 📖 How It Works

```
Resume Upload (PDF/DOCX)
    │
    ▼
Text Extraction ──► Preprocessing ──► Information Extraction
    │                                        │
    ▼                                        ▼
Resume Embedding                    Skill Normalization
    │                                        │
    ▼                                        │
FAISS Vector Search ◄────────────────────────┘
    │
    ▼
Semantic Role Matching (Hybrid 4-Factor Scoring)
    │
    ├──► ATS Scoring (Explainable)
    ├──► ATS Simulation (Real-world)
    ├──► Skill Gap Analysis
    ├──► JD Comparison (if provided)
    ├──► Soft Skill Detection
    ├──► Career Path Suggestions
    ├──► Certification Recommendations
    ├──► Industry Insights
    ├──► Role Explanation (XAI)
    └──► Resume Improvements
            │
            ▼
    Unified Report (Dashboard)
```

---

## 🔌 API Reference

### `POST /upload`
Upload a resume file for text extraction.
- **Body**: `multipart/form-data` with `file` (PDF or DOCX, max 10 MB)
- **Response**: Extracted text + file metadata

### `POST /analyze`
Run the full analysis pipeline.
- **Body**: `multipart/form-data` with `file`, optional `target_role`, optional `job_description`
- **Response**: Complete analysis report (role matches, ATS score, skill gaps, career paths, improvements, etc.)

### `GET /roles`
List all available target roles for the dropdown.
- **Response**: Array of role names

### `GET /health`
Health check endpoint.

> 📄 Full interactive docs available at **http://localhost:8000/docs** (Swagger UI)

---

## 🤖 NLP Models Used

| Model | Purpose | Dimensions |
|-------|---------|-----------|
| **all-MiniLM-L6-v2** | Resume & role embeddings | 384 |
| **en_core_web_sm** (spaCy) | Tokenization, NER, lemmatization | — |
| **NLTK** | Stopword removal, text preprocessing | — |

> Models are automatically downloaded on first run. The SentenceTransformer model (~80 MB) is cached locally.

---

## 📊 Datasets

TalentIQ ships with **20 curated datasets** covering:

| Dataset | Records | Purpose |
|---------|---------|---------|
| `roles_database.json` | 50+ roles | Complete role definitions with skills, keywords, experience ranges |
| `skills_master.csv` | 500+ skills | Master skills taxonomy |
| `skill_synonyms.csv` | 300+ mappings | Abbreviation → canonical skill |
| `certification_master.csv` | 100+ certs | Professional certifications |
| `skill_demand_trends.csv` | Market data | Current skill demand trends |
| `career_path_mapping.csv` | Path rules | Career progression relationships |
| *...and 14 more* | | |

---

## ⚙️ Configuration

Key settings in `app/config.py`:

```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # SentenceTransformer model
EMBEDDING_DIM   = 384                  # Vector dimensions
TOP_K_ROLES     = 5                    # Default roles to match
MAX_FILE_SIZE_MB = 10                  # Upload limit
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ using Python, FastAPI, Streamlit & Sentence-Transformers<br/>
  <b>TalentIQ</b> — Smarter Careers Start Here.
</p>

# Project 08: Malayalam Movie Review Sentiment Polarity & Morphological Profiler

[![Course](https://img.shields.io/badge/Course-Programming%20in%20Python-blue.svg)](https://duk.ac.in)
[![Python](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 1. Project Overview & Domain Context

- **Institution:** Digital University Kerala (MTech AI / MSc AI)
- **Course:** M4010104 / M4020104 — Programming in Python | **Instructor:** Dr. Sunil TT
- **Dataset:** Malayalam Movie Review Sentiment Dataset on Kaggle (https://www.kaggle.com/datasets/abhij

## 2. System Architecture & Pipeline Design

[Provide an ASCII or Mermaid architecture flow diagram showing raw ingestion -> validation -> analyzer -

## 3. Installation & Environment Setup

```bash
git clone https://github.com/<your-team>/malayalam-movie-review-analyzer.git
cd malayalam-movie-review-analyzer
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Execution Instructions

### A. Running the Standalone Application

```bash
python run_pipeline.py --input data/raw/malayalam_movie_reviews_raw.csv --output-dir data/processed --re
```

### B. Running the Development Notebook

```bash
jupyter notebook notebooks/development_cycle.ipynb
```

## 5. Key Analytical & Statistical Findings (Q1–Q12 Summary)

[Provide a concise markdown summary table detailing raw vs. clean counts, regression coefficients, anoma

## 6. Standalone Interactive Visualizations

The standalone interactive Plotly dashboard is generated locally as an offline HTML artifact:

- File Location: `reports/interactive_dashboard.html` (viewable directly in any standard web browser wit

## 7. Contributor Git Commit & Pull Request Log Table

<!-- CONTRIBUTOR-LOG:START -->

| Contributor Name | GitHub Handle | Assigned Module / Tasks | Verified Commit Hash Range | Merged Pull Request |
| :--------------- | :------------ | :---------------------- | :------------------------- | :------------------ |
| Chetan Krishna | `@chetancs26` | readme done chetan26 — `README.md` | [`6963464`](https://github.com/sankalpcs26-byte/Malayalam_Movie_Reviews_Detailed_Specification/commit/6963464da16b3e962bcbcd559bb4873b29d1bf2d) | [#1](https://github.com/sankalpcs26-byte/Malayalam_Movie_Reviews_Detailed_Specification/pull/1) |
| sankalpcs26-byte | `@sankalpcs26-byte` | envirnment setup by team lead — `data/processed/clean_malayalam_movies.csv`, `data/processed/movie_reviews_audit.log`, `data/raw/malayalam_movie_reviews_raw.csv`, `notebooks/development_cycle.ipynb`, `src/ingestion.py` | [`3058de9`](https://github.com/sankalpcs26-byte/Malayalam_Movie_Reviews_Detailed_Specification/commit/3058de9e8e0d595b729d3b35912d6442fc24d977) | [#2](https://github.com/sankalpcs26-byte/Malayalam_Movie_Reviews_Detailed_Specification/pull/2) |

<!-- CONTRIBUTOR-LOG:END -->

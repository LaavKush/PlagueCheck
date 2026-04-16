# PlagueCheck — ADSA Plagiarism Detection Engine

A B.Tech 3rd Year ADSA project that detects plagiarism by:
1. Extracting key phrases from your document
2. Searching the web via DuckDuckGo (no API key needed)
3. Fetching and parsing top result pages
4. Running 4 string-matching algorithms against each source

---

## Algorithms Implemented (from scratch)

| Algorithm | Purpose | Time Complexity |
|---|---|---|
| **KMP (Knuth-Morris-Pratt)** | Exact sentence matching | O(n + m) |
| **Rabin-Karp** (rolling hash) | N-gram fingerprint matching | O(n + mk) avg |
| **Winnowing / Shingling** | Fuzzy/paraphrase detection (Jaccard) | O(n) |
| **Z-Algorithm** | Longest common segment detection | O(n) |

Combined weighted score = 35% KMP + 30% RK + 20% Winnowing + 15% Z-Algo

---

## Project Structure

```
plagiarism-detector/
├── backend/
│   ├── algorithms.py   ← All 4 ADSA algorithms (pure Python, no shortcuts)
│   ├── searcher.py     ← DuckDuckGo scraper + web page fetcher
│   └── app.py          ← Flask REST API
├── frontend/
│   └── index.html      ← Beautiful single-page UI
├── requirements.txt
└── README.md
```

---

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the Flask server
python app.py

# 3. Open in browser
# http://localhost:5000
```

---

## How It Works (Flow)

```
User Input (text)
      │
      ▼
Extract Key Phrases (3 sentences)
      │
      ▼
DuckDuckGo Search (per phrase)
      │
      ▼
Fetch Top Web Pages (BeautifulSoup)
      │
      ▼
Run Algorithms against each page:
  ├─ KMP          → exact sentence match
  ├─ Rabin-Karp   → n-gram hash match
  ├─ Winnowing    → Jaccard shingle similarity
  └─ Z-Algorithm  → longest common segments
      │
      ▼
Weighted Combined Score → Verdict
```

---

## Verdict Thresholds

| Score | Verdict |
|---|---|
| 0–10% | ✅ Clean |
| 10–30% | 🔵 Low Similarity |
| 30–60% | 🟡 Moderate |
| 60%+ | 🔴 High Plagiarism Risk |

---

## Notes

- DuckDuckGo is scraped via HTML endpoint (no API key required)
- Polite 0.5–1.2s delay between requests to avoid rate limiting
- Max 4 sources fetched per check (adjustable in `searcher.py`)
- All algorithms written from scratch — no string library shortcuts

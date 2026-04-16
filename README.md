# 🔍 PlagueCheck — ADSA Plagiarism Detection Engine
### Detect Similarity. Uncover Hidden Matches. Think Like an Algorithm.

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a0f,50:111118,100:1e1e2e&height=200&section=header&text=PlagueCheck&fontSize=40&fontColor=e8ff47&animation=fadeIn" />
</p>

<p align="center">
  <b>Multi-Algorithm Plagiarism Detection Engine powered by ADSA concepts</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Algorithms-KMP%20%7C%20RabinKarp%20%7C%20Winnowing-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Backend-Flask-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Web-DuckDuckGo-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-orange?style=for-the-badge" />
</p>

---

An ADSA project that detects plagiarism by:
1. Extracting key phrases from your document
2. Searching the web via DuckDuckGo (no API key needed)
3. Fetching and parsing top result pages
4. Running 4 string-matching algorithms against each source

---

## Demo

<p align="center">
  <img src="images/demo.png" alt="PlagueCheck Demo" width="90%" />
</p>

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

<p align="center">
  <img src="images/workflow.png" alt="Workflow Diagram" width="90%" />
</p>

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
- All algorithms written from scratch — no string library shortcuts

## Author

**Laavanya Kushwaha**  
Web Development | AI | Machine Learning  

---

## ⭐ Support

If you like this project:

- Star the repo  
- Fork it  
- Share it  

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:1e1e2e,50:111118,100:0a0a0f&height=120&section=footer"/>
</p>

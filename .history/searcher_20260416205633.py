# # ============================================================
# # Web Search via DuckDuckGo + Content Scraper
# # ============================================================

# import requests
# from bs4 import BeautifulSoup
# import re
# import time
# import random


# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/120.0.0.0 Safari/537.36"
#     ),
#     "Accept-Language": "en-US,en;q=0.9",
# }


# def extract_key_phrases(text: str, num_phrases: int = 3) -> list[str]:
#     """
#     Extract the most distinctive phrases from the document
#     to use as search queries.
#     Strategy: pick sentences of medium length (not too short, not too long).
#     """
#     sentences = re.split(r'(?<=[.!?])\s+', text.strip())
#     # Filter: 8–20 words, no special chars
#     good = [
#         s.strip() for s in sentences
#         if 8 <= len(s.split()) <= 20 and re.search(r'[a-zA-Z]', s)
#     ]
#     # Pick spread-out sentences
#     if not good:
#         words = text.split()
#         good = [' '.join(words[i:i+10]) for i in range(0, min(30, len(words)), 10)]

#     step = max(1, len(good) // num_phrases)
#     selected = [good[i] for i in range(0, len(good), step)][:num_phrases]
#     return selected


# def duckduckgo_search(query: str, max_results: int = 5) -> list[dict]:
#     """
#     Scrape DuckDuckGo HTML search results.
#     Returns list of {title, url, snippet}.
#     """
#     url = "https://html.duckduckgo.com/html/"
#     params = {"q": query, "kl": "us-en"}

#     try:
#         resp = requests.post(url, data=params, headers=HEADERS, timeout=10)
#         resp.raise_for_status()
#     except Exception as e:
#         print(f"[DDG Search Error] {e}")
#         return []

#     soup = BeautifulSoup(resp.text, "html.parser")
#     results = []

#     for result in soup.select(".result")[:max_results]:
#         title_tag = result.select_one(".result__title a")
#         snippet_tag = result.select_one(".result__snippet")
#         if not title_tag:
#             continue

#         href = title_tag.get("href", "")
#         # DDG wraps URLs — extract real URL
#         if "uddg=" in href:
#             from urllib.parse import unquote, urlparse, parse_qs
#             parsed = urlparse(href)
#             real_url = unquote(parse_qs(parsed.query).get("uddg", [""])[0])
#         else:
#             real_url = href

#         if not real_url.startswith("http"):
#             continue

#         results.append({
#             "title": title_tag.get_text(strip=True),
#             "url": real_url,
#             "snippet": snippet_tag.get_text(strip=True) if snippet_tag else ""
#         })

#     return results


# def fetch_page_text(url: str, max_chars: int = 8000) -> str:
#     """
#     Fetch a webpage and extract clean body text.
#     """
#     try:
#         resp = requests.get(url, headers=HEADERS, timeout=8)
#         resp.raise_for_status()
#         soup = BeautifulSoup(resp.text, "html.parser")

#         # Remove noise
#         for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
#             tag.decompose()

#         # Get main content preferably
#         main = soup.find("article") or soup.find("main") or soup.find("body")
#         if not main:
#             return ""

#         text = main.get_text(separator=" ", strip=True)
#         text = re.sub(r'\s+', ' ', text)
#         return text[:max_chars]

#     except Exception as e:
#         print(f"[Fetch Error] {url}: {e}")
#         return ""


# def search_and_fetch_sources(document: str, max_sources: int = 4) -> list[dict]:
#     """
#     Full pipeline:
#     1. Extract key phrases from the document
#     2. Search DuckDuckGo for each phrase
#     3. Fetch and extract text from top results
#     Returns list of {title, url, snippet, content}
#     """
#     phrases = extract_key_phrases(document, num_phrases=3)
#     seen_urls = set()
#     sources = []

#     for phrase in phrases:
#         if len(sources) >= max_sources:
#             break

#         results = duckduckgo_search(phrase, max_results=3)

#         for r in results:
#             if len(sources) >= max_sources:
#                 break
#             if r["url"] in seen_urls:
#                 continue
#             seen_urls.add(r["url"])

#             content = fetch_page_text(r["url"])
#             if len(content) < 100:
#                 continue

#             sources.append({
#                 "title": r["title"],
#                 "url": r["url"],
#                 "snippet": r["snippet"],
#                 "content": content
#             })

#             time.sleep(random.uniform(0.5, 1.2))  # polite delay

#     return sources

import re
from collections import defaultdict

# -------------------------------
# BETTER PREPROCESSING (FIXED)
# -------------------------------
STOPWORDS = {"the","is","in","and","of","to","a","for","on","with"}

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)   # FIXED
    words = text.split()
    words = [w for w in words if w not in STOPWORDS]
    return ' '.join(words)


# -------------------------------
# N-GRAMS (LESS STRICT)
# -------------------------------
def get_ngrams(text, n=4):   # reduced from 5/6
    words = preprocess(text).split()
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]


# -------------------------------
# RABIN-KARP (UNCHANGED CORE)
# -------------------------------
BASE = 31
MOD = (1 << 61) - 1

def rabin_hash(s):
    h = 0
    for ch in s:
        h = (h * BASE + ord(ch)) % MOD
    return h


# -------------------------------
# SHINGLING (MAJOR FIX 🔥)
# -------------------------------
def get_shingles(text, k=3):   # 🔥 from 5 → 3
    words = preprocess(text).split()
    shingles = set()

    for i in range(len(words) - k + 1):
        shingle = ' '.join(words[i:i+k])
        shingles.add(rabin_hash(shingle))

    return shingles


def jaccard(a, b):
    if not a or not b:
        return 0
    return len(a & b) / len(a | b)


def winnowing_score(doc, source):
    s1 = get_shingles(doc)
    s2 = get_shingles(source)

    return round(jaccard(s1, s2) * 100, 2)


# -------------------------------
# NGRAM SIMILARITY (FAST)
# -------------------------------
def ngram_score(doc, source):
    doc_ngrams = set(get_ngrams(doc))
    src_ngrams = set(get_ngrams(source))

    return round(jaccard(doc_ngrams, src_ngrams) * 100, 2)


# -------------------------------
# FINAL COMBINED SCORE
# -------------------------------
def combined_similarity(doc, source):
    w = winnowing_score(doc, source)
    n = ngram_score(doc, source)

    final = 0.6 * w + 0.4 * n

    return {
        "winnowing": w,
        "ngram": n,
        "combined": round(final, 2)
    }
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
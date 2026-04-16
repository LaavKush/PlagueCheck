# # ============================================================
# # ADSA Core Algorithms: String Matching for Plagiarism Detection
# # ============================================================

# import re
# import math
# from collections import defaultdict


# # ─────────────────────────────────────────────
# # 1. TEXT PREPROCESSING
# # ─────────────────────────────────────────────

# def preprocess(text: str) -> str:
#     """Lowercase and strip punctuation."""
#     text = text.lower()
#     text = re.sub(r'[^a-z0-9\s]', '', text)
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text


# def get_sentences(text: str) -> list[str]:
#     """Split text into sentences."""
#     sentences = re.split(r'(?<=[.!?])\s+', text.strip())
#     return [s.strip() for s in sentences if len(s.strip()) > 20]


# def get_ngrams(text: str, n: int = 5) -> list[str]:
#     """Generate word-level n-grams from text."""
#     words = preprocess(text).split()
#     return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]


# # ─────────────────────────────────────────────
# # 2. KMP (Knuth-Morris-Pratt) — Exact Matching
# # ─────────────────────────────────────────────

# def build_lps(pattern: str) -> list[int]:
#     """Build the Longest Proper Prefix which is also Suffix array."""
#     m = len(pattern)
#     lps = [0] * m
#     length = 0
#     i = 1
#     while i < m:
#         if pattern[i] == pattern[length]:
#             length += 1
#             lps[i] = length
#             i += 1
#         else:
#             if length != 0:
#                 length = lps[length - 1]
#             else:
#                 lps[i] = 0
#                 i += 1
#     return lps


# def kmp_search(text: str, pattern: str) -> list[int]:
#     """
#     KMP string search. Returns list of start indices where pattern occurs in text.
#     Time: O(n + m), Space: O(m)
#     """
#     n, m = len(text), len(pattern)
#     if m == 0:
#         return []
#     lps = build_lps(pattern)
#     matches = []
#     i = j = 0
#     while i < n:
#         if text[i] == pattern[j]:
#             i += 1
#             j += 1
#         if j == m:
#             matches.append(i - j)
#             j = lps[j - 1]
#         elif i < n and text[i] != pattern[j]:
#             if j != 0:
#                 j = lps[j - 1]
#             else:
#                 i += 1
#     return matches


# def kmp_exact_match_score(doc: str, source: str) -> dict:
#     """
#     Find exact sentence matches between doc and source using KMP.
#     Returns matched sentences and a score.
#     """
#     doc_sentences = get_sentences(doc)
#     source_clean = preprocess(source)
#     matched = []

#     for sentence in doc_sentences:
#         pattern = preprocess(sentence)
#         if len(pattern) < 15:
#             continue
#         occurrences = kmp_search(source_clean, pattern)
#         if occurrences:
#             matched.append(sentence)

#     score = len(matched) / max(len(doc_sentences), 1)
#     return {
#         "algorithm": "KMP (Exact Match)",
#         "matched_sentences": matched,
#         "score": round(score * 100, 2)
#     }


# # ─────────────────────────────────────────────
# # 3. RABIN-KARP — Rolling Hash Multi-pattern
# # ─────────────────────────────────────────────

# BASE = 31
# MOD = (1 << 61) - 1  # Mersenne prime


# def rabin_karp_hash(s: str) -> int:
#     h = 0
#     for ch in s:
#         h = (h * BASE + ord(ch)) % MOD
#     return h


# def rabin_karp_search(text: str, patterns: list[str]) -> dict[str, list[int]]:
#     """
#     Multi-pattern Rabin-Karp search.
#     Time: O(n + m*k) avg, where k = number of patterns
#     """
#     pattern_hashes = {}
#     for p in patterns:
#         h = rabin_karp_hash(p)
#         pattern_hashes.setdefault(h, []).append(p)

#     results = defaultdict(list)
#     n = len(text)

#     for p_len in set(len(p) for p in patterns):
#         if p_len > n:
#             continue
#         # Compute hash of first window
#         window_hash = rabin_karp_hash(text[:p_len])
#         power = pow(BASE, p_len - 1, MOD)

#         for i in range(n - p_len + 1):
#             if window_hash in pattern_hashes:
#                 window = text[i:i + p_len]
#                 for pat in pattern_hashes[window_hash]:
#                     if len(pat) == p_len and window == pat:
#                         results[pat].append(i)

#             if i + p_len < n:
#                 window_hash = (
#                     (window_hash - ord(text[i]) * power) * BASE + ord(text[i + p_len])
#                 ) % MOD

#     return dict(results)


# def rabin_karp_ngram_score(doc: str, source: str, n: int = 6) -> dict:
#     """
#     Score similarity using n-gram fingerprinting via Rabin-Karp.
#     """
#     doc_ngrams = get_ngrams(doc, n)
#     source_clean = preprocess(source)

#     if not doc_ngrams:
#         return {"algorithm": "Rabin-Karp (N-gram)", "matched_ngrams": [], "score": 0}

#     doc_ngrams_clean = [preprocess(ng) for ng in doc_ngrams]
#     matches = rabin_karp_search(source_clean, doc_ngrams_clean)

#     matched_ngrams = list(matches.keys())
#     score = len(matched_ngrams) / max(len(doc_ngrams_clean), 1)

#     return {
#         "algorithm": "Rabin-Karp (N-gram Fingerprint)",
#         "matched_ngrams": matched_ngrams[:10],  # top 10 for display
#         "score": round(score * 100, 2)
#     }


# # ─────────────────────────────────────────────
# # 4. WINNOWING / SHINGLING — Jaccard Similarity
# # ─────────────────────────────────────────────

# def get_shingles(text: str, k: int = 5) -> set[int]:
#     """
#     Generate k-shingles (hashed word k-grams).
#     Used for fuzzy/paraphrase detection.
#     """
#     words = preprocess(text).split()
#     shingles = set()
#     for i in range(len(words) - k + 1):
#         shingle = ' '.join(words[i:i+k])
#         shingles.add(rabin_karp_hash(shingle))
#     return shingles


# def jaccard_similarity(set_a: set, set_b: set) -> float:
#     if not set_a or not set_b:
#         return 0.0
#     intersection = len(set_a & set_b)
#     union = len(set_a | set_b)
#     return intersection / union if union else 0.0


# def winnowing_score(doc: str, source: str, k: int = 5) -> dict:
#     """
#     Compute Jaccard similarity via shingling/winnowing.
#     Good for paraphrase detection.
#     """
#     doc_shingles = get_shingles(doc, k)
#     source_shingles = get_shingles(source, k)
#     score = jaccard_similarity(doc_shingles, source_shingles)

#     return {
#         "algorithm": "Winnowing / Jaccard Shingling",
#         "doc_shingles": len(doc_shingles),
#         "source_shingles": len(source_shingles),
#         "common_shingles": len(doc_shingles & source_shingles),
#         "score": round(score * 100, 2)
#     }


# # ─────────────────────────────────────────────
# # 5. Z-ALGORITHM — for fast suffix comparison
# # ─────────────────────────────────────────────

# def z_function(s: str) -> list[int]:
#     """
#     Z-algorithm: z[i] = length of longest substring starting at s[i]
#     that is also a prefix of s. Time: O(n)
#     """
#     n = len(s)
#     z = [0] * n
#     z[0] = n
#     l, r = 0, 0
#     for i in range(1, n):
#         if i < r:
#             z[i] = min(r - i, z[i - l])
#         while i + z[i] < n and s[z[i]] == s[i + z[i]]:
#             z[i] += 1
#         if i + z[i] > r:
#             l, r = i, i + z[i]
#     return z


# def z_algorithm_score(doc: str, source: str) -> dict:
#     """
#     Use Z-algorithm to find longest common prefix segments.
#     """
#     doc_clean = preprocess(doc)
#     source_clean = preprocess(source)

#     combined = doc_clean + "$" + source_clean
#     z = z_function(combined)

#     doc_len = len(doc_clean)
#     long_matches = []

#     for i in range(doc_len + 1, len(combined)):
#         match_len = z[i]
#         if match_len >= 30:  # min 30 char match
#             matched_text = combined[i:i + match_len]
#             long_matches.append(matched_text)

#     # deduplicate
#     seen = set()
#     unique_matches = []
#     for m in long_matches:
#         if m not in seen:
#             seen.add(m)
#             unique_matches.append(m)

#     score = min(sum(len(m) for m in unique_matches) / max(len(doc_clean), 1), 1.0)

#     return {
#         "algorithm": "Z-Algorithm (Longest Common Segments)",
#         "long_matches": unique_matches[:5],
#         "score": round(score * 100, 2)
#     }


# # ─────────────────────────────────────────────
# # 6. COMBINED SCORE
# # ─────────────────────────────────────────────

# def combined_similarity(doc: str, source: str) -> dict:
#     """Run all algorithms and return weighted combined score."""
#     kmp = kmp_exact_match_score(doc, source)
#     rk = rabin_karp_ngram_score(doc, source)
#     win = winnowing_score(doc, source)
#     z = z_algorithm_score(doc, source)

#     # Weighted average: exact matches weighted higher
#     weights = {"kmp": 0.35, "rk": 0.30, "win": 0.20, "z": 0.15}
#     combined = (
#         kmp["score"] * weights["kmp"] +
#         rk["score"] * weights["rk"] +
#         win["score"] * weights["win"] +
#         z["score"] * weights["z"]
#     )

#     return {
#         "kmp": kmp,
#         "rabin_karp": rk,
#         "winnowing": win,
#         "z_algorithm": z,
#         "combined_score": round(combined, 2)
#     }

# ============================================================
# ADSA Core Algorithms: String Matching for Plagiarism Detection
# ============================================================

import re
import math
from collections import defaultdict


# ─────────────────────────────────────────────
# 1. TEXT PREPROCESSING
# ─────────────────────────────────────────────

def preprocess(text: str) -> str:
    """Lowercase and strip punctuation while preserving numbers for technical accuracy."""
    text = text.lower()
    # Updated regex to keep alphanumeric characters
    text = re.sub(r'[^a-z0-9\s]', '', text) 
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_sentences(text: str) -> list[str]:
    """Split text into sentences with lower threshold for technical content."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Reduced threshold from 20 to 10 to catch shorter technical definitions
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def get_ngrams(text: str, n: int = 5) -> list[str]:
    """Generate word-level n-grams from text."""
    words = preprocess(text).split()
    return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]


# ─────────────────────────────────────────────
# 2. KMP (Knuth-Morris-Pratt) — Exact Matching
# ─────────────────────────────────────────────

def build_lps(pattern: str) -> list[int]:
    """Build the Longest Proper Prefix which is also Suffix array."""
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> list[int]:
    """
    KMP string search. Returns list of start indices where pattern occurs in text.
    Time: O(n + m), Space: O(m)
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return []
    lps = build_lps(pattern)
    matches = []
    i = j = 0
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            matches.append(i - j)
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches


def kmp_exact_match_score(doc: str, source: str) -> dict:
    """
    Find exact sentence matches between doc and source using KMP.
    Returns matched sentences and a score.
    """
    doc_sentences = get_sentences(doc)
    source_clean = preprocess(source)
    matched = []

    for sentence in doc_sentences:
        pattern = preprocess(sentence)
        if len(pattern) < 10: # Lowered from 15
            continue
        occurrences = kmp_search(source_clean, pattern)
        if occurrences:
            matched.append(sentence)

    score = len(matched) / max(len(doc_sentences), 1)
    return {
        "algorithm": "KMP (Exact Match)",
        "matched_sentences": matched,
        "score": round(score * 100, 2)
    }


# ─────────────────────────────────────────────
# 3. RABIN-KARP — Rolling Hash Multi-pattern
# ─────────────────────────────────────────────

BASE = 31
MOD = (1 << 61) - 1  # Mersenne prime


def rabin_karp_hash(s: str) -> int:
    h = 0
    for ch in s:
        h = (h * BASE + ord(ch)) % MOD
    return h


def rabin_karp_search(text: str, patterns: list[str]) -> dict[str, list[int]]:
    """
    Multi-pattern Rabin-Karp search.
    Time: O(n + m*k) avg, where k = number of patterns
    """
    pattern_hashes = {}
    for p in patterns:
        h = rabin_karp_hash(p)
        pattern_hashes.setdefault(h, []).append(p)

    results = defaultdict(list)
    n = len(text)

    for p_len in set(len(p) for p in patterns):
        if p_len > n:
            continue
        # Compute hash of first window
        window_hash = rabin_karp_hash(text[:p_len])
        power = pow(BASE, p_len - 1, MOD)

        for i in range(n - p_len + 1):
            if window_hash in pattern_hashes:
                window = text[i:i + p_len]
                for pat in pattern_hashes[window_hash]:
                    if len(pat) == p_len and window == pat:
                        results[pat].append(i)

            if i + p_len < n:
                window_hash = (
                    (window_hash - ord(text[i]) * power) * BASE + ord(text[i + p_len])
                ) % MOD

    return dict(results)


def rabin_karp_ngram_score(doc: str, source: str, n: int = 6) -> dict:
    """
    Score similarity using n-gram fingerprinting via Rabin-Karp.
    """
    doc_ngrams = get_ngrams(doc, n)
    source_clean = preprocess(source)

    if not doc_ngrams:
        return {"algorithm": "Rabin-Karp (N-gram)", "matched_ngrams": [], "score": 0}

    doc_ngrams_clean = [preprocess(ng) for ng in doc_ngrams]
    matches = rabin_karp_search(source_clean, doc_ngrams_clean)

    matched_ngrams = list(matches.keys())
    score = len(matched_ngrams) / max(len(doc_ngrams_clean), 1)

    return {
        "algorithm": "Rabin-Karp (N-gram Fingerprint)",
        "matched_ngrams": matched_ngrams[:10],  # top 10 for display
        "score": round(score * 100, 2)
    }


# ─────────────────────────────────────────────
# 4. WINNOWING / SHINGLING — Jaccard Similarity
# ─────────────────────────────────────────────

def get_shingles(text: str, k: int = 5) -> set[int]:
    """
    Generate k-shingles (hashed word k-grams).
    Used for fuzzy/paraphrase detection.
    """
    words = preprocess(text).split()
    shingles = set()
    for i in range(len(words) - k + 1):
        shingle = ' '.join(words[i:i+k])
        shingles.add(rabin_karp_hash(shingle))
    return shingles


def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def winnowing_score(doc: str, source: str, k: int = 5) -> dict:
    """
    Compute Jaccard similarity via shingling/winnowing.
    Good for paraphrase detection.
    """
    doc_shingles = get_shingles(doc, k)
    source_shingles = get_shingles(source, k)
    score = jaccard_similarity(doc_shingles, source_shingles)

    return {
        "algorithm": "Winnowing / Jaccard Shingling",
        "doc_shingles": len(doc_shingles),
        "source_shingles": len(source_shingles),
        "common_shingles": len(doc_shingles & source_shingles),
        "score": round(score * 100, 2)
    }


# ─────────────────────────────────────────────
# 5. Z-ALGORITHM — for fast suffix comparison
# ─────────────────────────────────────────────

def z_function(s: str) -> list[int]:
    """
    Z-algorithm: z[i] = length of longest substring starting at s[i]
    that is also a prefix of s. Time: O(n)
    """
    n = len(s)
    z = [0] * n
    z[0] = n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def z_algorithm_score(doc: str, source: str) -> dict:
    """
    Use Z-algorithm to find longest common prefix segments.
    """
    doc_clean = preprocess(doc)
    source_clean = preprocess(source)

    combined = doc_clean + "$" + source_clean
    z = z_function(combined)

    doc_len = len(doc_clean)
    long_matches = []

    for i in range(doc_len + 1, len(combined)):
        match_len = z[i]
        if match_len >= 20:  # min 20 char match instead of 30
            matched_text = combined[i:i + match_len]
            long_matches.append(matched_text)

    # deduplicate
    seen = set()
    unique_matches = []
    for m in long_matches:
        if m not in seen:
            seen.add(m)
            unique_matches.append(m)

    score = min(sum(len(m) for m in unique_matches) / max(len(doc_clean), 1), 1.0)

    return {
        "algorithm": "Z-Algorithm (Longest Common Segments)",
        "long_matches": unique_matches[:5],
        "score": round(score * 100, 2)
    }


# ─────────────────────────────────────────────
# 6. COMBINED SCORE
# ─────────────────────────────────────────────

def combined_similarity(doc: str, source: str) -> dict:
    """Run all algorithms and return weighted combined score."""
    kmp = kmp_exact_match_score(doc, source)
    rk = rabin_karp_ngram_score(doc, source)
    win = winnowing_score(doc, source)
    z = z_algorithm_score(doc, source)

    # Weighted average: exact matches weighted higher
    weights = {"kmp": 0.35, "rk": 0.30, "win": 0.20, "z": 0.15}
    combined = (
        kmp["score"] * weights["kmp"] +
        rk["score"] * weights["rk"] +
        win["score"] * weights["win"] +
        z["score"] * weights["z"]
    )

    return {
        "kmp": kmp,
        "rabin_karp": rk,
        "winnowing": win,
        "z_algorithm": z,
        "combined_score": round(combined, 2)
    }
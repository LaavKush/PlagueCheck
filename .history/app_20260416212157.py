# # ============================================================
# # Flask API — Plagiarism Detection Server
# # ============================================================

# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# import os
# import sys

# sys.path.insert(0, os.path.dirname(__file__))

# from algorithms import combined_similarity
# from searcher import search_and_fetch_sources

# app = Flask(__name__, static_folder="../frontend")
# CORS(app)


# @app.route("/")
# def index():
#     return send_from_directory(app.static_folder, "index.html")


# @app.route("/api/check", methods=["POST"])
# def check_plagiarism():
#     """
#     POST /api/check
#     Body: { "document": "<text>" }
#     Returns: similarity results vs top web sources
#     """
#     data = request.get_json()
#     if not data or "document" not in data:
#         return jsonify({"error": "Missing 'document' field"}), 400

#     document = data["document"].strip()
#     if len(document) < 50:
#         return jsonify({"error": "Document too short (min 50 characters)"}), 400

#     # Step 1: Search web for similar content
#     sources = search_and_fetch_sources(document, max_sources=4)

#     if not sources:
#         return jsonify({
#             "document_length": len(document),
#             "sources_checked": 0,
#             "results": [],
#             "overall_verdict": "clean",
#             "max_score": 0
#         })

#     # Step 2: Run all algorithms against each source
#     results = []
#     for source in sources:
#         similarity = combined_similarity(document, source["content"])
#         results.append({
#             "source": {
#                 "title": source["title"],
#                 "url": source["url"],
#                 "snippet": source["snippet"]
#             },
#             "analysis": similarity
#         })

#     # Step 3: Determine verdict
#     max_score = max(r["analysis"]["combined_score"] for r in results)
#     if max_score >= 60:
#         verdict = "high"
#     elif max_score >= 30:
#         verdict = "moderate"
#     elif max_score >= 10:
#         verdict = "low"
#     else:
#         verdict = "clean"

#     return jsonify({
#         "document_length": len(document),
#         "sources_checked": len(results),
#         "results": results,
#         "overall_verdict": verdict,
#         "max_score": round(max_score, 2)
#     })


# @app.route("/api/health")
# def health():
#     return jsonify({"status": "ok"})


# if __name__ == "__main__":
#     print("🔍 Plagiarism Detector running at http://localhost:5000")
#     app.run(debug=True, port=5000)

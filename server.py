from flask import Flask, request, jsonify, redirect
import requests
import threading
import asyncio
import os
from dotenv import load_dotenv
from sentiment import analyze_sentiment
from actions import delete_comment, like_comment
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Lade Umgebungsvariablen
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour", "10 per minute"])
comments_db = {}

# 📌 Automatische Weiterleitung von HTTP zu HTTPS
@app.before_request
def enforce_https():
    if request.headers.get("X-Forwarded-Proto") == "http":
        return redirect(request.url.replace("http://", "https://"), code=301)

# 📌 API-Key-Authentifizierung
@app.before_request
def authenticate():
    if request.endpoint not in ["static"]:
        api_key = request.headers.get("X-API-KEY")
        if api_key != API_SECRET_KEY:
            return jsonify({"error": "Ungültiger API-Schlüssel"}), 403

# 📌 1️⃣ Endpunkt: Kommentare empfangen & analysieren
@app.route('/api/comments', methods=['POST'])
@limiter.limit("5 per minute")  # Begrenzung pro Nutzer
def receive_comment():
    data = request.get_json()
    comment_id = data.get("comment_id")
    comment_text = data.get("comment_text", "").strip()
    username = data.get("username", "")
    post_id = data.get("post_id", "")
    
    if not comment_text:
        return jsonify({"error": "Kein Kommentar erhalten"}), 400

    # Google Sentiment-Analyse
    sentiment = analyze_sentiment(comment_text)
    comments_db[comment_id] = {"text": comment_text, "sentiment": sentiment}

    if sentiment == "negativ":
        delete_comment(comment_id)
        return jsonify({"status": "deleted", "comment": comment_text, "reason": "negativ"}), 200
    
    # Falls positiv/neutral, mit Verzögerung liken
    asyncio.run(schedule_like(comment_id))
    return jsonify({"status": "received", "comment": comment_text, "sentiment": sentiment}), 200

# 📌 2️⃣ Liken mit Verzögerung (Asynchron)
async def schedule_like(comment_id):
    await asyncio.sleep(10)  # 10 Sekunden Verzögerung
    like_comment(comment_id)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

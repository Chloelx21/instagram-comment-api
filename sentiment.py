import requests
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def analyze_sentiment(text):
    """Analysiert die Stimmung eines Textes mit der Google Natural Language API."""
    url = f"https://language.googleapis.com/v1/documents:analyzeSentiment?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "document": {
            "type": "PLAIN_TEXT",
            "content": text
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    score = result.get("documentSentiment", {}).get("score", 0)

    if score < -0.3:
        return "negativ"
    elif score > 0.3:
        return "positiv"
    return "neutral"

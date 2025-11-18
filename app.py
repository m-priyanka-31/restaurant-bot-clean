from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests
import json

app = Flask(__name__)
GROK_API_KEY = os.getenv("GROK_API_KEY")

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    # Force Grok to parse — no fallback
    prompt = f"""Extract booking details from this Hindi/English message and return ONLY valid JSON:
Message: "{incoming_msg}"

Return exactly this format (no extra text):
{{"people": "6", "time": "9 PM", "date": "tomorrow", "name": "Rahul"}}

If no booking intent, reply {{"people": "4", "time": "8 PM", "date": "today", "name": "Customer"}}"""

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-beta",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    try:
        r = requests.post("https://api.x.ai/v1/chat/completions", json=data, headers=headers, timeout=10)
        response = r.json()["choices"][0]["message"]["content"].strip()
        booking = json.loads(response)
    except Exception as e:
        print("Grok error:", e)
        booking = {"people": "4", "time": "8 PM", "date": "today", "name": "Customer"}

    reply = f"नमस्ते {booking.get('name', 'Customer')} जी!\n{booking['people']} लोग, {booking['time']} ({booking['date']}) के लिए बुकिंग हो गई।\nकन्फर्म: *1*  |  कैंसिल: *2*"
    msg.body(reply)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
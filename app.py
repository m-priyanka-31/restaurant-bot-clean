from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests
import json

app = Flask(__name__)

GROK_API_KEY = os.getenv("GROK_API_KEY")

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', 'unknown')
    resp = MessagingResponse()
    msg = resp.message()

    # Use Grok to parse the message
    if GROK_API_KEY:
        prompt = f"Extract booking from this message: '{incoming_msg}'\nReturn ONLY JSON: {{'people': '4', 'time': '8 PM', 'date': 'tomorrow'}}"
        headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "grok-beta", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        try:
            r = requests.post("https://api.x.ai/v1/chat/completions", json=data, headers=headers)
            response = r.json()["choices"][0]["message"]["content"]
            booking = json.loads(response)
        except:
            booking = {'people': '4', 'time': '8 PM', 'date': 'tomorrow'}  # Fallback
    else:
        booking = {'people': '4', 'time': '8 PM', 'date': 'tomorrow'}  # Fallback if no key

    # Dynamic reply based on parsed data
    reply = f"नमस्ते! {booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।\nकन्फर्म: *1*, कैंसिल: *2*"
    msg.body(reply)

    print(f"Parsed booking from {from_number}: {booking}")

    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re

app = Flask(__name__)

def extract_booking(text):
    text = text.lower()
    people = re.search(r'(\d+)\s*(people|person|log|pax|लोग)', text)
    time = re.search(r'(\d{1,2}(:\d{2})?\s*(am|pm|बजे))', text)
    date = re.search(r'(today|tomorrow|कल|आज|\d{1,2}[/-]\d{1,2})', text)

    p = people.group(1) if people else "4"
    t = time.group(1) if time else "8 PM"
    d = date.group(1) if date else "today"

    return {"people": p, "time": t, "date": d}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    booking = extract_booking(incoming)

    reply = f"नमस्ते!\n{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।\nकन्फर्म: *1*  |  कैंसिल: *2*"
    msg.body(reply)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
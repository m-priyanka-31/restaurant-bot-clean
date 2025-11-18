from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re

app = Flask(__name__)

def extract_booking(text):
    text = text.lower() + " "  # add space to catch end of string

    # Super strong regex — works for ALL these:
    # Table for 8, 8 people, 8 लोग, 8 log, 8 pax, for 8, 8 at, etc.
    people = re.search(r'(?:for|table for|book|\b)(\d{1,3})\s*(?:people|person|pax|लोग|log|लोगों)?', text)
    time = re.search(r'at\s+(\d{1,2}(?::\d{2})?\s*(?:pm|am|बजे)?)|(\d{1,2}\s*(?:pm|am|बजे))', text)

    p = people.group(1) if people else "4"
    t = time.group(1) or time.group(2) if time else "8 PM"
    t = t.strip().capitalize()

    return {"people": p, "time": t}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    booking = extract_booking(incoming)

    reply = f"<p>नमस्ते!</p>" \
            f"<p>{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।</p>" \
            f"<p>कन्फर्म करने के लिए <b>1</b> दबाएँ</p>" \
            f"<p>कैंसिल करने के लिए <b>2</b> दबाएँ</p>"

    msg.body(reply)
    print(f"Parsed → {booking['people']} लोग at {booking['time']}")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
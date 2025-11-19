from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re

app = Flask(__name__)

def extract_booking(text):
    text = text.lower() + " "
    people = re.search(r'(?:for|table for|book|\b)(\d{1,3})\s*(?:people|person|pax|लोग|log)?', text)
    time = re.search(r'at\s+(\d{1,2}(?::\d{2})?\s*(?:pm|am|बजे)?)|(\d{1,2}\s*(?:pm|am|बजे))', text)
    p = people.group(1) if people else "4"
    t = time.group(1) or time.group(2) if time else "8 PM"
    t = t.strip().title()
    return {"people": p, "time": t}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    booking = extract_booking(incoming)

    reply = f"<p>नमस्ते!</p><p>{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।</p><p>कन्फर्म: *1* | कैंसिल: *2*</p>"
    msg.body(reply)

    print(f"Booking → {booking['people']} लोग, {booking['time']}")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
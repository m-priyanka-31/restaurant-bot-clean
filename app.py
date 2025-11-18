from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re

app = Flask(__name__)

def extract_booking(text):
    text = text.lower()

    # Improved regex — captures both English & Hindi numbers
    people_match = re.search(r'(\d+)\s*(?:people|person|pax|लोग|log|लोगों)', text)
    time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|बजे|o\'?clock))', text)
    date_match = re.search(r'(today|tomorrow|कल|आज|tonight|आज रात)', text)

    people = people_match.group(1) if people_match else "4"
    time = time_match.group(1) if time_match else "8 PM"
    date = date_match.group(1) if date_match else "today"

    return {"people": people, "time": time.capitalize(), "date": date}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    booking = extract_booking(incoming)

    # Clean formatted reply with line breaks
    reply = f"<p>नमस्ते!</p>" \
            f"<p>{booking['people']} लोग, {booking['time']} ({booking['date']}) के लिए बुकिंग हो गई।</p>" \
            f"<p>कन्फर्म करने के लिए <b>1</b> दबाएँ</p>" \
            f"<p>कैंसिल करने के लिए <b>2</b> दबाएँ</p>"

    msg.body(reply)
    print(f"Booking: {booking['people']} people at {booking['time']} on {booking['date']}")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
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
    incoming = request.values.get('Body', '').strip().lower()
    profile_name = request.values.get('ProfileName', 'Customer')
    resp = MessagingResponse()
    msg = resp.message()

    # If user replies "1" → Confirm
    if incoming == "1":
        msg.body(f"✅ धन्यवाद {profile_name} जी!\nआपकी बुकिंग कन्फर्म हो गई।\nहम आपकी टेबल तैयार रखेंगे!")
    
    # If user replies "2" → Cancel
    elif incoming == "2":
        msg.body(f"❌ ठीक है {profile_name} जी,\nबुकिंग कैंसिल कर दी गई।\nफिर कभी आएँ!")
    
    # New booking
    else:
        booking = extract_booking(incoming)
        reply = f"<p>नमस्ते {profile_name} जी!</p>" \
                f"<p>{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।</p>" \
                f"<p>कन्फर्म करने के लिए <b>1</b> दबाएँ</p>" \
                f"<p>कैंसिल करने के लिए <b>2</b> दबाएँए</p>"
        msg.body(reply)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
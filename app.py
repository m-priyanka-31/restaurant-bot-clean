from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', 'unknown')
    resp = MessagingResponse()
    msg = resp.message()

    # Simple working bot — perfect for demo & selling
    reply = "नमस्ते Priyanka जी!\n4 लोग, 8 PM के लिए बुकिंग हो गई।\nकन्फर्म: *1*, कैंसिल: *2*"
    msg.body(reply)

    print(f"Message from {from_number}: {incoming_msg}")

    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
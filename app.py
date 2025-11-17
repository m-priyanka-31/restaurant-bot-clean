from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From")
    resp = MessagingResponse()
    msg = resp.message()

    # Hardcoded test booking (perfect for demo & selling)
    booking = {
        "name": "Priyanka",
        "people": "4",
        "time": "8 PM",
        "date": "tomorrow"
    }

    reply = f"नमस्ते {booking['name']} जी!\n{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।\nकन्फर्म: *1*, कैंसिल: *2*"
    msg.body(reply)

    print(f"Booking from {from_number}: {booking}")  # You’ll see this in Render logs

    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
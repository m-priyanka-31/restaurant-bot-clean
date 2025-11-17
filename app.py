from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Load Google Sheet only when first message comes (no creds.json file needed)
sheet = None
def get_sheet():
    global sheet
    if sheet is None:
        try:
            creds_json = os.getenv("GOOGLE_CREDS_JSON")
            if not creds_json:
                print("No Google creds in env - running without sheet")
                return None
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                creds_dict,
                ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            )
            client = gspread.authorize(creds)
            sheet = client.open("RestaurantBookings").sheet1
            print("Google Sheet connected!")
        except Exception as e:
            print("Sheet error:", e)
            sheet = None
    return sheet

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From")
    resp = MessagingResponse()
    msg = resp.message()

    # Hardcoded test booking
    booking = {
        "name": "Priyanka",
        "people": "4",
        "time": "8 PM",
        "date": "tomorrow"
    }

    # Try to save to Google Sheet
    sh = get_sheet()
    if sh:
        try:
            sh.append_row([booking["name"], booking["people"], booking["time"], booking["date"], from_number, "PENDING"])
            print("Row added to sheet")
        except Exception as e:
            print("Failed to write to sheet:", e)

    reply = f"नमस्ते {booking['name']} जी!\n{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।\nकन्फर्म: *1*, कैंसिल: *2*"
    msg.body(reply)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
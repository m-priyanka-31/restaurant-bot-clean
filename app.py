from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

# === LOAD ENV ===
load_dotenv()

# === FLASK APP ===
app = Flask(__name__)

# === GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("RestaurantBookings").sheet1

# === WHATSAPP ROUTE (BYPASS MODE) ===
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From", "unknown")
    resp = MessagingResponse()
    msg = resp.message()

    # === HARDCODED BOOKING ===
    name = "Priyanka"
    people = "4"
    time = "8 PM"
    date = "tomorrow"

    # === ADD TO SHEET ===
    try:
        sheet.append_row([name, people, time, date, from_number, "PENDING"])
        print("ROW ADDED TO SHEET!")
    except Exception as e:
        print("SHEET ERROR:", e)

    # === SEND REPLY ===
    reply = f"नमस्ते {name} जी!\n{people} लोग, {time} के लिए बुकिंग हो गई।\nकन्फर्म: *1*, कैंसिल: *2*"
    msg.body(reply)

    return str(resp)

# === RUN SERVER ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Lazy Google Sheet – only loads when needed
sheet = None
def get_sheet():
    global sheet
    if sheet is None:
        creds_json = os.getenv("GOOGLE_CREDS_JSON")
        if not creds_json:
            print("No GOOGLE_CREDS_JSON → Sheet disabled")
            return None
        try:
            creds_dict = json.loads(creds_json)
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("RestaurantBookings").sheet1   # ← change name if yours is different
            print("Google Sheet connected successfully!")
        except Exception as e:
            print("Sheet connection failed:", e)
            sheet = None
    return sheet

def extract_booking(text):
    text = text.lower() + " "
    people = re.search(r'(?:for|table for|book|\b)(\d{1,3})\s*(?:people|person|pax|लोग|log|लोगों)?', text)
    time = re.search(r'at\s+(\d{1,2}(?::\d{2})?\s*(?:pm|am|बजे)?)|(\d{1,2}\s*(?:pm|am|बजे))', text)
    p = people.group(1) if people else "4"
    t = time.group(1) or time.group(2) if time else "8 PM"
    t = t.strip().capitalize()
    return {"people": p, "time": t}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming = request.values.get('Body', '').strip()
    from_number = request.values.get('From', 'unknown')
    resp = MessagingResponse()
    msg = resp.message()

    booking = extract_booking(incoming)

    reply = f"<p>नमस्ते!</p>" \
            f"<p>{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।</p>" \
            f"<p>कन्फर्म → <b>1</b>   |   कैंसिल → <b>2</b></p>"
    msg.body(reply)

    # Save to Google Sheet if available
    sh = get_sheet()
    if sh:
        try:
            sh.append_row([booking["people"], booking["time"], "", from_number.split(':')[1], "PENDING"])
            print("Row added to Google Sheet!")
        except Exception as e:
            print("Failed to write row:", e)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
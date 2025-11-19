from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Lazy Sheet — only loads when first booking comes
sheet = None
def get_sheet():
    global sheet
    if sheet is None:
        creds_json = os.getenv("GOOGLE_CREDS_JSON")
        if not creds_json:
            print("No creds → Sheet disabled")
            return None
        try:
            creds_dict = json.loads(creds_json)
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("RestaurantBookings").sheet1   # ← change name if yours is different
            print("Google Sheet connected!")
        except Exception as e:
            print("Sheet failed:", e)
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

    reply = f"<p>नमस्ते!</p><p>{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।</p><p>कन्फर्म: *1* | कैंसिल: *2*</p>"
    msg.body(reply)

    # SAVE TO SHEET
    sh = get_sheet()
    if sh:
        try:
            phone = from_number.split(':')[1] if ':' in from_number else from_number
            sh.append_row([booking["people"], booking["time"], "", phone, "PENDING"])
            print("Row added to Sheet!")
        except Exception as e:
            print("Write failed:", e)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
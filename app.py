from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Lazy load Sheet — no startup crash
sheet = None
def get_sheet():
    global sheet
    if sheet is None:
        try:
            creds_json = os.getenv("GOOGLE_CREDS_JSON")
            if not creds_json:
                print("No GOOGLE_CREDS_JSON — skipping Sheet")
                return None
            creds_dict = json.loads(creds_json)
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("RestaurantBookings").sheet1
            print("Sheet loaded!")
        except Exception as e:
            print(f"Sheet error: {e}")
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

    # Formatted reply with line breaks
    reply = f"<p>नमस्ते!</p><p>{booking['people']} लोग, {booking['time']} के लिए बुकिंग हो गई।</p><p>कन्फर्म: *1* | कैंसिल: *2*</p>"
    msg.body(reply)

    # Save to Sheet if available
    sh = get_sheet()
    if sh:
        try:
            sh.append_row([booking["people"], booking["time"], "", from_number.split(':')[1], "PENDING"])
            print("Row added!")
        except Exception as e:
            print(f"Row error: {e}")

    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- Google Sheets setup ---
SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1BOGgBAEW2yvE4Cm9lCtASe_H7RD76GBPcVtRWWJ1nf0"

# Create credentials object
scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

# Authorize client
client = gspread.authorize(creds)
sheet = client.open_by_url(SPREADSHEET_URL).sheet1  # Open first sheet

# --- Example: append a row ---
data_to_append = ["Expiry", "123456", "Item Name", 5, 10.0, 15.0, 50.0, "01-Jan-25", "Supplier", "Remarks", "Outlet"]

try:
    sheet.append_row(data_to_append)
    print("✅ Row added successfully!")
except Exception as e:
    print("❌ Error submitting to Google Sheet:", e)

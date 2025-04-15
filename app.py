import streamlit as st
import datetime
import gspread
import json
import pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets auth setup using Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds_json = json.dumps(dict(creds_dict))
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
client = gspread.authorize(creds)

# Google Sheet and Tabs
sheet = client.open("Production_Tracking")
uid_list_ws = sheet.worksheet("UID_List")
log_ws = sheet.worksheet("Production_Log")

# App layout
st.set_page_config(page_title="Production Tracker", layout="centered")
st.title("📦 Production Tracker App")

# Worker login
worker_name = st.text_input("Enter Your Name")

if worker_name:
    # Fetch UID list
    uids = uid_list_ws.col_values(1)[1:]  # Skip header
    uid_selected = st.selectbox("Select UID", uids)

    # Stage selection
    stages = ["Cutting", "Stitching", "Handwork", "Embroidery", "Interlock", "Buttoning", "Ironing"]
    stage_selected = st.selectbox("Select Your Stage", stages)

    # Status update
    status = st.radio("Update Status", ["Started", "Done"])

    # Optional comments
    comment = st.text_area("Any Comments (Optional)")

# Get timezone from secrets
timezone = st.secrets["timezone"]["zone"]

# Set timezone
tz = pytz.timezone(timezone)
now = datetime.now(tz)

st.write("Current IST Time:", now.strftime("%Y-%m-%d %H:%M:%S"))

    # Submit button
 if st.button("Submit Update"):
        india = pytz.timezone("Asia/Kolkata")
        now = datetime.now(india)
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
       
        all_records = log_ws.get_all_records()
        updated = False

        for idx, row in enumerate(all_records):
            if (
                row["UID"] == uid_selected
                and row["Stage"] == stage_selected
                and row["Worker Name"] == worker_name
            ):
                # If same row exists and End Time is empty, update it
                if row["End Time"] == "":
                    cell_row = idx + 2  # +2 because get_all_records skips header and gspread is 1-indexed
                    log_ws.update_cell(cell_row, 5, timestamp)  # Column E = End Time
                    if comment:
                        log_ws.update_cell(cell_row, 6, comment)  # Column F = Comments
                    st.success("✅ End Time updated successfully!")
                    updated = True
                    break

        if not updated and status == "Started":
            # Append new row if not found and status is Started
            log_ws.append_row([uid_selected, stage_selected, worker_name, timestamp, "", comment])
            st.success("✅ New record added successfully!")
        elif not updated and status == "Done":
            st.warning("⚠️ No matching 'Started' record found for update.")

    

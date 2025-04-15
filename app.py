import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets auth setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# --- Open Sheet and Tabs ---
sheet = client.open("Production_Tracking")
uid_list_ws = sheet.worksheet("UID_List")
log_ws = sheet.worksheet("Production_Log")

# --- Streamlit UI ---
st.set_page_config(page_title="Production Tracker", layout="centered")
st.title("📦 Production Tracker App")

# Worker login
worker_name = st.text_input("Enter Your Name")

if worker_name:
    # UID select
    uids = uid_list_ws.col_values(1)[1:]  # skip header
    uid_selected = st.selectbox("Select UID", uids)

    # Stage select
    stages = ["Cutting", "Stitching", "Handwork", "Embroidery", "Interlock", "Buttoning", "Ironing"]
    stage_selected = st.selectbox("Select Your Stage", stages)

    # Status
    status = st.radio("Update Status", ["Started", "Done"])

    # Optional comment
    comment = st.text_area("Any Comments (Optional)")

    # Submit
    if st.button("Submit Update"):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        all_records = log_ws.get_all_records()
        updated = False

        for idx, row in enumerate(all_records):
            if (
                row["UID"] == uid_selected and
                row["Stage"] == stage_selected and
                row["Worker Name"] == worker_name
            ):
                if row["End Time"] == "":
                    cell_row = idx + 2  # +2 because of header and 1-indexed
                    log_ws.update_cell(cell_row, 5, timestamp)  # End Time
                    if comment:
                        log_ws.update_cell(cell_row, 6, comment)  # Comments
                    st.success("✅ End Time updated successfully!")
                    updated = True
                    break

        if not updated and status == "Started":
            log_ws.append_row([uid_selected, stage_selected, worker_name, timestamp, "", comment])
            st.success("✅ New record added successfully!")
        elif not updated and status == "Done":
            st.warning("⚠️ No matching 'Started' record found for update.")

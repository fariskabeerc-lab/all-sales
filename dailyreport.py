import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet Form Dashboard", layout="wide")

# ==========================================
# LOAD ITEM DATA
# ==========================================
@st.cache_data
def load_item_data():
    df = pd.read_excel("alllist.xlsx")  # Your Excel file
    df.columns = df.columns.str.strip()
    return df

item_data = load_item_data()

# ==========================================
# GOOGLE SHEET SETUP
# ==========================================
SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1BOGgBAEW2yvE4Cm9lCtASe_H7RD76GBPcVtRWWJ1nf0"

scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_url(SPREADSHEET_URL).sheet1

# ==========================================
# LOGIN SYSTEM
# ==========================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida", "Hadeqat",
    "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan", "Superstore",
    "Tay Tay", "Safa oudmehta", "Port saeed"
]
password = "123123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "selected_outlet" not in st.session_state:
    st.session_state.selected_outlet = None
if "submitted_items" not in st.session_state:
    st.session_state.submitted_items = []

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 Outlet Login")
    username = st.text_input("Username", placeholder="Enter username")
    outlet = st.selectbox("Select your outlet", outlets)
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "almadina" and pwd == password:
            st.session_state.logged_in = True
            st.session_state.selected_outlet = outlet
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ==========================================
# MAIN DASHBOARD
# ==========================================
else:
    outlet_name = st.session_state.selected_outlet
    st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)

    # =================================================
    # Disable Enter key submission globally
    # =================================================
    st.markdown("""
        <script>
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && event.target.tagName === 'INPUT') {
                event.preventDefault();
                return false;
            }
        });
        </script>
    """, unsafe_allow_html=True)

    # ==========================================
    # FORM TYPE
    # ==========================================
    form_type = st.sidebar.radio(
        "📋 Select Form Type",
        ["Expiry", "Damages", "Near Expiry"],
        horizontal=False,
        key="form_selector"
    )

    st.markdown("---")

    # ==========================================
    # FORM UI
    # ==========================================
    with st.form(f"{form_type}_form", clear_on_submit=False):
        st.subheader(f"{form_type} Form")

        col1, col2, col3 = st.columns(3)
        with col1:
            barcode = st.text_input("Barcode")
        with col2:
            qty = st.number_input("Qty [PCS]", min_value=1, value=1)
        with col3:
            expiry = None
            if form_type != "Damages":
                expiry = st.date_input("Expiry Date", datetime.now())

        # ------------------------------------------
        # Auto-fill from Excel
        # ------------------------------------------
        item_name, cost, selling, supplier = "", 0.0, 0.0, ""
        if barcode:
            match = item_data[item_data["Item Bar Code"].astype(str) == str(barcode)]
            if not match.empty:
                item_name = str(match.iloc[0]["Item Name"])
                cost = float(match.iloc[0]["Cost"])
                selling = float(match.iloc[0]["Selling"])
                supplier = str(match.iloc[0]["LP Supplier"])

        col4, col5, col6, col7 = st.columns(4)
        with col4:
            item_name = st.text_input("Item Name", value=item_name)
        with col5:
            st.text(f"Cost: {cost}")
        with col6:
            st.text(f"Selling Price: {selling}")
        with col7:
            supplier = st.text_input("Supplier Name", value=supplier)

        gp = ((selling - cost)/cost)*100 if cost > 0 else 0
        st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

        remarks = st.text_area("Remarks [if any]")

        # ------------------------------------------
        # ADD TO LIST BUTTON
        # ------------------------------------------
        add_to_list = st.form_submit_button("➕ Add to List")
        if add_to_list:
            if barcode and item_name:
                st.session_state.submitted_items.append({
                    "Form Type": form_type,
                    "Barcode": barcode,
                    "Item Name": item_name,
                    "Qty": qty,
                    "Cost": cost,
                    "Selling": selling,
                    "Amount": cost * qty,
                    "GP%": round(gp,2),
                    "Expiry": expiry.strftime("%d-%b-%y") if expiry else "",
                    "Supplier": supplier,
                    "Remarks": remarks,
                    "Outlet": outlet_name
                })
                st.success("✅ Added to list successfully!")
                # Clear form
                st.experimental_rerun()
            else:
                st.warning("⚠️ Please fill required fields before adding.")

    # ==========================================
    # DISPLAY SUBMITTED ITEMS
    # ==========================================
    if st.session_state.submitted_items:
        st.markdown("### 🧾 Items Added")
        df = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df, use_container_width=True)

        colA, colB = st.columns([1,1])
        with colA:
            if st.button("🧹 Clear List"):
                st.session_state.submitted_items = []
                st.rerun()
        with colB:
            if st.button("📤 Submit All to Google Sheet"):
                try:
                    for row in st.session_state.submitted_items:
                        sheet.append_row(list(row.values()))
                    st.success("✅ All data submitted to Google Sheet")
                    st.session_state.submitted_items = []
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error submitting to Google Sheet: {e}")

    # ==========================================
    # LOGOUT
    # ==========================================
    st.sidebar.button("🚪 Logout", on_click=lambda: [
        st.session_state.update({"logged_in": False, "selected_outlet": None, "submitted_items": []}),
        st.rerun()
    ])

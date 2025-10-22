import streamlit as st
import pandas as pd
from datetime import date

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Outlet Product Dashboard", layout="wide")

# ==============================
# OUTLET LOGIN
# ==============================
users = {
    "safa": "123123",
    "fida": "12341234",
    "Outlet3": "pass3",
    "Outlet4": "pass4",
    "Outlet5": "pass5",
    "Outlet6": "pass6",
    "Outlet7": "pass7",
    "Outlet8": "pass8",
    "Outlet9": "pass9",
    "Outlet10": "pass10",
    "Outlet11": "pass11",
    "Outlet12": "pass12",
    "Outlet13": "pass13",
    "Outlet14": "pass14",
    "Outlet15": "pass15",
    "Outlet16": "pass16",
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Outlet Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.session_state.user = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password")
else:
    st.title(f"🏬 Dashboard - {st.session_state.user}")

    # ==============================
    # Sidebar - Form Selection
    # ==============================
    form_type = st.sidebar.selectbox("Select Form Type", ["Near Expiry", "Damaged", "Other"])

    # Initialize submitted_data if not exists
    if "submitted_data" not in st.session_state:
        st.session_state.submitted_data = []

    # ==============================
    # Form with auto-clear
    # ==============================
    st.subheader(f"📋 {form_type} Form")

    with st.form("product_form", clear_on_submit=True):
        barcode = st.text_input("Barcode")
        product_name = st.text_input("Product Name")
        qty = st.number_input("Qty [PCS]", min_value=0)
        cost = st.number_input("Cost", min_value=0.0, format="%.2f")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        expiry = st.date_input("Expiry Date", value=date.today())
        supplier = st.text_input("Supplier Name")
        remarks = st.text_area("Remarks [if any]")

        submitted = st.form_submit_button("Add Entry")
        if submitted:
            st.success("✅ Entry added!")
            # Add entry to session state for demo
            st.session_state.submitted_data.append({
                "Outlet": st.session_state.user,
                "Form Type": form_type,
                "Barcode": barcode,
                "Product Name": product_name,
                "Qty": qty,
                "Cost": cost,
                "Amount": amount,
                "Expiry Date": expiry,
                "Supplier": supplier,
                "Remarks": remarks
            })

    # ==============================
    # Show Table of All Entries
    # ==============================
    st.subheader("📊 All Entries (Before GitHub Submission)")

    if st.session_state.submitted_data:
        df = pd.DataFrame(st.session_state.submitted_data)
        st.dataframe(df)

        # Demo GitHub submission button
        if st.button("Submit All to GitHub (Demo)"):
            # In a real app, here you would push df to GitHub
            st.success(f"✅ {len(st.session_state.submitted_data)} entries submitted to GitHub (Demo)!")
            # Clear all entries after submission
            st.session_state.submitted_data = []
    else:
        st.info("No entries added yet.")

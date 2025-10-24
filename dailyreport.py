import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================
# Page Config
# ==============================
st.set_page_config(page_title="Outlet Form Dashboard", layout="wide")

# ==============================
# Load Excel Data (for auto-fill)
# ==============================
@st.cache_data
def load_item_data():
    file_path = "your_excel_file.xlsx"  # 👈 put your Excel file path here
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # clean column names
    return df

item_data = load_item_data()

# ==============================
# Outlet Login Setup
# ==============================
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
            st.error("Invalid username or password")

else:
    # ==============================
    # Main Dashboard
    # ==============================
    outlet_name = st.session_state.selected_outlet
    st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)

    # Full Screen Toggle
    full_screen = st.sidebar.toggle("🖥️ Full Screen Mode")

    if full_screen:
        hide_css = """
        <style>
        [data-testid="stAppViewContainer"] {padding:0; margin:0;}
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {display:none;}
        html, body, .block-container {height:100%; width:100%; margin:0; padding:0;}
        </style>
        """
        st.markdown(hide_css, unsafe_allow_html=True)
    else:
        show_css = """
        <style>
        [data-testid="stAppViewContainer"] {padding:1rem;}
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {display:block;}
        </style>
        """
        st.markdown(show_css, unsafe_allow_html=True)

    # ==============================
    # Form Selection (on the left)
    # ==============================
    form_type = st.radio(
        "📋 Select Form Type",
        ["Expiry", "Damages", "Near Expiry"],
        horizontal=False,
        key="form_selector"
    )

    st.markdown("---")

    # Initialize submission list
    if "submitted_items" not in st.session_state:
        st.session_state.submitted_items = []

    # ==============================
    # Form UI
    # ==============================
    with st.form(f"{form_type}_form"):
        st.subheader(f"{form_type} Form")

        col1, col2, col3 = st.columns(3)
        with col1:
            barcode = st.text_input("Barcode")
        with col2:
            qty = st.number_input("Qty [PCS]", min_value=1, value=1)
        with col3:
            expiry = st.date_input("Expiry Date", datetime.now())

        # Auto-fill based on barcode
        item_name = ""
        cost = ""
        selling = ""
        supplier = ""

        if barcode:
            match = item_data[item_data["Item Bar Code"].astype(str) == str(barcode)]
            if not match.empty:
                item_name = match.iloc[0]["Item Name"]
                cost = match.iloc[0]["Cost"]
                selling = match.iloc[0]["Selling"]
                supplier = match.iloc[0]["LP Supplier"]

        col4, col5, col6, col7 = st.columns(4)
        with col4:
            item_name = st.text_input("Item Name", value=item_name)
        with col5:
            cost = st.number_input("Cost", value=float(cost) if cost != "" else 0.0)
        with col6:
            selling = st.number_input("Selling Price", value=float(selling) if selling != "" else 0.0)
        with col7:
            supplier = st.text_input("Supplier Name", value=supplier)

        remarks = st.text_area("Remarks [if any]")

        submitted = st.form_submit_button("➕ Add to List")

        if submitted:
            st.session_state.submitted_items.append({
                "Form Type": form_type,
                "Barcode": barcode,
                "Item Name": item_name,
                "Qty": qty,
                "Cost": cost,
                "Selling": selling,
                "Amount": cost * qty,
                "Expiry": expiry.strftime("%d-%b-%y"),
                "Supplier": supplier,
                "Remarks": remarks,
                "Outlet": outlet_name
            })
            st.success("✅ Added to list successfully!")
            st.rerun()

    # ==============================
    # Display Submitted Items
    # ==============================
    if st.session_state.submitted_items:
        st.markdown("### 🧾 Items Added")
        df = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df, use_container_width=True)

        if st.button("📤 Submit All (Demo)"):
            st.success("✅ All data submitted to Google Sheet (demo only)")
            st.session_state.submitted_items = []

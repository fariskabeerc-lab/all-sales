import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet Form Dashboard", layout="wide")

# ==========================================
# LOAD ITEM DATA (for auto-fill)
# ==========================================
@st.cache_data
def load_item_data():
    file_path = "alllist.xlsx"  # Replace with your Excel path
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    return df

item_data = load_item_data()

# ==========================================
# LOGIN SYSTEM
# ==========================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida", "Hadeqat",
    "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan", "Superstore",
    "Tay Tay", "Safa oudmehta", "Port saeed"
]
password = "123123"

# Initialize session state variables
for key in ["logged_in", "selected_outlet", "submitted_items", "barcode_input", "qty_input", "expiry_input", "remarks_input"]:
    if key not in st.session_state:
        if key == "submitted_items":
            st.session_state[key] = []
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now()
        else:
            st.session_state[key] = ""

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
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ==========================================
# MAIN DASHBOARD
# ==========================================
else:
    outlet_name = st.session_state.selected_outlet
    st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)

    # FORM TYPE SELECTION
    form_type = st.sidebar.radio(
        "📋 Select Form Type",
        ["Expiry", "Damages", "Near Expiry"]
    )
    st.markdown("---")

    # ==============================
    # FORM INPUTS
    # ==============================
    col1, col2, col3 = st.columns(3)
    with col1:
        barcode = st.text_input("Barcode", value=st.session_state.barcode_input)
        st.session_state.barcode_input = barcode
    with col2:
        qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input)
        st.session_state.qty_input = qty
    with col3:
        # Show expiry only for Expiry and Near Expiry
        if form_type != "Damages":
            expiry = st.date_input("Expiry Date", st.session_state.expiry_input)
            st.session_state.expiry_input = expiry
        else:
            expiry = None

    # AUTO-FILL BASED ON BARCODE
    item_name = ""
    cost = 0.0
    selling = 0.0
    supplier = ""
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
        st.number_input("Cost", value=cost, disabled=True)
    with col6:
        st.number_input("Selling Price", value=selling, disabled=True)
    with col7:
        supplier = st.text_input("Supplier Name", value=supplier)

    gp = ((selling - cost) / cost * 100) if cost else 0
    st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

    remarks = st.text_area("Remarks [if any]", value=st.session_state.remarks_input)
    st.session_state.remarks_input = remarks

    # ==============================
    # ADD TO LIST BUTTON
    # ==============================
    if st.button("➕ Add to List"):
        if barcode and item_name:
            st.session_state.submitted_items.append({
                "Form Type": form_type,
                "Barcode": barcode,
                "Item Name": item_name,
                "Qty": qty,
                "Cost": cost,
                "Selling": selling,
                "Amount": cost * qty,
                "GP%": round(gp, 2),
                "Expiry": expiry.strftime("%d-%b-%y") if expiry else "",
                "Supplier": supplier,
                "Remarks": remarks,
                "Outlet": outlet_name
            })
            st.success("✅ Added to list successfully!")
            # CLEAR FORM INPUTS
            st.session_state.barcode_input = ""
            st.session_state.qty_input = 1
            st.session_state.expiry_input = datetime.now()
            st.session_state.remarks_input = ""
        else:
            st.warning("⚠️ Fill barcode and item before adding.")

    # ==============================
    # DISPLAY SUBMITTED ITEMS
    # ==============================
    if st.session_state.submitted_items:
        st.markdown("### 🧾 Items Added")
        df = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df, use_container_width=True)

        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("🧹 Clear List"):
                st.session_state.submitted_items = []
        with colB:
            if st.button("📤 Submit All (Demo)"):
                st.success("✅ All data submitted to Google Sheet (demo only)")
                st.session_state.submitted_items = []


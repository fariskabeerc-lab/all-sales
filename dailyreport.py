import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet Dashboard", layout="wide")

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
# LOGIN DATA
# ==========================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida",
    "Hadeqat", "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan",
    "Superstore", "Tay Tay", "Safa oudmehta", "Port saeed"
]
password_outlet = "123123"

# ==========================================
# SESSION VARIABLES
# ==========================================
for key in [
    "logged_in", "selected_outlet", "submitted_items",
    "barcode_input", "qty_input", "expiry_input", "remarks_input",
    "item_name", "cost", "selling", "supplier"
]:
    if key not in st.session_state:
        if key == "submitted_items":
            st.session_state[key] = []
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now()
        elif key in ["cost", "selling"]:
            st.session_state[key] = 0.0
        else:
            st.session_state[key] = ""

# ==========================================
# HELPER FUNCTION TO CLEAR FORM
# ==========================================
def clear_form():
    st.session_state.barcode_input = ""
    st.session_state.qty_input = 1
    st.session_state.expiry_input = datetime.now()
    st.session_state.remarks_input = ""
    st.session_state.item_name = ""
    st.session_state.cost = 0.0
    st.session_state.selling = 0.0
    st.session_state.supplier = ""

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    outlet = st.selectbox("Select your outlet", outlets)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "almadina" and pwd == password_outlet:
            st.session_state.logged_in = True
            st.session_state.selected_outlet = outlet
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ==========================================
# OUTLET DASHBOARD
# ==========================================
else:
    outlet_name = st.session_state.selected_outlet
    st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)

    # FORM TYPE
    form_type = st.sidebar.radio("📋 Select Form Type", ["Expiry", "Damages", "Near Expiry"])
    st.markdown("---")

    # INPUTS
    col1, col2, col3 = st.columns(3)
    with col1:
        barcode = st.text_input("Barcode", value=st.session_state.barcode_input)
        st.session_state.barcode_input = barcode
    with col2:
        qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input)
        st.session_state.qty_input = qty
    with col3:
        expiry = None
        if form_type != "Damages":
            expiry = st.date_input("Expiry Date", st.session_state.expiry_input)
            st.session_state.expiry_input = expiry

    # AUTO-FILL BASED ON BARCODE
    if barcode:
        match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
        if not match.empty:
            st.session_state.item_name = str(match.iloc[0]["Item Name"])
            st.session_state.cost = float(match.iloc[0]["Cost"])
            st.session_state.selling = float(match.iloc[0]["Selling"])
            st.session_state.supplier = str(match.iloc[0]["LP Supplier"])
        else:
            st.session_state.item_name = ""
            st.session_state.cost = 0.0
            st.session_state.selling = 0.0
            st.session_state.supplier = ""

    # DISPLAY ITEM FIELDS
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        st.session_state.item_name = st.text_input("Item Name", value=st.session_state.item_name)
    with col5:
        st.number_input("Cost", value=st.session_state.cost, disabled=True)
    with col6:
        st.number_input("Selling Price", value=st.session_state.selling, disabled=True)
    with col7:
        st.session_state.supplier = st.text_input("Supplier Name", value=st.session_state.supplier)

    gp = ((st.session_state.selling - st.session_state.cost) / st.session_state.cost * 100) if st.session_state.cost else 0
    st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

    remarks = st.text_area("Remarks [if any]", value=st.session_state.remarks_input)
    st.session_state.remarks_input = remarks

    # ADD TO LIST BUTTON
    if st.button("➕ Add to List"):
        if barcode and st.session_state.item_name:
            st.session_state.submitted_items.append({
                "Form Type": form_type,
                "Barcode": barcode,
                "Item Name": st.session_state.item_name,
                "Qty": qty,
                "Cost": st.session_state.cost,
                "Selling": st.session_state.selling,
                "Amount": st.session_state.cost * qty,
                "GP%": round(gp, 2),
                "Expiry": expiry.strftime("%d-%b-%y") if expiry else "",
                "Supplier": st.session_state.supplier,
                "Remarks": remarks,
                "Outlet": outlet_name
            })
            st.success("✅ Added to list successfully!")
            clear_form()
        else:
            st.warning("⚠️ Fill barcode and item before adding.")

    # DISPLAY LIST
    if st.session_state.submitted_items:
        st.markdown("### 🧾 Items Added")
        df = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df, use_container_width=True)

        col_submit, col_delete = st.columns([1, 1])
        with col_submit:
            if st.button("📤 Submit All"):
                st.success("✅ All data submitted (demo)")
                st.session_state.submitted_items = []
        with col_delete:
            to_delete = st.selectbox(
                "Select Item to Delete",
                options=[f"{i+1}. {item['Item Name']}" for i, item in enumerate(st.session_state.submitted_items)]
            )
            if st.button("❌ Delete Selected"):
                index = int(to_delete.split(".")[0]) - 1
                st.session_state.submitted_items.pop(index)
                st.success("✅ Item removed")
                st.experimental_rerun()

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

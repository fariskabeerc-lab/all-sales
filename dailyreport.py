import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet & Feedback Dashboard", layout="wide")

# ==========================================
# LOAD ITEM DATA (for auto-fill)
# ==========================================
@st.cache_data
def load_item_data():
    file_path = "alllist.xlsx"
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"⚠️ Data file not found: {file_path}. Please replace with your actual file or mock data.")
        return pd.DataFrame()

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
for key in ["logged_in", "selected_outlet", "submitted_items",
            "barcode_input", "qty_input", "expiry_input", "remarks_input",
            "item_name_input", "supplier_input",
            "cost_input", "selling_input",
            "submitted_feedback"]:
    if key not in st.session_state:
        if key in ["submitted_items", "submitted_feedback"]:
            st.session_state[key] = []
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now().date()
        elif key in ["cost_input", "selling_input"]:
            st.session_state[key] = "0.0"
        else:
            st.session_state[key] = ""

# ==========================================
# PAGE SELECTION
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

else:
    page = st.sidebar.radio("📌 Select Page", ["Outlet Dashboard", "Customer Feedback"])

    # ==========================================
    # OUTLET DASHBOARD
    # ==========================================
    if page == "Outlet Dashboard":
        outlet_name = st.session_state.selected_outlet
        st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)
        form_type = st.sidebar.radio("📋 Select Form Type", ["Expiry", "Damages", "Near Expiry"])
        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Barcode", value=st.session_state.barcode_input, key="barcode_input")
            barcode = st.session_state.barcode_input
        with col2:
            st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input, key="qty_input")
            qty = st.session_state.qty_input
        with col3:
            if form_type != "Damages":
                st.date_input("Expiry Date", st.session_state.expiry_input, key="expiry_input")
                expiry = st.session_state.expiry_input
            else:
                expiry = None

        # Auto-fill logic
        if barcode and not item_data.empty:
            match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
            if not match.empty:
                st.session_state.item_name_input = str(match.iloc[0]["Item Name"])
                st.session_state.supplier_input = str(match.iloc[0]["LP Supplier"])
            else:
                st.session_state.item_name_input = ""
                st.session_state.supplier_input = ""
        elif not barcode:
            st.session_state.item_name_input = ""
            st.session_state.supplier_input = ""

        col4, col5, col6, col7 = st.columns(4)
        with col4:
            st.text_input("Item Name", value=st.session_state.item_name_input, key="item_name_input")
            item_name = st.session_state.item_name_input
        with col5:
            st.text_input("Cost", value=st.session_state.cost_input, key="cost_input")
            try:
                cost = float(st.session_state.cost_input)
            except ValueError:
                cost = 0.0
                st.error("Invalid Cost value. Using 0.0.")
        with col6:
            st.text_input("Selling Price", value=st.session_state.selling_input, key="selling_input")
            try:
                selling = float(st.session_state.selling_input)
            except ValueError:
                selling = 0.0
                st.error("Invalid Selling Price value. Using 0.0.")
        with col7:
            st.text_input("Supplier Name", value=st.session_state.supplier_input, key="supplier_input")
            supplier = st.session_state.supplier_input

        gp = ((selling - cost) / cost * 100) if cost else 0
        st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

        st.text_area("Remarks [if any]", value=st.session_state.remarks_input, key="remarks_input")
        remarks = st.session_state.remarks_input

        # Add to list button with clearing fix
        if st.button("➕ Add to List"):
            if barcode and item_name:
                expiry_display = expiry.strftime("%d-%b-%y") if expiry else ""
                st.session_state.submitted_items.append({
                    "Form Type": form_type,
                    "Barcode": barcode,
                    "Item Name": item_name,
                    "Qty": qty,
                    "Cost": round(cost, 2),
                    "Selling": round(selling, 2),
                    "Amount": round(cost * qty, 2),
                    "GP%": round(gp, 2),
                    "Expiry": expiry_display,
                    "Supplier": supplier,
                    "Remarks": remarks,
                    "Outlet": outlet_name
                })
                st.success("✅ Added to list successfully!")

                # --- FORM CLEARING FIX ---
                for k, v in {
                    "barcode_input": "",
                    "qty_input": 1,
                    "expiry_input": datetime.now().date(),
                    "remarks_input": "",
                    "item_name_input": "",
                    "supplier_input": "",
                    "cost_input": "0.0",
                    "selling_input": "0.0",
                }.items():
                    st.session_state[k] = v

                st.rerun()
            else:
                st.warning("⚠️ Fill barcode and item name before adding.")

        if st.session_state.submitted_items:
            st.markdown("### 🧾 Items Added")
            df = pd.DataFrame(st.session_state.submitted_items)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col_submit, col_delete = st.columns([1, 1])
            with col_submit:
                if st.button("📤 Submit All"):
                    st.success(f"✅ All {len(st.session_state.submitted_items)} items submitted for {outlet_name} (demo)")
                    st.session_state.submitted_items = []
                    st.rerun()

            with col_delete:
                options = [f"{i+1}. {item['Item Name']} ({item['Qty']} pcs)" for i, item in enumerate(st.session_state.submitted_items)]
                to_delete = st.selectbox("Select Item to Delete", options)
                if st.button("❌ Delete Selected"):
                    index = int(to_delete.split(".")[0]) - 1
                    if 0 <= index < len(st.session_state.submitted_items):
                        st.session_state.submitted_items.pop(index)
                        st.success("✅ Item removed")
                        st.rerun()

    # ==========================================
    # CUSTOMER FEEDBACK PAGE
    # ==========================================
    else:
        outlet_name = st.session_state.selected_outlet
        st.title("📝 Customer Feedback Form")
        st.markdown(f"Submitting feedback for **{outlet_name}**")
        st.markdown("---")

        with st.form("feedback_form", clear_on_submit=True):
            name = st.text_input("Customer Name")
            email = st.text_input("Email (Optional)")
            rating = st.slider("Rate Our Outlet", 1, 5, 5)
            feedback = st.text_area("Your Feedback (Required)")
            submitted = st.form_submit_button("📤 Submit Feedback")

        if submitted:
            if name.strip() and feedback.strip():
                st.session_state.submitted_feedback.append({
                    "Customer Name": name,
                    "Email": email if email else "N/A",
                    "Rating": f"{rating} / 5",
                    "Outlet": outlet_name,
                    "Feedback": feedback,
                    "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("✅ Feedback submitted successfully! The form has been cleared.")
            else:
                st.error("⚠️ Please fill Customer Name and Feedback before submitting.")

        if st.session_state.submitted_feedback:
            st.markdown("### 🗂 Recent Customer Feedback")
            df = pd.DataFrame(st.session_state.submitted_feedback)
            st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)

            if st.button("🗑 Clear All Feedback Records", type="primary"):
                st.session_state.submitted_feedback = []
                st.rerun()

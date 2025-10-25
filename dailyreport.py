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
        st.error(f"⚠️ Data file not found: {file_path}. Using mock data for demonstration.")
        return pd.DataFrame({
            "Item Bar Code": ["123456789012", "987654321098"],
            "Item Name": ["Mock Milk 1L", "Mock Bread Loaf"],
            "LP Supplier": ["Dairy King Co.", "Bakery Goods Ltd."],
        })

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
            "barcode_value", 
            "qty_input", "expiry_input", "remarks_input",
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

# ------------------------------------------------------------------
# --- Lookup Logic Function (Callable via Lookup Form submission) ---
# ------------------------------------------------------------------
def lookup_item_and_update_state():
    # Retrieve the value from the submitted form's key
    barcode = st.session_state.lookup_barcode_input
    
    if not barcode:
        st.session_state.item_name_input = ""
        st.session_state.supplier_input = ""
        st.session_state.barcode_value = ""
        return

    st.session_state.barcode_value = barcode 
    
    if not item_data.empty:
        # Match barcode, ensuring string comparison
        match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
        
        if not match.empty:
            # Update session state with found data
            st.session_state.item_name_input = str(match.iloc[0]["Item Name"])
            st.session_state.supplier_input = str(match.iloc[0]["LP Supplier"])
            st.toast("✅ Item details loaded.", icon="🔍")
        else:
            # Clear/set fields if not found
            st.session_state.item_name_input = ""
            st.session_state.supplier_input = ""
            st.toast("⚠️ Barcode not found. Manual entry required.", icon="⚠️")
# ------------------------------------------------------------------

# --- Form Submission Handler (Callback) ---
def add_item_to_list(barcode, item_name, qty, cost, selling, expiry, supplier, remarks, form_type, outlet_name):
    
    if not barcode.strip() or not item_name.strip():
        st.error("⚠️ Fill barcode and item name before adding.")
        return 

    expiry_display = expiry.strftime("%d-%b-%y") if expiry else ""
    gp = ((selling - cost) / cost * 100) if cost else 0

    st.session_state.submitted_items.append({
        "Form Type": form_type,
        "Barcode": barcode.strip(),
        "Item Name": item_name.strip(),
        "Qty": qty,
        "Cost": round(cost, 2),
        "Selling": round(selling, 2),
        "Amount": round(cost * qty, 2),
        "GP%": round(gp, 2),
        "Expiry": expiry_display,
        "Supplier": supplier.strip(),
        "Remarks": remarks.strip(),
        "Outlet": outlet_name
    })

    # --- CLEAR ALL COLUMNS SAFELY ---
    st.session_state.barcode_value = ""
    st.session_state.item_name_input = ""
    st.session_state.supplier_input = ""
    st.session_state.cost_input = "0.0"
    st.session_state.selling_input = "0.0"

    st.toast("✅ Added to list successfully! The form has been cleared.", icon="➕")
# -------------------------------------------------


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

        # --- Dedicated Lookup Form (Enter/Scan instantly updates state) ---
        # The Enter key in the st.text_input below will submit this form.
        with st.form("barcode_lookup_form", clear_on_submit=False):
            
            # Barcode input
            st.text_input(
                "Barcode",
                key="lookup_barcode_input", 
                placeholder="Enter or scan barcode and press Enter",
                value=st.session_state.barcode_value
            )
            
            # FIX: Removed label_visibility="collapsed" to avoid TypeError.
            # This visible button captures the Enter key press and runs the lookup.
            st.form_submit_button(
                "Trigger Lookup (Press Enter)", 
                on_click=lookup_item_and_update_state, 
                help="Press Enter in the barcode field to look up item."
            )

        st.markdown("---")
        # -----------------------------------------------------------

        # --- Start of the Item Entry Form (Clears on submit) ---
        with st.form("item_entry_form", clear_on_submit=True):
            
            # Form field variables (local to the form context)
            col1, col2 = st.columns(2)
            with col1:
                qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input, key="form_qty_input")
            with col2:
                if form_type != "Damages":
                    expiry = st.date_input("Expiry Date", st.session_state.expiry_input, key="form_expiry_input")
                else:
                    expiry = None

            col4, col5, col6, col7 = st.columns(4)
            with col4:
                # Defaults from session state, updated by the barcode input's lookup
                item_name = st.text_input("Item Name", value=st.session_state.item_name_input, key="form_item_name_input")
            with col5:
                cost_str = st.text_input("Cost", value=st.session_state.cost_input, key="form_cost_input")
            with col6:
                selling_str = st.text_input("Selling Price", value=st.session_state.selling_input, key="form_selling_input")
            with col7:
                # Defaults from session state, updated by the barcode input's lookup
                supplier = st.text_input("Supplier Name", value=st.session_state.supplier_input, key="form_supplier_input")

            # Try to convert cost and selling to float
            try:
                cost = float(cost_str)
            except ValueError:
                cost = 0.0
            try:
                selling = float(selling_str)
            except ValueError:
                selling = 0.0

            gp = ((selling - cost) / cost * 100) if cost else 0
            st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

            remarks = st.text_area("Remarks [if any]", key="form_remarks_input")

            # Form submission button using the callback
            st.form_submit_button(
                "➕ Add to List", 
                type="primary",
                on_click=add_item_to_list,
                # Pass barcode value from session state
                args=(
                    st.session_state.barcode_value, item_name, qty, cost, 
                    selling, expiry, supplier, remarks, form_type, outlet_name
                )
            )
            # --- End of the Item Entry Form ---


        # Displaying and managing the list
        if st.session_state.submitted_items:
            st.markdown("### 🧾 Items Added")
            # Show all item types (Expiry, Damages, Near Expiry) in one list
            df = pd.DataFrame(st.session_state.submitted_items)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col_submit, col_delete = st.columns([1, 1])
            with col_submit:
                if st.button("📤 Submit All"):
                    st.success(f"✅ All {len(st.session_state.submitted_items)} items submitted for {outlet_name} (demo). Resetting.")
                    st.session_state.submitted_items = []
                    # Clear state upon final submission
                    st.session_state.barcode_value = ""
                    st.session_state.item_name_input = ""
                    st.session_state.supplier_input = ""
                    st.session_state.cost_input = "0.0"
                    st.session_state.selling_input = "0.0"
                    st.rerun() # Rerun to fully reset the page

            with col_delete:
                options = [f"{i+1}. {item['Item Name']} ({item['Qty']} pcs)" for i, item in enumerate(st.session_state.submitted_items)]
                if options:
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
            rating = st.slider("Rate Our Outlet", 1, 5, 5)
            feedback = st.text_area("Your Feedback (Required)")
            submitted = st.form_submit_button("📤 Submit Feedback")

        if submitted:
            if name.strip() and feedback.strip():
                st.session_state.submitted_feedback.append({
                    "Customer Name": name,
                    "Rating": f"{rating} / 5",
                    "Outlet": outlet_name,
                    "Feedback": feedback,
                    "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("✅ Feedback submitted successfully! The form has been cleared.")
            else:
                st.error("⚠️ Please fill Customer Name and Feedback before submitting.")

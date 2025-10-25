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
        # Create mock data if the file is missing to ensure the app runs
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
            "barcode_input",  # Input for barcode
            "qty_input", "expiry_input", "remarks_input",
            "item_name_input", "supplier_input", # Used for auto-fill defaults
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

# --- Auto-fill/Lookup Logic Function (Callable via button) ---
def lookup_item_and_update_state():
    barcode = st.session_state.barcode_input # Get the current value from the input widget
    if barcode and not item_data.empty:
        match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
        if not match.empty:
            st.session_state.item_name_input = str(match.iloc[0]["Item Name"])
            st.session_state.supplier_input = str(match.iloc[0]["LP Supplier"])
            st.success("✅ Item details loaded.")
        else:
            st.session_state.item_name_input = ""
            st.session_state.supplier_input = ""
            st.warning("⚠️ Barcode not found in list. Please fill item details manually.")
    else:
        st.session_state.item_name_input = ""
        st.session_state.supplier_input = ""
        st.warning("⚠️ Please enter a barcode to lookup.")
    # Rerun is needed to refresh the form fields with new session state defaults
    st.rerun() 
# -------------------------------------------------------------


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

        # --- Barcode Input and Lookup Button (OUTSIDE MAIN FORM) ---
        col_bar, col_btn = st.columns([3, 1])
        with col_bar:
             # This input is outside the main form so Enter doesn't submit the form
             st.text_input("Barcode", key="barcode_input", placeholder="Enter or scan barcode")
        
        with col_btn:
            # Button to trigger the lookup function
            st.button("🔍 Lookup Item", on_click=lookup_item_and_update_state, use_container_width=True)
        
        st.markdown("---")
        # -----------------------------------------------------------

        # --- Start of the Item Entry Form (All inputs inside for submission control) ---
        with st.form("item_entry_form", clear_on_submit=True):
            
            # Using internal keys for form widgets
            col1, col2 = st.columns(2)
            with col1:
                qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input, key="form_qty_input")
            with col2:
                if form_type != "Damages":
                    expiry = st.date_input("Expiry Date", st.session_state.expiry_input, key="form_expiry_input")
                else:
                    expiry = None

            # Item details (auto-filled from session state defaults)
            col4, col5, col6, col7 = st.columns(4)
            with col4:
                # Defaults from session state, allowing manual override
                item_name = st.text_input("Item Name", value=st.session_state.item_name_input, key="form_item_name_input")
            with col5:
                cost_str = st.text_input("Cost", value=st.session_state.cost_input, key="form_cost_input")
            with col6:
                selling_str = st.text_input("Selling Price", value=st.session_state.selling_input, key="form_selling_input")
            with col7:
                # Defaults from session state, allowing manual override
                supplier = st.text_input("Supplier Name", value=st.session_state.supplier_input, key="form_supplier_input")

            # Try to convert cost and selling to float
            try:
                cost = float(cost_str)
            except ValueError:
                cost = 0.0
                st.error("Invalid Cost value. Using 0.0.")
            try:
                selling = float(selling_str)
            except ValueError:
                selling = 0.0
                st.error("Invalid Selling Price value. Using 0.0.")

            gp = ((selling - cost) / cost * 100) if cost else 0
            st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

            remarks = st.text_area("Remarks [if any]", key="form_remarks_input")

            # Form submission button - only this button submits the data.
            submitted = st.form_submit_button("➕ Add to List", type="primary")
            # --- End of the Item Entry Form ---

        # Logic for processing the submitted item
        if submitted:
            barcode = st.session_state.barcode_input # Get barcode from the input outside the form
            if barcode.strip() and item_name.strip():
                expiry_display = expiry.strftime("%d-%b-%y") if expiry else ""
                
                # Append the submitted data to session state
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

                st.success("✅ Added to list successfully! The form has been cleared.")
                
                # --- CLEAR ALL COLUMNS AS REQUESTED ---
                # Clear all related session state variables to reset the fields for the next entry
                # This clears the Barcode input (outside the form) and the auto-fill defaults
                st.session_state.barcode_input = ""
                st.session_state.item_name_input = ""
                st.session_state.supplier_input = ""
                st.session_state.cost_input = "0.0"
                st.session_state.selling_input = "0.0"
                # st.rerun() is necessary to apply these session state changes (especially barcode_input)
                st.rerun()
            else:
                st.warning("⚠️ Fill barcode and item name before adding.")


        # Displaying and managing the list
        if st.session_state.submitted_items:
            st.markdown("### 🧾 Items Added")
            df = pd.DataFrame(st.session_state.submitted_items)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col_submit, col_delete = st.columns([1, 1])
            with col_submit:
                if st.button("📤 Submit All"):
                    st.success(f"✅ All {len(st.session_state.submitted_items)} items submitted for {outlet_name} (demo)")
                    st.session_state.submitted_items = []
                    # Clear lookup state upon final submission as well
                    st.session_state.barcode_input = ""
                    st.session_state.item_name_input = ""
                    st.session_state.supplier_input = ""
                    st.session_state.cost_input = "0.0"
                    st.session_state.selling_input = "0.0"
                    st.rerun()

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

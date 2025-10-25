import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
# Corrected the typo: st.set_page_config
st.set_page_config(page_title="Outlet & Feedback Dashboard", layout="wide")

# ==========================================
# LOAD ITEM DATA (for auto-fill)
# ==========================================
@st.cache_data
def load_item_data():
    file_path = "alllist.xlsx"
    try:
        # Using a context manager to ensure file is closed, though read_excel handles it.
        # Adding a warning here as the file is likely not present for a user running the code.
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
             "barcode_value",  # Used to store the currently scanned/typed barcode
             "qty_input", "expiry_input", "remarks_input",
             "item_name_input", "supplier_input",  # Used for auto-fill/manual typing
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
# --- Lookup Logic Function (Callback for Barcode Form) ---
# ------------------------------------------------------------------
def lookup_item_and_update_state():
    # Retrieve the value from the submitted form's key (barcode_lookup_form's text_input)
    barcode = st.session_state.lookup_barcode_input
    
    if not barcode:
        st.session_state.item_name_input = ""
        st.session_state.supplier_input = ""
        st.session_state.barcode_value = ""
        st.toast("⚠️ Barcode cleared.", icon="❌")
        st.rerun()
        return

    # Update the general state variable that the main form widgets use for their 'value'
    st.session_state.barcode_value = barcode 
    
    if not item_data.empty:
        # Ensure comparison is on stripped strings
        match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
        
        if not match.empty:
            # Update generic session state keys which the main form uses for 'value'
            st.session_state.item_name_input = str(match.iloc[0]["Item Name"])
            st.session_state.supplier_input = str(match.iloc[0]["LP Supplier"])
            # Keep other values as they were, e.g., cost, selling, qty, expiry
            st.toast("✅ Item details loaded.", icon="🔍")
        else:
            # Clear auto-filled fields if barcode is new/unknown
            st.session_state.item_name_input = ""
            st.session_state.supplier_input = ""
            st.session_state.cost_input = "0.0"
            st.session_state.selling_input = "0.0"
            st.toast("⚠️ Barcode not found. Manual entry required.", icon="⚠️")
    
    # CRITICAL: Force a rerun here so the main form reloads with the new state values
    st.rerun() 
# ------------------------------------------------------------------

# -------------------------------------------------
# --- Main Form Submission Handler ---
# -------------------------------------------------
def process_item_entry(barcode, item_name, qty, cost_str, selling_str, expiry, supplier, remarks, form_type, outlet_name):
    
    # Validation and conversion
    if not barcode.strip() or not item_name.strip():
        # Using a dedicated error is better than st.error here as the form is already submitted
        st.toast("⚠️ Fill barcode and item name before adding.", icon="❌")
        return False

    try:
        cost = float(cost_str)
    except ValueError:
        cost = 0.0
    try:
        selling = float(selling_str)
    except ValueError:
        selling = 0.0

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

    # --- CRITICAL FIX: CLEAR ALL COLUMNS SAFELY ---
    # Clear the generic session state keys that the main form uses for its 'value'
    st.session_state.barcode_value = ""          # Clears the Barcode input in the lookup form
    st.session_state.item_name_input = ""        # Clears the Item Name input
    st.session_state.supplier_input = ""         # Clears the Supplier Name input
    st.session_state.cost_input = "0.0"          # Clears Cost
    st.session_state.selling_input = "0.0"       # Clears Selling Price
    st.session_state.qty_input = 1               # Resets Quantity
    st.session_state.remarks_input = ""          # Clears Remarks
    st.session_state.expiry_input = datetime.now().date() # Resets Expiry Date
    
    st.toast("✅ Added to list successfully! The form has been cleared.", icon="➕")
    return True
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
    # Logout button
    if st.sidebar.button("Logout 🚪", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.submitted_items = [] # Clear the list on logout
        st.session_state.submitted_feedback = [] # Clear feedback on logout
        st.rerun()

    page = st.sidebar.radio("📌 Select Page", ["Outlet Dashboard", "Customer Feedback"])

    # ==========================================
    # OUTLET DASHBOARD
    # ==========================================
    if page == "Outlet Dashboard":
        outlet_name = st.session_state.selected_outlet
        st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)
        form_type = st.sidebar.radio("📋 Select Form Type", ["Expiry", "Damages", "Near Expiry"])
        st.markdown("---")

        # --- Dedicated Lookup Form (for instant barcode lookup on Enter) ---
        with st.form("barcode_lookup_form", clear_on_submit=False):
            
            col_bar, col_btn = st.columns([5, 1])
            
            with col_bar:
                # Barcode input - The key is 'lookup_barcode_input' and it determines the value used in callback
                st.text_input(
                    "Barcode",
                    key="lookup_barcode_input", 
                    placeholder="Enter or scan barcode and press Enter to look up details",
                    # Ensure the value is displayed from the session state after a lookup/submit
                    value=st.session_state.barcode_value
                )
            
            with col_btn:
                # This button captures the Enter key press from the barcode input
                st.markdown("<div style='height: 33px;'></div>", unsafe_allow_html=True) # Spacer
                st.form_submit_button(
                    "🔍", 
                    on_click=lookup_item_and_update_state, # Callback runs and forces rerun
                    help="Click or press Enter in the barcode field to look up item.",
                    type="secondary",
                    use_container_width=True
                )

        st.markdown("---")
        # -----------------------------------------------------------

        # --- Start of the Item Entry Form (Only submits on button click) ---
        with st.form("item_entry_form", clear_on_submit=False): 

            # Form field variables (local to the form context)
            col1, col2 = st.columns(2)
            with col1:
                # CRITICAL: Set initial value from generic state variable
                qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input, key="form_qty_input")
            with col2:
                if form_type != "Damages":
                    # CRITICAL: Set initial value from generic state variable
                    expiry = st.date_input("Expiry Date", st.session_state.expiry_input, key="form_expiry_input")
                else:
                    expiry = None

            col4, col5, col6, col7 = st.columns(4)
            with col4:
                # CRITICAL: Use session state to display the looked-up value
                item_name = st.text_input("Item Name", value=st.session_state.item_name_input, key="form_item_name_input")
            with col5:
                # CRITICAL: Use session state to display the looked-up value
                cost_str = st.text_input("Cost", value=st.session_state.cost_input, key="form_cost_input")
            with col6:
                # CRITICAL: Use session state to display the looked-up value
                selling_str = st.text_input("Selling Price", value=st.session_state.selling_input, key="form_selling_input")
            with col7:
                # CRITICAL: Use session state to display the looked-up value
                supplier = st.text_input("Supplier Name", value=st.session_state.supplier_input, key="form_supplier_input")

            # Calculate and display GP% (based on current form values, not session state)
            try:
                temp_cost = float(cost_str)
                temp_selling = float(selling_str)
            except ValueError:
                temp_cost = 0.0
                temp_selling = 0.0
                
            gp = ((temp_selling - temp_cost) / temp_cost * 100) if temp_cost else 0
            st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

            # CRITICAL: Use session state to display the looked-up value
            remarks = st.text_area("Remarks [if any]", value=st.session_state.remarks_input, key="form_remarks_input")

            # Form submission button (NO on_click)
            submitted_item = st.form_submit_button(
                "➕ Add to List", 
                type="primary",
            )
            # --- End of the Item Entry Form ---

        # --------------------------------------------------------
        # --- Handle Main Form Submission ONLY on Button Click ---
        # --------------------------------------------------------
        if submitted_item:
            # The logic runs only when the button is explicitly clicked.
            # We pass the values from the internal form state keys.
            success = process_item_entry(
                # Get current values from form state keys
                st.session_state.barcode_value, # Barcode is from the lookup form's persistent state
                st.session_state.form_item_name_input, 
                st.session_state.form_qty_input, 
                st.session_state.form_cost_input, 
                st.session_state.form_selling_input, 
                st.session_state.form_expiry_input if form_type != "Damages" else None, 
                st.session_state.form_supplier_input, 
                st.session_state.form_remarks_input,
                form_type, 
                outlet_name
            )
            if success:
                 st.rerun() # Rerun to reflect list update and clear inputs via session state

        # Displaying and managing the list
        if st.session_state.submitted_items:
            st.markdown("### 🧾 Items Added")
            df = pd.DataFrame(st.session_state.submitted_items)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col_submit, col_delete = st.columns([1, 1])
            with col_submit:
                if st.button("📤 Submit All", type="primary"):
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
                    # Added a default None option to prevent immediate selection
                    to_delete = st.selectbox("Select Item to Delete", ["Select item to remove..."] + options)
                    if to_delete != "Select item to remove...":
                        if st.button("❌ Delete Selected", type="secondary"):
                            # Index is based on the options list (1-based), so we subtract 1 for the list index
                            index = options.index(to_delete) 
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
                    "Email": email.strip(),
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

            if st.button("🗑 Clear All Feedback Records", type="secondary"):
                st.session_state.submitted_feedback = []
                st.rerun()

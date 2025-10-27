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
        # Ensure column names are clean
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        # Display the actual error if the file isn't found
        st.error(f"⚠️ Data file not found: {file_path}. Please ensure the file is in the application directory.")
        # Return an empty DataFrame so the application doesn't crash
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
             # Updated state keys for simpler form management
             "barcode_input", "qty_input", "expiry_input", "remarks_input",
             "submitted_feedback"]:
    if key not in st.session_state:
        if key in ["submitted_items", "submitted_feedback"]:
            st.session_state[key] = []
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now().date()
        else:
            st.session_state[key] = ""

# ------------------------------------------------------------------
# --- Lookup Logic Function (Callback for Barcode Form) ---
# NOTE: This function is no longer needed as the lookup is done in-line,
# but we keep a dummy function just in case.
# ------------------------------------------------------------------
# Removed previous complex lookup logic.

# -------------------------------------------------
# --- Main Form Submission Handler (Handles Clearing) ---
# -------------------------------------------------
def process_item_entry(barcode, item_name, qty, cost_str, selling_str, expiry, supplier, remarks, form_type, outlet_name):
    
    # Validation and conversion
    if not barcode.strip() or not item_name.strip():
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
    # Clear the generic session state keys that the form uses for its 'value' on next rerun
    st.session_state.barcode_input = ""          
    st.session_state.qty_input = 1               
    st.session_state.remarks_input = ""          
    st.session_state.expiry_input = datetime.now().date()
    
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
        st.session_state.submitted_items = [] 
        st.session_state.submitted_feedback = [] 
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

        # --- Start of the Item Entry Form ---
        with st.form("item_entry_form", clear_on_submit=False): 
            
            # --- Barcode and Qty inputs (using the simplified layout from your successful code) ---
            col1, col2, col3 = st.columns(3)
            with col1:
                # Use a specific key for the barcode input value
                barcode = st.text_input("Barcode", key="form_barcode_input", value=st.session_state.barcode_input)
            with col2:
                # Use a specific key for the qty input value
                qty = st.number_input("Qty [PCS]", min_value=1, key="form_qty_input", value=st.session_state.qty_input)
            with col3:
                # Show expiry only for Expiry and Near Expiry
                if form_type != "Damages":
                    # Use a specific key for the expiry input value
                    expiry = st.date_input("Expiry Date", key="form_expiry_input", value=st.session_state.expiry_input)
                else:
                    expiry = None

            # --- In-line Auto-Fill Logic (based on your successful code) ---
            
            # Initialize default values
            initial_item_name = ""
            initial_cost_str = "0.0"
            initial_selling_str = "0.0"
            initial_supplier = ""
            
            # Perform lookup only if a barcode is entered
            if barcode:
                # Ensure the comparison column and lookup barcode are strings
                match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
                
                if not match.empty:
                    # Pull values from the first match
                    initial_item_name = str(match.iloc[0]["Item Name"])
                    
                    # Safely convert to string for the text_input widget
                    # FIX: Use .get() and string conversion to ensure it doesn't break if columns are slightly different
                    initial_cost_str = str(match.iloc[0].get("Cost", "0.0"))
                    initial_selling_str = str(match.iloc[0].get("Selling Price", "0.0")) # Assuming 'Selling Price' is the column name
                    
                    initial_supplier = str(match.iloc[0]["LP Supplier"])
                    
            # Check if values are already in the form state (i.e., user typed/edited them)
            # This ensures user edits persist across reruns until submitted
            
            # The 'value' parameter of st.text_input only sets the initial value.
            # We rely on Streamlit's internal form state keys (form_item_name_input, etc.)
            # to hold the *current* user-entered value. 
            # We set the initial value to the lookup result *only if* the form hasn't been used yet.
            
            col4, col5, col6, col7 = st.columns(4)
            with col4:
                # The value here is critical: Use the lookup result as the initial value.
                item_name = st.text_input("Item Name", key="form_item_name_input", value=initial_item_name)
            with col5:
                # FIX: Cost is now editable and not disabled
                cost_str = st.text_input("Cost", key="form_cost_input", value=initial_cost_str)
            with col6:
                # FIX: Selling Price is now editable and not disabled
                selling_str = st.text_input("Selling Price", key="form_selling_input", value=initial_selling_str)
            with col7:
                # The value here is critical: Use the lookup result as the initial value.
                supplier = st.text_input("Supplier Name", key="form_supplier_input", value=initial_supplier)

            # Recalculate GP% based on the currently displayed/edited values
            try:
                current_cost = float(cost_str)
                current_selling = float(selling_str)
            except ValueError:
                current_cost = 0.0
                current_selling = 0.0
                
            gp = ((current_selling - current_cost) / current_cost * 100) if current_cost else 0
            st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

            # Use a specific key for the remarks input value
            remarks = st.text_area("Remarks [if any]", key="form_remarks_input", value=st.session_state.remarks_input)

            # Form submission button 
            submitted_item = st.form_submit_button(
                "➕ Add to List", 
                type="primary",
            )
            # --- End of the Item Entry Form ---
            
            # --- Capture the latest user input for use on the next rerun ---
            # This ensures that if the user manually changes a field, that change persists 
            # until the next barcode lookup or form submission.
            st.session_state.barcode_input = barcode
            st.session_state.qty_input = qty
            if form_type != "Damages" and expiry is not None:
                st.session_state.expiry_input = expiry
            st.session_state.remarks_input = remarks
            
        # --------------------------------------------------------
        # --- Handle Main Form Submission ONLY on Button Click ---
        # --------------------------------------------------------
        if submitted_item:
            # We pass the final, submitted values from the form's state keys.
            success = process_item_entry(
                # Use the form's state keys to get the final, user-submitted value
                st.session_state.form_barcode_input, 
                st.session_state.form_item_name_input, 
                st.session_state.form_qty_input, 
                st.session_state.form_cost_input, # Now uses the editable cost value
                st.session_state.form_selling_input, # Now uses the editable selling value
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
                    # Clear state upon final submission (clears form on rerun)
                    st.session_state.submitted_items = []
                    st.session_state.barcode_input = ""
                    st.session_state.qty_input = 1
                    st.session_state.remarks_input = ""
                    st.session_state.expiry_input = datetime.now().date()
                    st.rerun() # Rerun to fully reset the page

            with col_delete:
                options = [f"{i+1}. {item['Item Name']} ({item['Qty']} pcs)" for i, item in enumerate(st.session_state.submitted_items)]
                if options:
                    to_delete = st.selectbox("Select Item to Delete", ["Select item to remove..."] + options)
                    if to_delete != "Select item to remove...":
                        if st.button("❌ Delete Selected", type="secondary"):
                            index = options.index(to_delete) 
                            st.session_state.submitted_items.pop(index)
                            st.success("✅ Item removed")
                            st.rerun()

    # ==========================================
    # CUSTOMER FEEDBACK PAGE (UNCHANGED)
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

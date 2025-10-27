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
        
        # Check only critical columns needed for the app to run
        required_cols = ["Item Bar Code", "Item Name", "LP Supplier"] 
        for col in required_cols:
            if col not in df.columns:
                st.error(f"⚠️ Missing critical column: '{col}' in alllist.xlsx. Please check the file.")
                return pd.DataFrame()
        return df
    except FileNotFoundError:
        st.error(f"⚠️ Data file not found: {file_path}. Please ensure the file is in the application directory.")
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
             # Main form inputs (values persist until submitted/cleared)
             "barcode_value", "qty_input", "expiry_input", "remarks_input",
             "item_name_input", "supplier_input", 
             "cost_input", "selling_input",
             # Lookup state (temporary data from filter)
             "lookup_data", "submitted_feedback"]:
    if key not in st.session_state:
        if key in ["submitted_items", "submitted_feedback"]:
            st.session_state[key] = []
        elif key == "lookup_data":
            st.session_state[key] = pd.DataFrame()
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now().date()
        elif key in ["cost_input", "selling_input"]:
            st.session_state[key] = "0.0" # Ensure cost/selling starts at 0.0
        else:
            st.session_state[key] = ""

# ------------------------------------------------------------------
# --- Lookup Logic Function (Callback for Barcode Form) ---
# FIX: This now displays the table AND transfers the details in one step.
# ------------------------------------------------------------------
def lookup_item_and_update_state():
    # Retrieve the value from the submitted form's key
    barcode = st.session_state.lookup_barcode_input
    
    # Reset lookup data and current item details
    st.session_state.lookup_data = pd.DataFrame()
    st.session_state.barcode_value = barcode 
    st.session_state.item_name_input = ""
    st.session_state.supplier_input = ""
    
    if not barcode:
        st.toast("⚠️ Barcode cleared.", icon="❌")
        st.rerun()
        return

    if not item_data.empty:
        # Ensure comparison is on stripped strings
        match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
        
        if not match.empty:
            # Get the first matching row
            row = match.iloc[0]
            
            # 1. Prepare data for display table
            df_display = row[["Item Name", "LP Supplier"]].to_frame().T
            df_display.columns = ["Item Name", "Supplier"]
            st.session_state.lookup_data = df_display.reset_index(drop=True)
            
            # 2. Automatically transfer details to the main form state
            st.session_state.item_name_input = str(row["Item Name"])
            st.session_state.supplier_input = str(row["LP Supplier"])
            
            st.toast("✅ Item found. Details loaded to entry form.", icon="🔍")
        else:
            st.toast("⚠️ Barcode not found. Details cleared.", icon="⚠️")
    else:
         st.toast("⚠️ Item data file is empty.", icon="⚠️")
    
    # CRITICAL: Force a rerun here so the display and main form inputs update
    st.rerun() 
# ------------------------------------------------------------------

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
    # Clear the generic session state keys that the main form uses for its 'value'
    st.session_state.barcode_value = ""          
    st.session_state.item_name_input = ""        
    st.session_state.supplier_input = ""         
    st.session_state.cost_input = "0.0"          
    st.session_state.selling_input = "0.0"       
    st.session_state.qty_input = 1               
    st.session_state.remarks_input = ""          
    st.session_state.expiry_input = datetime.now().date()
    st.session_state.lookup_data = pd.DataFrame() # Clear the lookup table display
    
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

        # --- 1. Dedicated Lookup Form (Enter key only triggers search/filter) ---
        with st.form("barcode_lookup_form", clear_on_submit=False):
            
            col_bar, col_btn = st.columns([5, 1])
            
            with col_bar:
                st.text_input(
                    "Barcode Lookup",
                    key="lookup_barcode_input", 
                    placeholder="Enter or scan barcode and press Enter to search details",
                    value=st.session_state.barcode_value
                )
            
            with col_btn:
                st.markdown("<div style='height: 33px;'></div>", unsafe_allow_html=True) # Spacer
                st.form_submit_button(
                    "🔍 Search", 
                    on_click=lookup_item_and_update_state, 
                    help="Click or press Enter in the barcode field to look up item.",
                    type="secondary",
                    use_container_width=True
                )

        # --- 2. Item Details Display Panel (The 'Filter' result) ---
        if not st.session_state.lookup_data.empty:
            st.markdown("### 🔍 Found Item Details")
            # Display the table with only Name and Supplier
            st.dataframe(st.session_state.lookup_data, use_container_width=True, hide_index=True)
            st.markdown("---") # Separator after lookup panel

        # --- 3. Start of the Main Item Entry Form ---
        with st.form("item_entry_form", clear_on_submit=False): 
            
            # --- Row 1: Qty and Expiry ---
            col1, col2 = st.columns(2)
            with col1:
                qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input, key="form_qty_input")
            with col2:
                if form_type != "Damages":
                    expiry = st.date_input("Expiry Date", st.session_state.expiry_input, key="form_expiry_input")
                else:
                    expiry = None

            # --- Row 2: Item Name, Cost, Selling, Supplier ---
            col4, col5, col6, col7 = st.columns(4)
            with col4:
                # Value initialized from session state (updated by automatic transfer)
                item_name = st.text_input("Item Name", value=st.session_state.item_name_input, key="form_item_name_input")
            with col5:
                # Cost is editable and defaults to "0.0"
                cost_str = st.text_input("Cost", value=st.session_state.cost_input, key="form_cost_input")
            with col6:
                # Selling is editable and defaults to "0.0"
                selling_str = st.text_input("Selling Price", value=st.session_state.selling_input, key="form_selling_input")
            with col7:
                # Value initialized from session state (updated by automatic transfer)
                supplier = st.text_input("Supplier Name", value=st.session_state.supplier_input, key="form_supplier_input")

            # Calculate and display GP%
            try:
                temp_cost = float(cost_str)
                temp_selling = float(selling_str)
            except ValueError:
                temp_cost = 0.0
                temp_selling = 0.0
                
            gp = ((temp_selling - temp_cost) / temp_cost * 100) if temp_cost else 0
            st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

            # --- Remarks and Submit Button ---
            remarks = st.text_area("Remarks [if any]", value=st.session_state.remarks_input, key="form_remarks_input")

            # Form submission button (only this button adds the item)
            submitted_item = st.form_submit_button(
                "➕ Add to List", 
                type="primary",
            )
            # --- End of the Item Entry Form ---

        # --------------------------------------------------------
        # --- Handle Main Form Submission ONLY on Button Click ---
        # --------------------------------------------------------
        if submitted_item:
            # We use the barcode from the *lookup form state* since the lookup form holds the master barcode value
            success = process_item_entry(
                st.session_state.barcode_value, # The barcode used for lookup
                st.session_state.form_item_name_input, 
                st.session_state.form_qty_input, 
                st.session_state.form_cost_input, # Use manually entered/edited cost
                st.session_state.form_selling_input, # Use manually entered/edited selling price
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
                    st.session_state.barcode_value = ""
                    st.session_state.item_name_input = ""
                    st.session_state.supplier_input = ""
                    st.session_state.cost_input = "0.0"
                    st.session_state.selling_input = "0.0"
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

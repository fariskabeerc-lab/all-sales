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
             # Main state (persists barcode/lookup details outside of the main form)
             "barcode_value", "item_name_input", "supplier_input", 
             # Manual Entry temporary keys
             "temp_item_name_manual", "temp_supplier_manual",
             # Lookup state
             "lookup_data", "submitted_feedback", "barcode_found"]: 
    
    if key not in st.session_state:
        if key in ["submitted_items", "submitted_feedback"]:
            st.session_state[key] = []
        elif key == "lookup_data":
            st.session_state[key] = pd.DataFrame()
        elif key == "barcode_found":
            st.session_state[key] = False 
        else:
            st.session_state[key] = ""

# ------------------------------------------------------------------
# --- Helper functions to synchronize manual inputs ---
def update_item_name_state():
    # Updates the main item_name_input state variable from the temp manual input
    st.session_state.item_name_input = st.session_state.temp_item_name_manual

def update_supplier_state():
    # Updates the main supplier_input state variable from the temp manual input
    st.session_state.supplier_input = st.session_state.temp_supplier_manual
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# --- Lookup Logic Function (Callback for Barcode Form) ---
# ------------------------------------------------------------------
def lookup_item_and_update_state():
    barcode = st.session_state.lookup_barcode_input
    
    # Reset lookup states
    st.session_state.lookup_data = pd.DataFrame()
    st.session_state.barcode_value = barcode 
    st.session_state.item_name_input = ""
    st.session_state.supplier_input = ""
    st.session_state.barcode_found = False
    st.session_state.temp_item_name_manual = ""
    st.session_state.temp_supplier_manual = "" 
    
    # Reset all fields *within the item entry form* via a full reset of the form's session keys 
    # to avoid the state exception when using `clear_on_submit=True` on the next submit.
    # NOTE: Since we are using clear_on_submit=True, we rely on the form clear 
    # and only reset the non-form keys here.

    if not barcode:
        st.toast("⚠️ Barcode cleared.", icon="❌")
        st.rerun()
        return

    if not item_data.empty:
        match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
        
        if not match.empty:
            st.session_state.barcode_found = True
            row = match.iloc[0]
            
            # Transfer details to the main form state
            st.session_state.item_name_input = str(row["Item Name"])
            st.session_state.supplier_input = str(row["LP Supplier"])
            
            st.toast("✅ Item found. Details loaded.", icon="🔍")
        else:
            # Barcode not found 
            st.session_state.barcode_found = False 
            st.toast("⚠️ Barcode not found. Please enter item name and supplier manually.", icon="⚠️")
    
    st.rerun() 
# ------------------------------------------------------------------

# -------------------------------------------------
# --- Main Form Submission Handler (Handles Clearing) ---
# FIX: Removed the entire manual reset logic.
# -------------------------------------------------
def process_item_entry(barcode, item_name, qty, cost_str, selling_str, expiry, supplier, remarks, form_type, outlet_name):
    
    # Validation
    if not barcode.strip():
        st.toast("⚠️ Barcode is required before adding.", icon="❌")
        return False
    if not item_name.strip():
        st.toast("⚠️ Item Name is required before adding.", icon="❌")
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

    # --- CLEAR ONLY THE NON-FORM STATE VARIABLES ---
    # The form inputs will be cleared by clear_on_submit=True on the rerun.
    st.session_state.barcode_value = ""          
    st.session_state.item_name_input = ""        
    st.session_state.supplier_input = ""         
    st.session_state.lookup_data = pd.DataFrame() 
    st.session_state.barcode_found = False
    
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
            st.dataframe(st.session_state.lookup_data, use_container_width=True, hide_index=True)
        
        # --- 2b. Manual Entry Fallback ---
        # Show manual entry fields ONLY if a search was done and the barcode was NOT found
        if st.session_state.barcode_value.strip() and not st.session_state.barcode_found:
             st.markdown("### ⚠️ Manual Item Entry (Barcode Not Found)")
             col_manual_name, col_manual_supplier = st.columns(2)
             with col_manual_name:
                 st.text_input(
                     "Item Name (Manual)", 
                     value=st.session_state.item_name_input, 
                     key="temp_item_name_manual", 
                     on_change=update_item_name_state
                 )
             with col_manual_supplier:
                 st.text_input(
                     "Supplier Name (Manual)", 
                     value=st.session_state.supplier_input, 
                     key="temp_supplier_manual", 
                     on_change=update_supplier_state
                 )

        # Separator only if a search has happened
        if st.session_state.barcode_value.strip():
             st.markdown("---") 


        # --- 3. Start of the Main Item Entry Form ---
        # FIX: Set clear_on_submit=True to clear the fields automatically
        with st.form("item_entry_form", clear_on_submit=True): 
            
            # --- Row 1: Qty and Expiry ---
            col1, col2 = st.columns(2)
            with col1:
                # Widgets in a clear_on_submit=True form do not need custom keys unless their value 
                # needs to be accessed/controlled outside the form's submit block.
                qty = st.number_input("Qty [PCS]", min_value=1, value=1)
            with col2:
                if form_type != "Damages":
                    expiry = st.date_input("Expiry Date", datetime.now().date())
                else:
                    expiry = None

            # --- Row 2: Cost, Selling ---
            col5, col6 = st.columns(2)
            with col5:
                cost_str = st.text_input("Cost", value="0.0")
            with col6:
                selling_str = st.text_input("Selling Price", value="0.0")

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
            remarks = st.text_area("Remarks [if any]", value="")

            # Form submission button (only this button adds the item)
            submitted_item = st.form_submit_button(
                "➕ Add to List", 
                type="primary",
            )
            # --- End of the Item Entry Form ---

        # --------------------------------------------------------
        # --- Handle Main Form Submission ONLY on Button Click ---
        # --------------------------------------------------------
        # When clear_on_submit=True, the state values are available in the submit block.
        if submitted_item:
            
            final_item_name = st.session_state.item_name_input
            final_supplier = st.session_state.supplier_input

            if not st.session_state.barcode_value.strip():
                 st.toast("❌ Please enter a Barcode before adding to the list.", icon="❌")
                 # A manual rerun is required here since clear_on_submit already triggered one.
                 st.rerun() 

            success = process_item_entry(
                st.session_state.barcode_value, 
                final_item_name,               
                qty,        # Passed directly from the form widget
                cost_str,   # Passed directly from the form widget
                selling_str,# Passed directly from the form widget
                expiry,     # Passed directly from the form widget
                final_supplier,                
                remarks,    # Passed directly from the form widget
                form_type, 
                outlet_name
            )
            # Success logic is inside process_item_entry, which triggers a final rerun.
            if success:
                 st.rerun()


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
                    st.session_state.barcode_found = False
                    st.session_state.temp_item_name_manual = "" 
                    st.session_state.temp_supplier_manual = "" 
                    st.rerun() 

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

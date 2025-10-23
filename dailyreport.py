import streamlit as st
import pandas as pd
from datetime import date

# --- Configuration & State Initialization ---

# 1. Outlet/Password Configuration
OUTLETS = {
    "Outlet A": "outleta", "Outlet B": "outletb", "Outlet C": "outletc", "Outlet D": "outletd",
    "Outlet E": "outlete", "Outlet F": "outletf", "Outlet G": "outletg", "Outlet H": "outleth",
    "Outlet I": "outleti", "Outlet J": "outletj", "Outlet K": "outletk", "Outlet L": "outletl",
    "Outlet M": "outletm", "Outlet N": "outletn", "Outlet O": "outleto", "Outlet P": "outletp",
}
USERNAME_REQUIRED = "almadina"
FORM_OPTIONS = ["Expiry", "Damages", "Near Expiry"]

# 2. Function to Initialize Session State
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'current_outlet' not in st.session_state:
        st.session_state['current_outlet'] = None
    if 'current_form_data' not in st.session_state:
        st.session_state['current_form_data'] = [] # Accumulates submitted items

# 3. Data Structure for Forms (Common Fields + Specific Remark)
def get_common_fields(remark_label):
    return {
        "Barcode": st.text_input("Barcode", key="barcode"),
        "Product Name": st.text_input("Product Name", key="product_name"),
        "Qty [PCS]": st.number_input("Qty [PCS]", min_value=1, step=1, key="qty"),
        "Cost": st.number_input("Cost", min_value=0.01, format="%.2f", key="cost"),
        "Amount": None, # Will be calculated
        "Expiry Date [dd-mmm-yy]": st.date_input("Expiry Date", min_value=date.today(), key="expiry_date"),
        "Supplier Name": st.text_input("Supplier Name", key="supplier_name"),
        "Remarks": st.text_input(remark_label, key="remarks"),
        "Form Type": st.session_state.get('selected_form', 'N/A')
    }

# --- Authentication Logic ---

def login_form():
    st.subheader("Login 🔑")
    with st.form("login_form"):
        username = st.text_input("Username").lower()
        password = st.text_input("Password (Outlet Name)", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            if username == USERNAME_REQUIRED:
                # Check if password (outlet name) is valid
                if password in OUTLETS.values():
                    outlet_name = [k for k, v in OUTLETS.items() if v == password][0]
                    st.session_state['authenticated'] = True
                    st.session_state['current_outlet'] = outlet_name
                    st.success(f"Successfully logged in as {outlet_name}!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid Outlet Name (Password).")
            else:
                st.error("Invalid Username.")

# --- Main Application (After Login) ---

def main_app():
    # Header showing the current outlet name
    st.header(f"Data Entry Portal 🛒 - {st.session_state['current_outlet']}")
    st.markdown("---")

    # Sidebar for Form Selection
    with st.sidebar:
        st.header("Select Form Type 📋")
        
        # Use a selectbox for a cleaner interface, selecting one at a time
        selected_form = st.selectbox(
            "Choose a Form:",
            FORM_OPTIONS,
            key="selected_form"
        )
        
        # Optional: Logout Button in Sidebar
        if st.button("Logout"):
            st.session_state['authenticated'] = False
            st.session_state['current_outlet'] = None
            st.session_state['current_form_data'] = []
            st.experimental_rerun()
            
    st.subheader(f"{selected_form} Entry Form")
    
    # --- Dynamic Form Generation ---
    remark_label = f"Remarks [for {selected_form}]"
    
    with st.form(key=f'{selected_form}_form', clear_on_submit=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            barcode = st.text_input("Barcode", max_chars=20)
            qty = st.number_input("Qty [PCS]", min_value=1, step=1, value=1)
            expiry_date = st.date_input("Expiry Date [dd-mmm-yy]", min_value=date.today())

        with col2:
            product_name = st.text_input("Product Name")
            cost = st.number_input("Cost", min_value=0.01, format="%.2f")
            supplier_name = st.text_input("Supplier Name")

        # Full-width Remark field
        remarks = st.text_area(remark_label, height=50)

        # Button to submit to the temporary list
        submit_to_list = st.form_submit_button("Submit to List ▶️")

        if submit_to_list:
            if barcode and product_name and qty and cost and supplier_name:
                amount = qty * cost
                
                new_entry = {
                    "Barcode": barcode,
                    "Product Name": product_name,
                    "Qty [PCS]": qty,
                    "Cost": cost,
                    "Amount": amount,
                    "Expiry Date [dd-mmm-yy]": expiry_date.strftime('%d-%b-%y'),
                    "Supplier Name": supplier_name,
                    "Remarks [if any]": remarks,
                    "Form Type": selected_form,
                    "Outlet": st.session_state['current_outlet'] # Crucial for Google Sheet
                }
                
                st.session_state['current_form_data'].append(new_entry)
                st.success("Item added to the submission list!")
                # To clear form fields after submission (requires re-running the script, often done by setting a key or just letting the session state update)
            else:
                st.error("Please fill in all mandatory fields (Barcode, Product Name, Qty, Cost, Supplier Name).")
    
    st.markdown("---")
    
    # --- Accumulated List Display ---
    st.subheader("Accumulated Submission List 📝")

    if st.session_state['current_form_data']:
        # Convert list of dicts to DataFrame for better display
        df = pd.DataFrame(st.session_state['current_form_data'])
        
        # Select and reorder columns for display
        display_cols = [
            "Form Type", "Barcode", "Product Name", "Qty [PCS]", "Cost", "Amount", 
            "Expiry Date [dd-mmm-yy]", "Supplier Name", "Remarks [if any]"
        ]
        
        st.dataframe(df[display_cols], use_container_width=True)
        
        # --- Full Submission Button ---
        st.markdown("<br>", unsafe_allow_html=True) # Adding some space

        if st.button("Full Submit to Google Sheet 🚀", key="full_submit", type="primary"):
            # Placeholder for Google Sheet Integration
            
            # --- GOOGLE SHEETS INTEGRATION LOGIC GOES HERE ---
            # 1. Connect to Google Sheet using API credentials (not possible here)
            # 2. Append st.session_state['current_form_data'] to the sheet.
            
            # Simulated Success/Failure
            if len(st.session_state['current_form_data']) > 0:
                st.balloons()
                st.success(f"Successfully submitted {len(st.session_state['current_form_data'])} items to Google Sheet (Simulation Complete)!")
                
                # IMPORTANT: Clear the temporary list after successful submission
                st.session_state['current_form_data'] = []
                st.dataframe(pd.DataFrame(), use_container_width=True) # Clear the display table
                
            else:
                st.warning("Submission list is empty. Nothing to submit.")
                
    else:
        st.info("No items have been added to the submission list yet.")


# --- Main Application Execution Flow ---

if __name__ == '__main__':
    st.set_page_config(
        page_title="Almadina Stock Data Entry",
        layout="wide", # Uses the full width of the screen, good for tables/mobile
        initial_sidebar_state="expanded" # Sidebar visible by default
    )
    
    # Custom CSS for better mobile/tab display (optional, but good practice)
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        .stTextInput, .stNumberInput, .stDateInput, .stSelectbox {
            margin-bottom: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)

    init_session_state()

    if st.session_state['authenticated']:
        main_app()
    else:
        login_form()

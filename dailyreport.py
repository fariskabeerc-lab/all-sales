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
    # NOTE: You must have an 'alllist.xlsx' file in the same directory for this to work.
    # For a runnable demo without the file, uncomment the lines below and comment out the excel lines.
    # data = {
    #     "Item Bar Code": ["123", "456"], 
    #     "Item Name": ["Apples", "Bananas"], 
    #     "Cost": [1.50, 0.75], 
    #     "Selling": [2.50, 1.25], 
    #     "LP Supplier": ["Supplier A", "Supplier B"]
    # }
    # return pd.DataFrame(data)
    
    file_path = "alllist.xlsx"  # Replace with your Excel path
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
            "cost_input", "selling_input", # NEW: Added for editable cost/selling
            "submitted_feedback"]:
    if key not in st.session_state:
        if key == "submitted_items" or key == "submitted_feedback":
            st.session_state[key] = []
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now().date() # Use date object for st.date_input
        elif key == "cost_input" or key == "selling_input": # Initialize cost/selling to 0.0
             st.session_state[key] = 0.0
        else:
            st.session_state[key] = ""

# ==========================================
# PAGE SELECTION
# ==========================================
if not st.session_state.logged_in:
    # LOGIN PAGE
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
    # Sidebar to select page
    page = st.sidebar.radio("📌 Select Page", ["Outlet Dashboard", "Customer Feedback"])
    
    # The logout button has been removed as requested.

    # ==========================================
    # OUTLET DASHBOARD
    # ==========================================
    if page == "Outlet Dashboard":
        outlet_name = st.session_state.selected_outlet
        st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)

        # FORM TYPE SELECTION
        form_type = st.sidebar.radio(
            "📋 Select Form Type",
            ["Expiry", "Damages", "Near Expiry"]
        )
        st.markdown("---")

        # ==============================
        # FORM INPUTS (Top Row)
        # ==============================
        col1, col2, col3 = st.columns(3)
        with col1:
            # Barcode input and binding
            barcode = st.text_input("Barcode", value=st.session_state.barcode_input, key="db_barcode_input")
            st.session_state.barcode_input = barcode
        with col2:
            qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input, key="db_qty_input")
            st.session_state.qty_input = qty
        with col3:
            if form_type != "Damages":
                expiry = st.date_input("Expiry Date", st.session_state.expiry_input, key="db_expiry_input")
                st.session_state.expiry_input = expiry
            else:
                expiry = None

        # --- AUTO-FILL LOGIC (Only Item Name and Supplier) ---
        if barcode and not item_data.empty:
            match = item_data[item_data["Item Bar Code"].astype(str).str.strip() == str(barcode).strip()]
            if not match.empty:
                # Only update session state for item name and supplier from data
                st.session_state.item_name_input = str(match.iloc[0]["Item Name"])
                st.session_state.supplier_input = str(match.iloc[0]["LP Supplier"])
            else:
                 # If no match, clear the auto-fill fields
                 st.session_state.item_name_input = ""
                 st.session_state.supplier_input = ""
        elif not barcode:
            # If barcode is cleared, clear auto-fill fields
             st.session_state.item_name_input = ""
             st.session_state.supplier_input = ""
        
        # --- INPUT FIELDS USING SESSION STATE (Bottom Row) ---
        col4, col5, col6, col7 = st.columns(4)
        
        # 1. Item Name (Auto-filled, Editable)
        with col4:
            item_name = st.text_input("Item Name", 
                                      value=st.session_state.item_name_input, 
                                      key="db_item_name_input_key")
            st.session_state.item_name_input = item_name # Capture user manual edits
            
        # 2. Cost (Now Editable)
        with col5:
            cost_str = st.text_input("Cost", 
                                     value=str(st.session_state.cost_input), 
                                     key="db_cost_input_key")
            try:
                # Convert string input to float for calculation/storage
                cost = float(cost_str) if cost_str else 0.0
                st.session_state.cost_input = cost
            except ValueError:
                cost = 0.0
                st.error("Invalid Cost value. Using 0.0 for calculation.")
                
        # 3. Selling Price (Now Editable)
        with col6:
            selling_str = st.text_input("Selling Price", 
                                        value=str(st.session_state.selling_input), 
                                        key="db_selling_input_key")
            try:
                # Convert string input to float for calculation/storage
                selling = float(selling_str) if selling_str else 0.0
                st.session_state.selling_input = selling
            except ValueError:
                selling = 0.0
                st.error("Invalid Selling Price value. Using 0.0 for calculation.")
                
        # 4. Supplier Name (Auto-filled, Editable)
        with col7:
            supplier = st.text_input("Supplier Name", 
                                     value=st.session_state.supplier_input,
                                     key="db_supplier_input_key")
            st.session_state.supplier_input = supplier # Capture user manual edits

        # Recalculate GP based on the user-edited/default cost/selling values
        gp = ((selling - cost) / cost * 100) if cost and cost != 0 else 0
        st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

        remarks = st.text_area("Remarks [if any]", value=st.session_state.remarks_input)
        st.session_state.remarks_input = remarks

        # ==============================
        # ADD TO LIST BUTTON
        # ==============================
        if st.button("➕ Add to List"):
            # Use the latest values from the inputs
            if barcode and item_name:
                # Ensure expiry is correctly handled for display
                expiry_display = expiry.strftime("%d-%b-%y") if expiry else ""
                
                st.session_state.submitted_items.append({
                    "Form Type": form_type,
                    "Barcode": barcode,
                    "Item Name": item_name,
                    "Qty": qty,
                    "Cost": round(cost, 2), # Use user-entered cost
                    "Selling": round(selling, 2), # Use user-entered selling
                    "Amount": round(cost * qty, 2),
                    "GP%": round(gp, 2),
                    "Expiry": expiry_display,
                    "Supplier": supplier,
                    "Remarks": remarks,
                    "Outlet": outlet_name
                })
                st.success("✅ Added to list successfully!")
                
                # --- CLEAR ALL FORM INPUTS IN SESSION STATE ---
                st.session_state.barcode_input = ""
                st.session_state.qty_input = 1
                st.session_state.expiry_input = datetime.now().date()
                st.session_state.remarks_input = ""
                st.session_state.item_name_input = ""
                st.session_state.supplier_input = ""
                st.session_state.cost_input = 0.0    # CLEARED/RESET
                st.session_state.selling_input = 0.0 # CLEARED/RESET
                
                st.rerun() 
            else:
                st.warning("⚠️ Fill barcode and item name before adding.")

        # ==============================
        # DISPLAY SUBMITTED ITEMS
        # ==============================
        if st.session_state.submitted_items:
            st.markdown("### 🧾 Items Added")
            df = pd.DataFrame(st.session_state.submitted_items)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col_submit, col_delete = st.columns([1, 1])
            with col_submit:
                if st.button("📤 Submit All"):
                    # Submit logic here (e.g., Google Sheets)
                    st.success(f"✅ All {len(st.session_state.submitted_items)} items submitted for {outlet_name} (demo)")
                    st.session_state.submitted_items = []
                    st.rerun() 

            with col_delete:
                # Create options list for deletion
                options = [f"{i+1}. {item['Item Name']} ({item['Qty']} pcs)" for i, item in enumerate(st.session_state.submitted_items)]
                
                to_delete = st.selectbox(
                    "Select Item to Delete",
                    options=options
                )
                
                if st.button("❌ Delete Selected"):
                    # Extract the index from the selected string (e.g., "1. Apples (1 pcs)" -> 0)
                    index = int(to_delete.split(".")[0]) - 1
                    
                    if 0 <= index < len(st.session_state.submitted_items):
                        st.session_state.submitted_items.pop(index)
                        st.success("✅ Item removed")
                        st.rerun() 
                    else:
                        st.warning("Could not find the item to delete.")


    # ==========================================
    # CUSTOMER FEEDBACK PAGE
    # ==========================================
    else:
        outlet_name = st.session_state.selected_outlet
        st.title("📝 Customer Feedback Form")
        st.markdown(f"Submitting feedback for **{outlet_name}**")
        st.markdown("---")

        with st.form("feedback_form", clear_on_submit=True): # FIX: Added clear_on_submit=True
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
                    "Outlet": outlet_name, # NEW: Added Outlet name
                    "Feedback": feedback,
                    "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                # UPDATED: Confirm form cleared
                st.success("✅ Feedback submitted successfully! The form has been cleared.")
            else:
                # UPDATED: More specific error message
                st.error("⚠️ Submission failed. Please provide your **Customer Name** and **Feedback**.")

        # Display all feedback
        if st.session_state.submitted_feedback:
            st.markdown("### 🗂 Recent Customer Feedback")
            
            # Convert to DataFrame and reverse order to show latest first
            df = pd.DataFrame(st.session_state.submitted_feedback)
            st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
            
            # Clear all button
            if st.button("🗑 Clear All Feedback Records", type="primary"):
                st.session_state.submitted_feedback = []
                st.rerun()

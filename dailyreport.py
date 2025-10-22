import streamlit as st
import pandas as pd
from datetime import date

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="Outlet Management Dashboard", layout="wide")

# ============================================
# USER SETUP
# ============================================
managers = {
    "salman": "12345",
    "manager2": "managerpass2",
}

outlets = {
    "safa": "123123",
    "fida": "12341234",
    "outlet3": "pass3",
    "outlet4": "pass4",
}

all_users = {**managers, **outlets}

# ============================================
# SESSION STATE INIT
# ============================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "product_data" not in st.session_state:
    st.session_state.product_data = []          # Permanent outlet data
if "temp_entries" not in st.session_state:
    st.session_state.temp_entries = []          # Temporary outlet entries
if "checklist_data" not in st.session_state:
    st.session_state.checklist_data = []        # Manager checklist data

# ============================================
# LOGIN PAGE
# ============================================
if not st.session_state.authenticated:
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in all_users and all_users[username] == password:
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.user_role = "manager" if username in managers else "outlet"
            st.success(f"✅ Welcome {username}!")
        else:
            st.error("❌ Invalid username or password")

# ============================================
# MAIN DASHBOARD
# ============================================
else:
    st.title(f"🏬 Welcome {st.session_state.user} ({st.session_state.user_role})")

    # ----------------------------------------------------------
    # OUTLET DASHBOARD
    # ----------------------------------------------------------
    if st.session_state.user_role == "outlet":

        form_type = st.sidebar.selectbox(
            "Select Form Type",
            ["Near Expiry", "Damaged", "Other"]
        )

        st.subheader(f"📋 {form_type} Form")

        # -----------------------------
        # FORM FOR OUTLET ENTRY
        # -----------------------------
        with st.form("outlet_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                barcode = st.text_input("Barcode")
                product_name = st.text_input("Product Name")
                qty = st.number_input("Qty [PCS]", min_value=0)
                cost = st.number_input("Cost", min_value=0.0, format="%.2f")

            with col2:
                amount = st.number_input("Amount", min_value=0.0, format="%.2f")
                expiry = st.date_input("Expiry Date", value=date.today())
                supplier = st.text_input("Supplier Name")
                remarks = st.text_area("Remarks [if any]")

            submitted = st.form_submit_button("➕ Add Entry")
            if submitted:
                st.session_state.temp_entries.append({
                    "Form Type": form_type,
                    "Barcode": barcode,
                    "Product Name": product_name,
                    "Qty": qty,
                    "Cost": cost,
                    "Amount": amount,
                    "Expiry Date": expiry,
                    "Supplier": supplier,
                    "Remarks": remarks
                })
                st.success("✅ Entry added to the table below!")

        # -----------------------------
        # TEMPORARY ENTRIES TABLE
        # -----------------------------
        if st.session_state.temp_entries:
            st.subheader("📝 Current Session Entries (Pending Submission)")
            temp_df = pd.DataFrame(st.session_state.temp_entries)
            st.dataframe(temp_df, use_container_width=True)

            if st.button("📤 Submit All Data"):
                for entry in st.session_state.temp_entries:
                    entry["Outlet"] = st.session_state.user
                    st.session_state.product_data.append(entry)
                st.session_state.temp_entries = []
                st.success("✅ All entries submitted successfully!")

        # -----------------------------
        # SHOW ALL PREVIOUS SUBMISSIONS
        # -----------------------------
        outlet_entries = [e for e in st.session_state.product_data if e["Outlet"] == st.session_state.user]
        if outlet_entries:
            st.subheader("📊 Your Submitted Entries")
            st.dataframe(pd.DataFrame(outlet_entries), use_container_width=True)
        else:
            st.info("No previous entries yet.")

    # ----------------------------------------------------------
    # MANAGER DASHBOARD
    # ----------------------------------------------------------
    elif st.session_state.user_role == "manager":

        manager_option = st.sidebar.radio(
            "Select Option",
            ["Outlet Checklist Form", "Previous Checklists"]
        )

        if manager_option == "Outlet Checklist Form":
            st.subheader("📋 Outlet Visit Checklist Form")

            with st.form("checklist_form", clear_on_submit=True):
                outlet_name = st.text_input("Outlet Name")
                buyer_name = st.text_input("Buyer Name")
                visit_date = st.date_input("Visit Date", value=date.today())
                managers_present = st.text_input("Managers Present")

                checklist_items = [
                    "Store Entrance area clean and tidy",
                    "Shopping baskets/trolleys available & in good condition",
                    "Store floors clean and dry",
                    "Shelves dust-free and organized",
                    "No stock or blockages in aisles",
                    "All staff in proper uniform and grooming",
                    "Staff awareness of promotions/products",
                    "Promotional tags and displays correctly placed",
                    "Promo stock available and refilled timely",
                    "Shelve tags properly placed",
                    "Stock neatly arranged (facing and stacking)",
                    "Expired items removed from shelves",
                    "Check for overstocked or understocked products",
                    "Verify stock levels of fast-moving items",
                    "Identify slow-moving or obsolete items",
                    "Review last purchase orders and delivery timelines",
                    "Note any frequent product requests not currently stocked",
                    "Check for counterfeit or unapproved brands",
                    "Note competitor products or promotions seen in the area",
                    "Quality of fruits and vegetables (fresh, no damage)",
                    "Check for unauthorized purchases or wastage",
                    "Validate consistency in product standards across outlets",
                    "Gather feedback from outlet managers on supply issues",
                    "Review communication between purchasing and outlet staff",
                    "Review expiry management and disposal records",
                    "Loyalty cards/offers being promoted by staff",
                    "Discuss vendor performance concerns",
                    "LC products out of stock",
                    "LC products not displayed properly"
                ]

                checklist_responses = {}
                for item in checklist_items:
                    checklist_responses[item] = st.selectbox(item, ["OK", "Not OK", "Bad"], key=item)

                additional_comments = st.text_area("Additional Comments")

                submitted_chk = st.form_submit_button("✅ Submit Checklist")
                if submitted_chk:
                    st.session_state.checklist_data.append({
                        "Outlet Name": outlet_name,
                        "Buyer Name": buyer_name,
                        "Date": visit_date,
                        "Managers Present": managers_present,
                        "Responses": checklist_responses,
                        "Additional Comments": additional_comments
                    })
                    st.success("✅ Checklist submitted successfully!")

        elif manager_option == "Previous Checklists":
            st.subheader("📊 All Submitted Checklists")
            if st.session_state.checklist_data:
                df_check = pd.DataFrame([{
                    "Outlet": d["Outlet Name"],
                    "Date": d["Date"],
                    "Managers Present": d["Managers Present"]
                } for d in st.session_state.checklist_data])
                st.dataframe(df_check, use_container_width=True)
            else:
                st.info("No checklist submissions yet.")

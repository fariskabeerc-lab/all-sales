import streamlit as st
import pandas as pd
from datetime import date

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Outlet Management Dashboard", layout="wide")

# ==============================
# USERS SETUP
# ==============================
# Managers credentials
managers = {
    "salman": "12345",
    "manager2": "managerpass2",
}

# Outlets credentials
outlets = {
    "safa": "123123",
    "fida": "12341234",
    "outlet3": "pass3",
    "outlet4": "pass4",
}

# Merge all users for login
all_users = {**managers, **outlets}

# ==============================
# SESSION STATE INIT
# ==============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None  # "manager" or "outlet"

if "product_data" not in st.session_state:
    st.session_state.product_data = []

if "checklist_data" not in st.session_state:
    st.session_state.checklist_data = []

# ==============================
# LOGIN
# ==============================
if not st.session_state.authenticated:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in all_users and all_users[username] == password:
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.user_role = "manager" if username in managers else "outlet"
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password")
else:
    st.title(f"🏬 Welcome {st.session_state.user} ({st.session_state.user_role})")

    # ==============================
    # MANAGER VIEW
    # ==============================
    if st.session_state.user_role == "manager":
        st.subheader("📋 Product Form")
        form_type = st.selectbox("Select Form Type", ["Near Expiry", "Damaged", "Other"])

        # Product form
        with st.form("product_form", clear_on_submit=True):
            barcode = st.text_input("Barcode")
            product_name = st.text_input("Product Name")
            qty = st.number_input("Qty [PCS]", min_value=0)
            cost = st.number_input("Cost", min_value=0.0, format="%.2f")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            expiry = st.date_input("Expiry Date", value=date.today())
            supplier = st.text_input("Supplier Name")
            remarks = st.text_area("Remarks [if any]")

            submitted = st.form_submit_button("Add Product Entry")
            if submitted:
                st.session_state.product_data.append({
                    "Outlet": st.session_state.user,
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
                st.success("✅ Product entry added!")

        # Show all product entries
        if st.session_state.product_data:
            st.subheader("📊 Product Entries (Before Final Submission)")
            st.dataframe(pd.DataFrame(st.session_state.product_data))
            if st.button("Submit All Product Entries (Demo)"):
                st.success(f"✅ {len(st.session_state.product_data)} entries submitted to GitHub (Demo)!")
                st.session_state.product_data = []

        # ==============================
        # Outlet Visit Checklist Form
        # ==============================
        st.subheader("📋 Outlet Visit Checklist Form")
        with st.form("checklist_form", clear_on_submit=True):
            outlet_name = st.text_input("Outlet Name")
            buyer_name = st.text_input("Buyer Name")
            visit_date = st.date_input("Date", value=date.today())
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
                checklist_responses[item] = st.selectbox(item, ["OK", "Not OK"], key=f"{item}_chk")

            additional_comments = st.text_area("Additional Comments")

            submitted_chk = st.form_submit_button("Submit Checklist")
            if submitted_chk:
                st.session_state.checklist_data.append({
                    "Outlet Name": outlet_name,
                    "Buyer Name": buyer_name,
                    "Date": visit_date,
                    "Managers Present": managers_present,
                    "Responses": checklist_responses,
                    "Additional Comments": additional_comments
                })
                st.success("✅ Checklist submitted!")

        # Show previous checklists
        if st.session_state.checklist_data:
            st.subheader("📊 All Checklist Entries (Demo)")
            st.dataframe(pd.DataFrame([{
                "Outlet": d["Outlet Name"],
                "Date": d["Date"],
                "Managers Present": d["Managers Present"]
            } for d in st.session_state.checklist_data]))
            if st.button("Submit All Checklists (Demo)"):
                st.success(f"✅ {len(st.session_state.checklist_data)} checklists submitted to GitHub (Demo)!")
                st.session_state.checklist_data = []

    # ==============================
    # OUTLET VIEW
    # ==============================
    else:
        st.subheader("📄 Your Product Entries")
        outlet_products = [entry for entry in st.session_state.product_data
                           if entry["Outlet"].lower() == st.session_state.user.lower()]
        if outlet_products:
            st.dataframe(pd.DataFrame(outlet_products))
        else:
            st.info("No product entries yet.")

        st.subheader("📄 Your Checklist Submissions")
        outlet_checklists = [entry for entry in st.session_state.checklist_data
                             if entry["Outlet Name"].lower() == st.session_state.user.lower()]
        if outlet_checklists:
            for i, entry in enumerate(outlet_checklists, 1):
                st.markdown(f"### Checklist Submission {i}")
                st.text(f"Buyer: {entry['Buyer Name']}")
                st.text(f"Date: {entry['Date']}")
                st.text(f"Managers Present: {entry['Managers Present']}")
                df = pd.DataFrame(entry['Responses'], index=[0]).T
                df.columns = ["Status"]
                st.table(df)
                st.markdown("**Additional Comments:**")
                st.text(entry['Additional Comments'])
        else:
            st.info("No checklist submissions yet.")

import streamlit as st
import pandas as pd
from datetime import datetime, date

# ======================================
# PAGE CONFIGURATION
# ======================================
st.set_page_config(page_title="Outlet Management Dashboard", layout="wide")
st.title("🏪 Outlet Management Dashboard")

# ======================================
# USER LOGIN SIMULATION
# ======================================
managers = {"salman": "12345", "manager2": "managerpass2"}
outlets = {"safa": "123123", "fida": "12341234"}
all_users = {**managers, **outlets}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if not st.session_state.authenticated:
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in all_users and all_users[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = "manager" if username in managers else "outlet"
            st.success(f"✅ Welcome {username} ({st.session_state.user_role})")
        else:
            st.error("❌ Invalid username or password")
    st.stop()

username = st.session_state.username
role = st.session_state.user_role

# ======================================
# SIDEBAR NAVIGATION
# ======================================
st.sidebar.title("📋 Navigation")
if role == "outlet":
    menu = st.sidebar.radio("Select an Option", ["Expiry Entry", "Damage Entry"])
else:
    menu = st.sidebar.radio("Select an Option", ["Outlet Checklist Form", "Previous Checklists"])

# ======================================
# DATA INITIALIZATION
# ======================================
expiry_columns = [
    "Date", "Username", "Outlet", "Item Code", "Item Name", "Brand", "Category",
    "Quantity", "Unit", "Batch No", "Expiry Date", "Reason/Remarks"
]
damage_columns = [
    "Date", "Username", "Outlet", "Item Code", "Item Name", "Brand", "Category",
    "Quantity", "Unit", "Batch No", "Reason/Remarks"
]
checklist_columns = [
    "Date", "Username", "Outlet Name", "Buyer Name", "Managers Present", "Responses", "Additional Comments"
]

if "expiry_data" not in st.session_state:
    st.session_state["expiry_data"] = pd.DataFrame(columns=expiry_columns)
if "damage_data" not in st.session_state:
    st.session_state["damage_data"] = pd.DataFrame(columns=damage_columns)
if "checklist_data" not in st.session_state:
    st.session_state["checklist_data"] = pd.DataFrame(columns=checklist_columns)

# ======================================
# OUTLET ENTRY FORM (Expiry/Damage)
# ======================================
def outlet_entry_form(data_key, title):
    st.subheader(f"{title} Entry Form")

    with st.form(f"{data_key}_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            outlet = st.text_input("🏪 Outlet Name", value=username)
            item_code = st.text_input("🔢 Item Code")
            brand = st.text_input("🏷️ Brand Name")
        with col2:
            item_name = st.text_input("🧾 Item Name")
            category = st.text_input("📦 Category")
            batch_no = st.text_input("🔖 Batch No")
        with col3:
            quantity = st.number_input("🔢 Quantity", min_value=1, step=1)
            unit = st.selectbox("⚖️ Unit", ["PCS", "Box", "Kg", "Litre", "Pack"])
            expiry_date = None
            if title == "Expiry":
                expiry_date = st.date_input("📅 Expiry Date")

        reason = st.text_area("📝 Reason / Remarks")

        submitted = st.form_submit_button("Add Entry")

        if submitted:
            if item_name.strip() == "" or reason.strip() == "":
                st.warning("⚠️ Please fill all required fields before submitting.")
            else:
                new_entry = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Username": username,
                    "Outlet": outlet,
                    "Item Code": item_code,
                    "Item Name": item_name,
                    "Brand": brand,
                    "Category": category,
                    "Quantity": quantity,
                    "Unit": unit,
                    "Batch No": batch_no,
                    "Expiry Date": expiry_date.strftime("%Y-%m-%d") if expiry_date else "",
                    "Reason/Remarks": reason,
                }
                st.session_state[data_key] = pd.concat(
                    [st.session_state[data_key], pd.DataFrame([new_entry])],
                    ignore_index=True,
                )
                st.success("✅ Entry added successfully!")

    if not st.session_state[data_key].empty:
        st.write("### 🧾 Current Entries")
        st.dataframe(st.session_state[data_key], use_container_width=True)

        if st.button("📤 Submit All Data", key=f"{data_key}_submit"):
            filename = f"{data_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            st.session_state[data_key].to_excel(filename, index=False)
            st.success(f"✅ All data saved to `{filename}` successfully!")
            st.session_state[data_key] = pd.DataFrame(columns=st.session_state[data_key].columns)

# ======================================
# MANAGER CHECKLIST FORM
# ======================================
def manager_checklist_form():
    st.subheader("📋 Outlet Visit Checklist Form")

    with st.form("checklist_form", clear_on_submit=True):
        outlet_name = st.text_input("🏪 Outlet Name")
        buyer_name = st.text_input("👤 Buyer Name")
        visit_date = st.date_input("📅 Visit Date", value=date.today())
        managers_present = st.text_input("👥 Managers Present")

        st.divider()
        st.markdown("### ✅ Checklist Items")

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
            "LC products not displayed properly",
        ]

        checklist_responses = {}
        for item in checklist_items:
            checklist_responses[item] = st.selectbox(item, ["OK", "Not OK", "Bad"], key=f"{item}_chk")

        additional_comments = st.text_area("🗒️ Additional Comments")

        submitted_chk = st.form_submit_button("Submit Checklist")
        if submitted_chk:
            new_check = {
                "Date": visit_date.strftime("%Y-%m-%d"),
                "Username": username,
                "Outlet Name": outlet_name,
                "Buyer Name": buyer_name,
                "Managers Present": managers_present,
                "Responses": checklist_responses,
                "Additional Comments": additional_comments,
            }
            st.session_state["checklist_data"] = pd.concat(
                [st.session_state["checklist_data"], pd.DataFrame([new_check])],
                ignore_index=True,
            )
            st.success("✅ Checklist submitted successfully!")

# ======================================
# MANAGER PREVIOUS CHECKLISTS
# ======================================
def view_previous_checklists():
    st.subheader("📊 Previous Checklists")
    if not st.session_state["checklist_data"].empty:
        df_simple = pd.DataFrame([{
            "Date": row["Date"],
            "Outlet": row["Outlet Name"],
            "Buyer": row["Buyer Name"],
            "Managers Present": row["Managers Present"]
        } for _, row in st.session_state["checklist_data"].iterrows()])
        st.dataframe(df_simple, use_container_width=True)

        if st.button("📤 Export All Checklists"):
            filename = f"checklists_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            st.session_state["checklist_data"].to_excel(filename, index=False)
            st.success(f"✅ All checklist data saved to `{filename}` successfully!")
    else:
        st.info("No checklist data available yet.")

# ======================================
# PAGE LOGIC
# ======================================
if role == "outlet":
    if menu == "Expiry Entry":
        outlet_entry_form("expiry_data", "Expiry")
    elif menu == "Damage Entry":
        outlet_entry_form("damage_data", "Damage")

elif role == "manager":
    if menu == "Outlet Checklist Form":
        manager_checklist_form()
    elif menu == "Previous Checklists":
        view_previous_checklists()

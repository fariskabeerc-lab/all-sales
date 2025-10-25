import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet & Manager Dashboard", layout="wide")

# ==========================================
# LOAD ITEM DATA
# ==========================================
@st.cache_data
def load_item_data():
    file_path = "alllist.xlsx"  # Replace with your Excel path
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    return df

item_data = load_item_data()

# ==========================================
# LOGIN SYSTEM
# ==========================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida", "Hadeqat",
    "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan", "Superstore",
    "Tay Tay", "Safa oudmehta", "Port saeed"
]

users = {
    "almadina": {"password": "123123", "role": "outlet"},
    "manager1": {"password": "1234512345", "role": "manager"},
    "manager2": {"password": "1234512345", "role": "manager"},
    "manager3": {"password": "1234512345", "role": "manager"}
}

# Initialize session state
for key in ["logged_in", "user_role", "selected_outlet", "submitted_items"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "submitted_items" else []

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username", placeholder="Enter username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and pwd == users[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.user_role = users[username]["role"]
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ==========================================
# OUTLET DASHBOARD
# ==========================================
elif st.session_state.user_role == "outlet":
    outlet_name = st.selectbox("🏪 Select Your Outlet", outlets)
    st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)
    st.sidebar.success("Logged in as Outlet")

    form_type = st.sidebar.radio("📋 Select Form Type", ["Expiry", "Damages", "Near Expiry"])
    st.markdown("---")

    # FORM INPUTS
    col1, col2, col3 = st.columns(3)
    with col1:
        barcode = st.text_input("Barcode")
    with col2:
        qty = st.number_input("Qty [PCS]", min_value=1, value=1)
    with col3:
        expiry = st.date_input("Expiry Date") if form_type != "Damages" else None

    # Auto-fill item details
    item_name, cost, selling, supplier = "", 0.0, 0.0, ""
    if barcode:
        match = item_data[item_data["Item Bar Code"].astype(str) == str(barcode)]
        if not match.empty:
            item_name = str(match.iloc[0]["Item Name"])
            cost = float(match.iloc[0]["Cost"])
            selling = float(match.iloc[0]["Selling"])
            supplier = str(match.iloc[0]["LP Supplier"])

    gp = ((selling - cost) / cost * 100) if cost else 0
    st.info(f"💹 GP%: {gp:.2f}%")

    remarks = st.text_area("Remarks [if any]")

    if st.button("➕ Add to List"):
        if barcode and item_name:
            st.session_state.submitted_items.append({
                "Form Type": form_type,
                "Barcode": barcode,
                "Item Name": item_name,
                "Qty": qty,
                "Cost": cost,
                "Selling": selling,
                "Amount": cost * qty,
                "GP%": round(gp, 2),
                "Expiry": expiry.strftime("%d-%b-%y") if expiry else "",
                "Supplier": supplier,
                "Remarks": remarks,
                "Outlet": outlet_name
            })
            st.success("✅ Added successfully!")
        else:
            st.warning("⚠️ Enter barcode and item name")

    # DISPLAY TABLE
    if st.session_state.submitted_items:
        st.markdown("### 🧾 Items Added")
        df = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df, use_container_width=True)

        col_submit, col_delete = st.columns([1, 1])
        with col_submit:
            if st.button("📤 Submit All"):
                st.success("✅ All data submitted (demo)")
                st.session_state.submitted_items = []
        with col_delete:
            if st.session_state.submitted_items:
                to_delete = st.selectbox(
                    "Select Item to Delete",
                    options=[f"{i+1}. {item['Item Name']}" for i, item in enumerate(st.session_state.submitted_items)]
                )
                if st.button("❌ Delete Selected"):
                    index = int(to_delete.split(".")[0]) - 1
                    st.session_state.submitted_items.pop(index)
                    st.success("✅ Item removed")
                    st.experimental_rerun()

# ==========================================
# MANAGER DASHBOARD
# ==========================================
elif st.session_state.user_role == "manager":
    st.sidebar.success("Logged in as Manager")

    st.title("🧾 Outlet Visit Form - Central Buyer")
    outlet_selected = st.selectbox("🏪 Outlet Name", outlets)
    buyer_name = st.text_input("Buyer Name")
    visit_date = st.date_input("Date", datetime.today())
    managers_present = st.text_input("Managers Present")

    st.markdown("### ✅ Store Checklist")
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

    checklist_df = pd.DataFrame({
        "Checklist Item": checklist_items,
        "Status (OK/Not OK)": ["OK" for _ in checklist_items]
    })

    edited_df = st.data_editor(checklist_df, use_container_width=True, num_rows="fixed")

    additional_comments = st.text_area("🗒️ Additional Comments")

    if st.button("📤 Submit Visit Report"):
        st.success("✅ Report submitted successfully (demo)")
        st.write("**Outlet:**", outlet_selected)
        st.write("**Buyer:**", buyer_name)
        st.write("**Managers Present:**", managers_present)
        st.write("**Date:**", visit_date.strftime("%d-%b-%Y"))
        st.dataframe(edited_df)
        st.write("**Comments:**", additional_comments)

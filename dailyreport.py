import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Customer / Outlet / Manager Demo", layout="wide")

# ==========================================
# LOAD ITEM DATA (for auto-fill in outlet form)
# ==========================================
@st.cache_data
def load_item_data():
    file_path = "alllist.xlsx"  # Replace with your Excel path
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    return df

item_data = load_item_data()

# ==========================================
# OUTLETS & MANAGERS
# ==========================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida",
    "Hadeqat", "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan",
    "Superstore", "Tay Tay", "Safa oudmehta", "Port saeed"
]
managers = ["Manager 1", "Manager 2", "Manager 3"]
password_outlet = "123123"
password_manager = "1234512345"

# ==========================================
# SESSION VARIABLES
# ==========================================
for key in ["selected_outlet_customer", "customer_feedback", 
            "logged_in", "role", "selected_outlet", 
            "submitted_items", "manager_form"]:
    if key not in st.session_state:
        if key in ["submitted_items", "manager_form"]:
            st.session_state[key] = []
        elif key == "customer_feedback":
            st.session_state[key] = ""
        else:
            st.session_state[key] = None

# ==========================================
# TOP-RIGHT LOGIN BUTTON
# ==========================================
with st.container():
    st.markdown(
        """
        <style>
        .login-button {position: fixed; top: 10px; right: 20px; z-index:100;}
        </style>
        """, unsafe_allow_html=True
    )
    if st.button("🔐 Login", key="login_button"):
        st.session_state.show_login = True

# ==========================================
# LOGIN PAGE
# ==========================================
if "show_login" in st.session_state and st.session_state.show_login:
    st.session_state.show_login = False
    st.experimental_rerun()

if st.session_state.logged_in is None:
    st.session_state.logged_in = False

if not st.session_state.logged_in and st.session_state.selected_outlet_customer:
    st.title("🔐 Login Page")
    role = st.radio("Login As:", ["Outlet", "Manager"])
    username = st.text_input("Username / Name")

    if role == "Outlet":
        outlet_login = st.selectbox("Select Outlet", outlets)
        pwd = st.text_input("Password", type="password")
        if st.button("Login Outlet"):
            if username == "almadina" and pwd == password_outlet:
                st.session_state.logged_in = True
                st.session_state.role = "Outlet"
                st.session_state.selected_outlet = outlet_login
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password")

    elif role == "Manager":
        manager_login = st.selectbox("Select Manager", managers)
        pwd = st.text_input("Password", type="password")
        if st.button("Login Manager"):
            if pwd == password_manager:
                st.session_state.logged_in = True
                st.session_state.role = "Manager"
                st.session_state.selected_outlet = manager_login
                st.experimental_rerun()
            else:
                st.error("❌ Invalid password")

# ==========================================
# CUSTOMER INTERFACE
# ==========================================
if not st.session_state.selected_outlet_customer:
    st.title("🏪 Select Your Outlet")
    outlet_choice = st.selectbox("Select your outlet", outlets)
    if st.button("Continue as Customer"):
        st.session_state.selected_outlet_customer = outlet_choice
        st.experimental_rerun()

elif st.session_state.selected_outlet_customer and not st.session_state.logged_in:
    st.markdown(f"### Customer Interface - Outlet: **{st.session_state.selected_outlet_customer}**")
    feedback = st.text_area("Your Feedback / Message")
    if st.button("Submit Feedback"):
        if feedback:
            st.success("✅ Feedback submitted (demo)")
            st.session_state.customer_feedback = ""
        else:
            st.warning("⚠️ Please enter feedback")

# ==========================================
# OUTLET DASHBOARD
# ==========================================
if st.session_state.logged_in and st.session_state.role == "Outlet":
    outlet_name = st.session_state.selected_outlet
    st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)

    # FORM TYPE
    form_type = st.sidebar.radio("📋 Select Form Type", ["Expiry", "Damages", "Near Expiry"])
    st.markdown("---")

    # INPUTS
    col1, col2, col3 = st.columns(3)
    with col1:
        barcode = st.text_input("Barcode")
    with col2:
        qty = st.number_input("Qty [PCS]", min_value=1, value=1)
    with col3:
        expiry = None
        if form_type != "Damages":
            expiry = st.date_input("Expiry Date", datetime.now())

    # AUTO-FILL
    item_name, cost, selling, supplier = "", 0.0, 0.0, ""
    if barcode:
        match = item_data[item_data["Item Bar Code"].astype(str) == str(barcode)]
        if not match.empty:
            item_name = str(match.iloc[0]["Item Name"])
            cost = float(match.iloc[0]["Cost"])
            selling = float(match.iloc[0]["Selling"])
            supplier = str(match.iloc[0]["LP Supplier"])

    col4, col5, col6, col7 = st.columns(4)
    with col4:
        item_name = st.text_input("Item Name", value=item_name)
    with col5:
        st.number_input("Cost", value=cost, disabled=True)
    with col6:
        st.number_input("Selling Price", value=selling, disabled=True)
    with col7:
        supplier = st.text_input("Supplier Name", value=supplier)

    gp = ((selling - cost) / cost * 100) if cost else 0
    st.info(f"💹 **GP% (Profit Margin)**: {gp:.2f}%")

    remarks = st.text_area("Remarks [if any]")

    # ADD TO LIST
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
            st.success("✅ Added to list successfully!")
            # CLEAR FORM
            st.experimental_rerun()
        else:
            st.warning("⚠️ Fill barcode and item before adding.")

    # SHOW ITEMS
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
            to_delete = st.selectbox(
                "Select Item to Delete",
                options=[f"{i+1}. {item['Item Name']}" for i, item in enumerate(st.session_state.submitted_items)]
            )
            if st.button("❌ Delete Selected"):
                index = int(to_delete.split(".")[0]) - 1
                st.session_state.submitted_items.pop(index)
                st.success("✅ Item removed")
                st.experimental_rerun()

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# ==========================================
# MANAGER DASHBOARD
# ==========================================
if st.session_state.logged_in and st.session_state.role == "Manager":
    st.markdown("<h2 style='text-align:center;'>🧍 Manager Outlet Visit Checklist</h2>", unsafe_allow_html=True)

    outlet_selected = st.selectbox("Select Outlet", outlets)
    buyer_name = st.text_input("Buyer Name")
    visit_date = st.date_input("Date", datetime.now())
    managers_present = st.text_input("Managers Present")

    st.markdown("---")
    st.markdown("### ✅ Checklist")

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

    checklist_results = {}
    for item in checklist_items:
        status = st.radio(item, ["OK", "Not OK"], horizontal=True, key=item)
        checklist_results[item] = status

    st.markdown("---")
    additional_comments = st.text_area("📝 Additional Comments")

    if st.button("📤 Submit Checklist"):
        record = {
            "Outlet Name": outlet_selected,
            "Buyer Name": buyer_name,
            "Date": visit_date.strftime("%d-%b-%Y"),
            "Managers Present": managers_present,
            "Checklist": checklist_results,
            "Comments": additional_comments
        }
        st.session_state.manager_form.append(record)
        st.success("✅ Checklist submitted successfully (demo)")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

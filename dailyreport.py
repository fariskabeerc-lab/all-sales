import streamlit as st
import pandas as pd
from datetime import datetime

# =============================
# PAGE CONFIGURATION
# =============================
st.set_page_config(page_title="Expiry / Damages / Near-Expiry Demo", layout="wide")

# =============================
# INITIALIZE SESSION STATE
# =============================
def init_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "outlet" not in st.session_state:
        st.session_state.outlet = ""
    if "pending_items" not in st.session_state:
        st.session_state.pending_items = []
    if "submitted_items" not in st.session_state:
        st.session_state.submitted_items = []

init_state()

OUTLETS = [
    "Outlet A", "Outlet B", "Outlet C", "Outlet D",
    "Outlet E", "Outlet F", "Outlet G", "Outlet H",
    "Outlet I", "Outlet J", "Outlet K", "Outlet L",
    "Outlet M", "Outlet N", "Outlet O", "Outlet P",
]

FORMS = ["Expiry", "Damages", "Near Expiry", "Other"]

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.logged_in:
    st.markdown("## 🔐 Login")

    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")
        with col3:
            outlet_select = st.selectbox("Select your Outlet", OUTLETS)

        submitted = st.form_submit_button("Login")

    if submitted:
        if username.strip().lower() == "almadina" and password.strip() == outlet_select:
            st.session_state.logged_in = True
            st.session_state.outlet = outlet_select
            st.success(f"✅ Logged in as **{outlet_select}**")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Username must be 'almadina' and password should match the selected outlet.")

# =============================
# MAIN PAGE (after login)
# =============================
else:
    # Header section
    top_cols = st.columns([6, 1, 1])
    with top_cols[0]:
        st.title(f"📋 Item Forms — {st.session_state.outlet}")

    with top_cols[1]:
        if st.button("🔁 Logout / Switch Outlet"):
            st.session_state.logged_in = False
            st.session_state.outlet = ""
            st.rerun()

    with top_cols[2]:
        if st.button("🧹 Clear Pending"):
            st.session_state.pending_items = []

    st.divider()

    # =============================
    # SIDEBAR
    # =============================
    with st.sidebar:
        st.header("🗂️ Select Form Type")
        selected_form = st.radio("Forms", FORMS)

        st.divider()
        st.write("📦 Pending items:", len(st.session_state.pending_items))

        if st.button("🚀 Full Submit (Demo Only)"):
            if len(st.session_state.pending_items) == 0:
                st.warning("No pending items to submit.")
            else:
                st.session_state.submitted_items.extend(st.session_state.pending_items)
                st.session_state.pending_items = []
                st.success("✅ Submitted all items (demo only — not uploaded).")

    # =============================
    # INPUT FORM
    # =============================
    st.subheader(f"➕ Add New Item — {selected_form}")

    with st.form("item_form"):
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1:
            barcode = st.text_input("Barcode")
            product_name = st.text_input("Product Name")
            qty = st.number_input("Qty [PCS]", min_value=0, step=1)
        with c2:
            cost = st.number_input("Cost", min_value=0.0, format="%.2f")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=0.0)
            if amount == 0 and qty > 0 and cost > 0:
                amount = round(qty * cost, 2)
        with c3:
            expiry = st.date_input("Expiry Date")
            supplier = st.text_input("Supplier Name")
            remarks = st.text_area("Remarks (if any)")

        add_btn = st.form_submit_button("Add to List")

        if add_btn:
            item = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Form": selected_form,
                "Barcode": barcode,
                "Product Name": product_name,
                "Qty": int(qty),
                "Cost": float(cost),
                "Amount": float(amount),
                "Expiry Date": expiry.strftime("%d-%b-%y"),
                "Supplier": supplier,
                "Remarks": remarks,
                "Outlet": st.session_state.outlet,
            }
            st.session_state.pending_items.append(item)
            st.success("Item added to pending list ✅")
            st.rerun()

    st.divider()

    # =============================
    # PENDING ITEMS TABLE
    # =============================
    st.subheader("🕒 Pending Items")
    if len(st.session_state.pending_items) == 0:
        st.info("No pending items. Add using the form above.")
    else:
        df_pending = pd.DataFrame(st.session_state.pending_items)
        st.dataframe(df_pending, use_container_width=True)

        remove_index = st.number_input(
            "Enter Row Index to Remove (0-based)",
            min_value=0,
            max_value=max(0, len(st.session_state.pending_items) - 1),
            step=1,
        )

        if st.button("🗑️ Remove Selected Row"):
            try:
                st.session_state.pending_items.pop(int(remove_index))
                st.success(f"Removed row {remove_index}")
                st.rerun()
            except Exception:
                st.error("Invalid index provided.")

        if st.button("✅ Full Submit (Demo Only)"):
            st.session_state.submitted_items.extend(st.session_state.pending_items)
            st.session_state.pending_items = []
            st.success("✅ All pending items submitted (demo only — not uploaded).")

    st.divider()

    # =============================
    # SUBMITTED ITEMS TABLE
    # =============================
    st.subheader("📤 Submitted Items (Demo History)")
    if len(st.session_state.submitted_items) == 0:
        st.info("No submitted items yet.")
    else:
        df_submitted = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df_submitted, use_container_width=True)

    # =============================
    # FOOTER
    # =============================
    st.caption("💡 Demo Mode: Data is stored only in memory and resets when refreshed. No Google Sheets upload is performed.")

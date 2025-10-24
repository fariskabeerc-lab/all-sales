import streamlit as st
import pandas as pd

# =======================================
# PAGE CONFIG
# =======================================
st.set_page_config(page_title="Outlet Dashboard", layout="wide")

# =======================================
# OUTLET LOGIN DATA
# =======================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida",
    "Hadeqat", "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan",
    "Superstore", "Tay Tay", "Safa oudmehta", "Port saeed"
]
password = "123123"

# =======================================
# LOAD ITEM DATA
# =======================================
@st.cache_data
def load_data():
    # 🟢 Replace with your actual Excel file path
    df = pd.read_excel("alllist.xlsx")
    df.columns = df.columns.str.strip()
    return df

item_data = load_data()

# =======================================
# SESSION STATE INIT
# =======================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "outlet" not in st.session_state:
    st.session_state.outlet = None
if "items" not in st.session_state:
    st.session_state.items = []

# =======================================
# LOGIN PAGE
# =======================================
if not st.session_state.logged_in:
    st.sidebar.header("🔐 Login")

    with st.sidebar.form("login_form"):
        outlet = st.selectbox("Select Outlet", outlets)
        pw = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

        if login_btn:
            if pw == password:
                st.session_state.logged_in = True
                st.session_state.outlet = outlet
                st.rerun()
            else:
                st.sidebar.error("❌ Incorrect password. Try again.")

# =======================================
# MAIN DASHBOARD
# =======================================
if st.session_state.logged_in:
    st.title(f"🏪 {st.session_state.outlet} Dashboard")

    with st.form("item_form"):
        st.subheader("🧾 Add Item Details")

        col1, col2, col3 = st.columns([1.5, 1.5, 1])
        with col1:
            barcode = st.text_input("Item Barcode")
        with col2:
            item_name = st.text_input("Item Name")
        with col3:
            supplier = st.text_input("LP Supplier")

        col4, col5 = st.columns(2)
        with col4:
            cost = st.number_input("Cost", min_value=0.0, step=0.01)
        with col5:
            selling = st.number_input("Selling Price", min_value=0.0, step=0.01)

        # Auto-fill when barcode entered
        if barcode:
            match = item_data[item_data["Item Bar Code"].astype(str) == barcode]
            if not match.empty:
                item_name = match.iloc[0]["Item Name"]
                cost = float(match.iloc[0]["Cost"])
                selling = float(match.iloc[0]["Selling"])
                supplier = match.iloc[0]["LP Supplier"]

        add_btn = st.form_submit_button("➕ Add to List")

        if add_btn:
            if barcode and item_name:
                st.session_state.items.append({
                    "Barcode": barcode,
                    "Item Name": item_name,
                    "Supplier": supplier,
                    "Cost": cost,
                    "Selling": selling
                })
                st.success(f"✅ {item_name} added successfully!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter at least a barcode and item name.")

    # =======================================
    # DISPLAY ADDED ITEMS
    # =======================================
    if st.session_state.items:
        st.subheader("📋 Added Items")
        df = pd.DataFrame(st.session_state.items)
        st.dataframe(df, use_container_width=True)

        colA, colB = st.columns(2)
        with colA:
            if st.button("🧹 Reset List"):
                st.session_state.items = []
                st.success("List cleared!")
                st.rerun()
        with colB:
            st.download_button(
                "💾 Download as Excel",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"{st.session_state.outlet}_Items.csv",
                mime="text/csv"
            )

    # =======================================
    # LOGOUT BUTTON
    # =======================================
    st.sidebar.button("🚪 Logout", on_click=lambda: [
        st.session_state.update({"logged_in": False, "outlet": None, "items": []}),
        st.rerun()
    ])

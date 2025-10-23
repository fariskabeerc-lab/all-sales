import streamlit as st
import pandas as pd

# ======================================
# PAGE CONFIGURATION
# ======================================
st.set_page_config(page_title="Product Management Forms", layout="wide")

# ======================================
# OUTLET LIST
# ======================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida", "Hadeqat",
    "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan", "Superstore",
    "Tay Tay", "Safa oudmehta", "Port saeed"
]

# ======================================
# INITIAL SESSION STATES
# ======================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "outlet" not in st.session_state:
    st.session_state.outlet = None
if "submitted_data" not in st.session_state:
    st.session_state.submitted_data = []

# ======================================
# LOGIN PAGE
# ======================================
if not st.session_state.logged_in:
    st.title("🏪 Al Madina Product Management Demo")

    # Outlet selection
    st.markdown("### 🏬 Select Your Outlet")
    selected_outlet = st.selectbox("Choose Outlet", ["-- Select --"] + outlets)

    # Username / Password
    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    login_success = False  # flag

    if st.button("Login"):
        if selected_outlet == "-- Select --":
            st.warning("Please select an outlet before logging in.")
        elif username.lower() == "almadina" and password == "123123":
            login_success = True
        else:
            st.error("Invalid username or password.")

    if login_success:
        st.session_state.logged_in = True
        st.session_state.outlet = selected_outlet
        st.success(f"✅ Logged in successfully! Outlet: {st.session_state.outlet}")

# ======================================
# DASHBOARD AFTER LOGIN
# ======================================
if st.session_state.logged_in and st.session_state.outlet:
    # ======================================
    # FULL SCREEN TOGGLE
    # ======================================
    st.sidebar.subheader("⚙️ Settings")
    full_screen = st.sidebar.toggle("🖥️ Full Screen Mode")

    if full_screen:
        st.markdown(
            """
            <style>
            [data-testid="stAppViewContainer"] {
                padding: 0 !important;
                margin: 0 !important;
            }
            [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
                display: none;
            }
            html, body, .block-container {
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # ======================================
    # DASHBOARD HEADER
    # ======================================
    st.markdown(
        f"<h2 style='text-align:center;'>🛒 Outlet Dashboard: {st.session_state.outlet}</h2>",
        unsafe_allow_html=True
    )

    # ======================================
    # FORM SELECTION
    # ======================================
    st.subheader("📋 Select Form Type")
    form_type = st.selectbox(
        "Choose a form to fill",
        ["Expiry", "Damage", "Near Expiry", "Other"]
    )

    # ======================================
    # FORM INPUT SECTION
    # ======================================
    st.markdown(
        """
        <div style='background-color:#f9f9f9; padding:20px; border-radius:15px; box-shadow:0 0 10px rgba(0,0,0,0.1);'>
        """,
        unsafe_allow_html=True
    )

    with st.form("product_form", clear_on_submit=True):
        st.markdown(f"### ✏️ Enter {form_type} Form Details")

        col1, col2, col3 = st.columns(3)
        with col1:
            barcode = st.text_input("Barcode")
            qty = st.number_input("Qty [PCS]", min_value=0, step=1)
        with col2:
            product_name = st.text_input("Product Name")
            cost = st.number_input("Cost", min_value=0.0, step=0.01)
        with col3:
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            expiry_date = st.date_input("Expiry Date")

        supplier_name = st.text_input("Supplier Name")
        remarks = st.text_area("Remarks [if any]")

        submitted = st.form_submit_button("➕ Add to List")

        if submitted:
            st.session_state.submitted_data.append({
                "Form Type": form_type,
                "Barcode": barcode,
                "Product Name": product_name,
                "Qty [PCS]": qty,
                "Cost": cost,
                "Amount": amount,
                "Expiry Date": expiry_date.strftime("%d-%b-%y"),
                "Supplier Name": supplier_name,
                "Remarks": remarks,
                "Outlet": st.session_state.outlet
            })
            st.success(f"{form_type} record added successfully!")

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================================
    # DISPLAY TABLE
    # ======================================
    if st.session_state.submitted_data:
        df = pd.DataFrame(st.session_state.submitted_data)
        st.markdown("### 📦 Submitted Items")
        st.dataframe(df, use_container_width=True)

        if st.button("✅ Final Submit (Save All to Sheet - Demo)"):
            st.success("All entries submitted successfully to Google Sheet (Demo Mode)")
            st.session_state.submitted_data.clear()

    st.caption("💡 This is a demo — data is stored only during the session.")

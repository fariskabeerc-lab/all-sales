import streamlit as st
import pandas as pd

# ======================================
# PAGE CONFIGURATION
# ======================================
st.set_page_config(page_title="Product Management Forms", layout="wide")

# ======================================
# OUTLET LOGIN
# ======================================
st.title("🏪 Al Madina Product Management Demo")

outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida", "Hadeqat",
    "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan", "Superstore",
    "Tay Tay", "Safa oudmehta", "Port saeed"
]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        if username.lower() == "almadina" and password == "123123":
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password. Try again.")
else:
    # Once logged in, select outlet
    if "outlet" not in st.session_state:
        st.session_state.outlet = None

    if not st.session_state.outlet:
        st.subheader("🏬 Select Your Outlet")
        selected_outlet = st.selectbox("Choose Outlet", outlets)
        if st.button("Confirm Outlet"):
            st.session_state.outlet = selected_outlet
            st.experimental_rerun()
    else:
        # ======================================
        # MAIN DASHBOARD AFTER OUTLET SELECTED
        # ======================================
        st.sidebar.success(f"✅ Logged in as: {st.session_state.outlet}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.outlet = None
            st.experimental_rerun()

        # ======================================
        # FULL SCREEN TOGGLE
        # ======================================
        full_screen = st.sidebar.toggle("🖥️ Full Screen Mode")

        if full_screen:
            st.markdown(
                """
                <style>
                .main {padding-top: 0rem; padding-left: 0rem; padding-right: 0rem;}
                </style>
                """,
                unsafe_allow_html=True,
            )

        # ======================================
        # FORM TYPE SELECTION
        # ======================================
        st.subheader("📋 Select Form Type")
        form_type = st.selectbox(
            "Choose a form to fill",
            ["Expiry", "Damage", "Near Expiry", "Other"]
        )

        # ======================================
        # SESSION STATE INITIALIZATION
        # ======================================
        if "submitted_data" not in st.session_state:
            st.session_state.submitted_data = []

        # ======================================
        # FORM INPUT SECTION
        # ======================================
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

        # ======================================
        # DISPLAY SUBMITTED DATA
        # ======================================
        if st.session_state.submitted_data:
            df = pd.DataFrame(st.session_state.submitted_data)
            st.markdown("### 📦 Submitted Items")
            st.dataframe(df, use_container_width=True)

            if st.button("✅ Final Submit (Save All to Sheet - Demo)"):
                st.success("All entries submitted successfully to Google Sheet (Demo Mode)")
                st.session_state.submitted_data.clear()

        st.caption("💡 This is a demo — data is stored only during the session.")

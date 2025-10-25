import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet Dashboard", layout="wide")

# ==========================================
# SESSION STATE INIT
# ==========================================
for key in [
    "logged_in", "selected_outlet", "page", "submitted_items",
    "barcode_input", "qty_input", "expiry_input", "remarks_input",
    "feedback_name", "feedback_text", "feedback_rating",
    "customer_feedback", "clear_feedback_form"
]:
    if key not in st.session_state:
        if key == "submitted_items" or key == "customer_feedback":
            st.session_state[key] = []
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now()
        elif key == "feedback_rating":
            st.session_state[key] = 3
        elif key == "clear_feedback_form":
            st.session_state[key] = False
        else:
            st.session_state[key] = ""

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
# LOGIN
# ==========================================
outlets = ["Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl"]
password = "123123"

if not st.session_state.logged_in:
    st.title("🔐 Outlet Login")
    username = st.text_input("Username")
    outlet = st.selectbox("Select Outlet", outlets)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "almadina" and pwd == password:
            st.session_state.logged_in = True
            st.session_state.selected_outlet = outlet
            st.session_state.page = "Customer Feedback"
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ==========================================
# DASHBOARD
# ==========================================
if st.session_state.logged_in:

    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.session_state.page = st.sidebar.radio("Go to", ["Customer Feedback", "Outlet Form"])

    # ==========================================
    # CUSTOMER FEEDBACK PAGE
    # ==========================================
    if st.session_state.page == "Customer Feedback":
        st.header(f"💬 Customer Feedback - {st.session_state.selected_outlet}")

        # Feedback form
        name = st.text_input("Customer Name", key="feedback_name")
        feedback = st.text_area("Feedback / Comments", key="feedback_text")

        # Slider rating
        labels = ["Very Bad", "Bad", "Neutral", "Good", "Excellent"]
        rating = st.slider(
            "Rating",
            min_value=1, max_value=5,
            value=st.session_state.feedback_rating,
            key="feedback_rating"
        )
        st.write(f"**Selected Rating:** {labels[rating-1]}")

        # Submit
        if st.button("📤 Submit Feedback"):
            # Save feedback
            st.session_state.customer_feedback.append({
                "Customer Name": name,
                "Feedback": feedback,
                "Rating": labels[rating-1],
                "Outlet": st.session_state.selected_outlet,
                "Date": datetime.now().strftime("%d-%b-%Y %H:%M")
            })
            st.success("✅ Feedback submitted successfully!")
            st.session_state.clear_feedback_form = True
            st.experimental_rerun()

        # Clear form after rerun
        if st.session_state.clear_feedback_form:
            st.session_state.update({
                "feedback_name": "",
                "feedback_text": "",
                "feedback_rating": 3
            })
            st.session_state.clear_feedback_form = False

    # ==========================================
    # OUTLET FORM PAGE
    # ==========================================
    if st.session_state.page == "Outlet Form":
        st.header(f"🏪 Outlet Form - {st.session_state.selected_outlet}")

        # Form Inputs
        form_type = st.sidebar.radio("📋 Select Form Type", ["Expiry", "Damages", "Near Expiry"])
        col1, col2, col3 = st.columns(3)
        with col1:
            barcode = st.text_input("Barcode", value=st.session_state.barcode_input)
            st.session_state.barcode_input = barcode
        with col2:
            qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input)
            st.session_state.qty_input = qty
        with col3:
            if form_type != "Damages":
                expiry = st.date_input("Expiry Date", st.session_state.expiry_input)
                st.session_state.expiry_input = expiry
            else:
                expiry = None

        # Auto-fill
        item_name = ""
        cost = 0.0
        selling = 0.0
        supplier = ""
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

        remarks = st.text_area("Remarks [if any]", value=st.session_state.remarks_input)
        st.session_state.remarks_input = remarks

        # Add to list
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
                    "Outlet": st.session_state.selected_outlet
                })
                st.success("✅ Added to list successfully!")
                st.session_state.barcode_input = ""
                st.session_state.qty_input = 1
                st.session_state.expiry_input = datetime.now()
                st.session_state.remarks_input = ""
            else:
                st.warning("⚠️ Fill barcode and item before adding.")

        # Display submitted items
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
                    st.experimental_rerun()

    # ==========================================
    # LOGOUT
    # ==========================================
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

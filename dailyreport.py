import streamlit as st
import pandas as pd
from datetime import datetime

# ====================================
# PAGE CONFIG
# ====================================
st.set_page_config(page_title="Outlet Entry Dashboard", layout="wide")
st.title("🏪 Outlet Entry Dashboard")

# ====================================
# USER SESSION SIMULATION (you can replace with real login)
# ====================================
if "username" not in st.session_state:
    st.session_state["username"] = "Outlet_User"  # Example user name

username = st.session_state["username"]

# ====================================
# SIDEBAR MENU
# ====================================
st.sidebar.title("📋 Navigation")
menu = st.sidebar.radio("Select Form", ["Expiry Entry", "Damage Entry"])

# ====================================
# INITIALIZE DATA STORAGE
# ====================================
if "expiry_data" not in st.session_state:
    st.session_state["expiry_data"] = pd.DataFrame(columns=["Date", "Username", "Item Name", "Quantity", "Reason"])
if "damage_data" not in st.session_state:
    st.session_state["damage_data"] = pd.DataFrame(columns=["Date", "Username", "Item Name", "Quantity", "Reason"])

# ====================================
# FORM FUNCTION
# ====================================
def entry_form(data_key, title):
    st.subheader(f"{title} Form")

    with st.form(f"{data_key}_form", clear_on_submit=True):
        item_name = st.text_input("🧾 Item Name")
        quantity = st.number_input("📦 Quantity", min_value=1, step=1)
        reason = st.text_area("📝 Reason / Remarks")
        submitted = st.form_submit_button("Add Entry")

        if submitted:
            if item_name.strip() == "" or reason.strip() == "":
                st.warning("⚠️ Please fill all fields before submitting.")
            else:
                new_entry = pd.DataFrame(
                    [[datetime.now().strftime("%Y-%m-%d"), username, item_name, quantity, reason]],
                    columns=["Date", "Username", "Item Name", "Quantity", "Reason"]
                )
                st.session_state[data_key] = pd.concat(
                    [st.session_state[data_key], new_entry], ignore_index=True
                )
                st.success("✅ Entry added successfully!")

    # Display data table if entries exist
    if not st.session_state[data_key].empty:
        st.write("### 🧾 Current Entries")
        st.dataframe(st.session_state[data_key], use_container_width=True)

        # Submit all data button
        if st.button("📤 Submit All Data", key=f"{data_key}_submit"):
            st.success("✅ All data submitted successfully!")
            # You can save it like:
            # st.session_state[data_key].to_excel(f"{data_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", index=False)
            st.session_state[data_key] = pd.DataFrame(columns=["Date", "Username", "Item Name", "Quantity", "Reason"])

# ====================================
# PAGE LOGIC
# ====================================
if menu == "Expiry Entry":
    entry_form("expiry_data", "Expiry")
elif menu == "Damage Entry":
    entry_form("damage_data", "Damage")

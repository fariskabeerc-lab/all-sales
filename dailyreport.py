import streamlit as st
import pandas as pd
from datetime import datetime
from github import Github
import io

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Outlet Product Dashboard", layout="wide")

# ==============================
# GITHUB CONFIG
# ==============================
GITHUB_TOKEN = "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"  # Replace with your token
REPO_NAME = "sickmansickmansickman/reports"             # Replace with your repo
SUBMISSION_FOLDER = "submit"            # Folder in GitHub to store files

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ==============================
# OUTLET LOGIN
# ==============================
users = {
    "safa": "123123",
    "fida": "12341234",
    "Outlet3": "pass3",
    "Outlet4": "pass4",
    "Outlet5": "pass5",
    "Outlet6": "pass6",
    "Outlet7": "pass7",
    "Outlet8": "pass8",
    "Outlet9": "pass9",
    "Outlet10": "pass10",
    "Outlet11": "pass11",
    "Outlet12": "pass12",
    "Outlet13": "pass13",
    "Outlet14": "pass14",
    "Outlet15": "pass15",
    "Outlet16": "pass16",
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Outlet Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.session_state.user = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password")
else:
    st.title(f"🏬 Dashboard - {st.session_state.user}")

    # ==============================
    # Sidebar - Form Selection
    # ==============================
    form_type = st.sidebar.selectbox("Select Form Type", ["Near Expiry", "Damaged", "Other"])

    # ==============================
    # Form
    # ==============================
    st.subheader(f"📋 {form_type} Form")

    with st.form("product_form"):
        barcode = st.text_input("Barcode")
        product_name = st.text_input("Product Name")
        qty = st.number_input("Qty [PCS]", min_value=0)
        cost = st.number_input("Cost", min_value=0.0, format="%.2f")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        expiry = st.date_input("Expiry Date")
        supplier = st.text_input("Supplier Name")
        remarks = st.text_area("Remarks [if any]")

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("✅ Data submitted successfully!")

            # Create dataframe
            data = {
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
            }
            df = pd.DataFrame([data])

            # Save to session state for demo dashboard
            if "submitted_data" not in st.session_state:
                st.session_state.submitted_data = []
            st.session_state.submitted_data.append(data)

            # ==============================
            # Push to GitHub
            # ==============================
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)

            # Create a filename with Outlet + Date + Time
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{SUBMISSION_FOLDER}/{st.session_state.user}_{timestamp}.csv"

            try:
                repo.create_file(file_name, f"New submission from {st.session_state.user}", csv_buffer.getvalue())
                st.success(f"Data also pushed to GitHub as `{file_name}`")
            except Exception as e:
                st.error(f"GitHub submission failed: {e}")

    # ==============================
    # Show Submitted Data (Demo Dashboard)
    # ==============================
    st.subheader("📊 Submitted Data Overview")
    if "submitted_data" in st.session_state and st.session_state.submitted_data:
        df_display = pd.DataFrame(st.session_state.submitted_data)
        st.dataframe(df_display)
    else:
        st.info("No data submitted yet.")

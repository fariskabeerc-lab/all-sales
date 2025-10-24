import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet Form Dashboard", layout="wide")

# ==========================================
# LOAD ITEM DATA (for auto-fill)
# ==========================================
@st.cache_data
def load_item_data():
    file_path = "alllist.xlsx"  # Replace with your Excel path
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    return df

item_data = load_item_data()

# ==========================================
# GOOGLE SHEETS CONNECTION
# ==========================================
def connect_to_gsheet():
    credentials_dict = {
      "type": "service_account",
      "project_id": "madina-476107",
      "private_key_id": "22bfbcd374b76734518df81884f1004011d54804",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDOIHqNEAQY/WMd\n6dTLDp8UD114ELMqjg8xdNWqM1qZKoR8+y7BzPGFAikFIxCztNDQ8GKW4tsxPxVg\nzjOLPffMPBC4shyBi1XmCmYmxy6dZcYcfUftV1ZdTsrJi+TUf/djLmrIyylpkJ9q\n01DKWVSMeIBKH1g5BDz4Ll3yL/NfjNCP1k/iCCy1ZlSBByiYZ9CXGs6rzRE9C3HT\n7hBV3dmRk3rhZLFSm3j5DFkzjrhTzA5CgAy5oivJuzCUwQkCCqjmINDV7WyyU6+u\ndV1Fow3Xrpo3n7x4Ds1QGG1PE+aBqhevskublbXLufU/ZtP0BeaF3OsTa/FHC9fV\nwfp1fA7nAgMBAAECggEAC3QHizYEHEVcEAnxnnTKBwnRhj3bTraFBpj41FO1KYSQ\nxwcH8pHKK7tSfywTHgEihzGMMNkbF9HrBK2AdLC1R55gyXpwFgyhcb5LLcVshCdn\nCic162yqalXZ87f3t40CuHqYSV7shqaYDQ3/07aB+aoqarPyKXzgTGP7KV1btwfY\n2R5nscop2YGgkZnX/UHCmyQ7HHi1NlVqnVmYHRvAhcndJKfyJgQ8IViui2exHQOe\nfCUATt2VB/31n6FhFSuUWbJlJK71BFeQA/YQoA3FxULt/f9dIxlqddIdQGzYOb1m\nAXDDngHB60JBNFxPIxScvVfd1Ns0D40hNqWbbxTVTQKBgQD90bJ9a1q6fPzfp2jL\nBXSEazVqUCwzxztFAErimUbARdefeQpoOmGaCyN/pjNxCNvKUbEstv4xPew2UUaP\nosve7ATkZCn7/XXdLL54WsXV0S+200+h9FRECak7thAeAZB50nKN0/+yLP8X8ss0\nCo7ZhpU1oNzom7nxIBGqEVZD6wKBgQDP5eCOtxU8QKyEndWClIy9C9C0sohjNFGs\nMV5kWJjP3Sim9j+VwpumFeODvnrpmkGsdZJrdgv+70je8gjsamljxoa4u5J2ND7q\n5j0gmCmc54ydPKNmgyCb0WDh6Lqf7lKl/sxxsfoypmpoao4XiU+x7P6VcexvJlUv\nzZGEQoZt9QKBgQCfA5rRHEqw/tDlxVnPp1FCDHBgdG3c2np1ViOUJva+SoM1s30j\noz+2ZDgPJq6fqC8aZ2eaXeKOMv8jYHPWVOVoeXDvLRlod3g54mhJuoSq2e0MmwIO\nsqWAIpVVhVA/nDdJOuDtnd1ZYPtHo6JOrjakbL5Z5LfBOp6ZQ8ANTeM/lQKBgFcm\nhXEuPJ+qeOeLBqMbxLfHCTGGmfgESayGcYxdO4n/qvf6yILuNrNz/5ENu5bLzHYQ\nP1X/AV5YTtLu4WDB5vYllfpA30/f7PQpmjxcrS0SP/b2IYVquLO5HQT2u60picn+\nOxP6SOkMrBSjfndNX3Q15i8dt8CMcC9+3F52SMY1AoGANWCnR99ZrfmlQEQbZ46Y\nS7sfEfVOH01uQZMzNdWOQ0aSNJCc+0QVAoDXLcCx7+0zyZWcTmCWXwpyfM5mG5Qe\nIlQnN6Fpuz323Ui/0dxz9VQ63jNM+X9cCn4ZryMqlsvRjvBkddAmswG8oLMwNoP/\ncKg6b7+wwb81269smHTOq7U=\n-----END PRIVATE KEY-----\n",
      "client_email": "sheet-madina@madina-476107.iam.gserviceaccount.com",
      "client_id": "111687925191106670207",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheet-madina%40madina-476107.iam.gserviceaccount.com",
      "universe_domain": "googleapis.com"
    }
    creds = Credentials.from_service_account_info(credentials_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1BOGgBAEW2yvE4Cm9lCtASe_H7RD76GBPcVtRWWJ1nf0").sheet1
    return sheet

# ==========================================
# LOGIN SYSTEM
# ==========================================
outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida", "Hadeqat",
    "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan", "Superstore",
    "Tay Tay", "Safa oudmehta", "Port saeed"
]
password = "123123"

# Initialize session state variables
for key in ["logged_in", "selected_outlet", "submitted_items", "barcode_input", "qty_input", "expiry_input", "remarks_input"]:
    if key not in st.session_state:
        if key == "submitted_items":
            st.session_state[key] = []
        elif key == "qty_input":
            st.session_state[key] = 1
        elif key == "expiry_input":
            st.session_state[key] = datetime.now()
        else:
            st.session_state[key] = ""

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 Outlet Login")
    username = st.text_input("Username", placeholder="Enter username")
    outlet = st.selectbox("Select your outlet", outlets)
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "almadina" and pwd == password:
            st.session_state.logged_in = True
            st.session_state.selected_outlet = outlet
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ==========================================
# MAIN DASHBOARD
# ==========================================
else:
    outlet_name = st.session_state.selected_outlet
    st.markdown(f"<h2 style='text-align:center;'>🏪 {outlet_name} Dashboard</h2>", unsafe_allow_html=True)

    # FORM TYPE SELECTION
    form_type = st.sidebar.radio(
        "📋 Select Form Type",
        ["Expiry", "Damages", "Near Expiry"]
    )
    st.markdown("---")

    # ==============================
    # FORM INPUTS
    # ==============================
    col1, col2, col3 = st.columns(3)
    with col1:
        barcode = st.text_input("Barcode", value=st.session_state.barcode_input)
        st.session_state.barcode_input = barcode
    with col2:
        qty = st.number_input("Qty [PCS]", min_value=1, value=st.session_state.qty_input)
        st.session_state.qty_input = qty
    with col3:
        # Show expiry only for Expiry and Near Expiry
        if form_type != "Damages":
            expiry = st.date_input("Expiry Date", st.session_state.expiry_input)
            st.session_state.expiry_input = expiry
        else:
            expiry = None

    # AUTO-FILL BASED ON BARCODE
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

    # ==============================
    # ADD TO LIST BUTTON
    # ==============================
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
            # CLEAR FORM INPUTS
            st.session_state.barcode_input = ""
            st.session_state.qty_input = 1
            st.session_state.expiry_input = datetime.now()
            st.session_state.remarks_input = ""
        else:
            st.warning("⚠️ Fill barcode and item before adding.")

    # ==============================
    # DISPLAY SUBMITTED ITEMS
    # ==============================
    if st.session_state.submitted_items:
        st.markdown("### 🧾 Items Added")
        df = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df, use_container_width=True)

        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("🧹 Clear List"):
                st.session_state.submitted_items = []
        with colB:
            if st.button("📤 Submit All"):
                try:
                    sheet = connect_to_gsheet()
                    sheet.append_rows([list(row.values()) for row in st.session_state.submitted_items])
                    st.success("✅ All data submitted to Google Sheet successfully!")
                    st.session_state.submitted_items = []
                except Exception as e:
                    st.error(f"❌ Error submitting to Google Sheet: {e}")

    # LOGOUT
    st.sidebar.button("🚪 Logout", on_click=lambda: [
        st.session_state.update({
            "logged_in": False, 
            "selected_outlet": None, 
            "submitted_items": [], 
            "barcode_input": "", 
            "qty_input": 1, 
            "expiry_input": datetime.now(),
            "remarks_input": ""
        }),
        st.experimental_rerun()
    ])

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Expiry/Damages/Near-Expiry Demo", layout="wide")

# -------------------------------
# Helper functions
# -------------------------------

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
    "Outlet A",
    "Outlet B",
    "Outlet C",
    "Outlet D",
    "Outlet E",
    "Outlet F",
    "Outlet G",
    "Outlet H",
    "Outlet I",
    "Outlet J",
    "Outlet K",
    "Outlet L",
    "Outlet M",
    "Outlet N",
    "Outlet O",
    "Outlet P",
]

FORMS = ["Expiry", "Damages", "Near Expiry", "Other"]

# -------------------------------
# Login
# -------------------------------
if not st.session_state.logged_in:
    st.markdown("# 🔐 Login")
    with st.form("login_form", clear_on_submit=False):
        cols = st.columns([1, 1, 1])
        with cols[0]:
            username = st.text_input("Username")
        with cols[1]:
            password = st.text_input("Password", type="password")
        with cols[2]:
            outlet_select = st.selectbox("Select your Outlet", OUTLETS)
        submitted = st.form_submit_button("Login")

    if submitted:
        # Requirement: username must be 'almadina' and password equals the outlet name (as per your instructions)
        if username.strip().lower() == "almadina" and password.strip() == outlet_select:
            st.session_state.logged_in = True
            st.session_state.outlet = outlet_select
            st.success(f"Logged in as **{outlet_select}**")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. Username should be 'almadina' and password should match the chosen outlet name.")

else:
    # Top bar with logout and outlet name
    cols_top = st.columns([6, 1, 1])
    with cols_top[0]:
        st.title(f"📋 Forms Demo — {st.session_state.outlet}")
    with cols_top[1]:
        if st.button("🔁 Switch Outlet / Logout"):
            # simple logout
            st.session_state.logged_in = False
            st.session_state.outlet = ""
            st.experimental_rerun()

    with cols_top[2]:
        if st.button("⬇️ Clear Pending"):
            st.session_state.pending_items = []

    st.markdown("---")

    # Layout: sidebar for form selection (as list, one at a time)
    with st.sidebar:
        st.header("Select Form Type")
        selected_form = st.radio("Forms", FORMS)
        st.markdown("---")
        st.markdown("**Quick actions**")
        st.write("Pending items: ", len(st.session_state.pending_items))
        if st.button("Simulate Full Submit to Google Sheets (demo)"):
            # For demo: move pending to submitted and clear pending
            if len(st.session_state.pending_items) == 0:
                st.warning("No pending items to submit.")
            else:
                st.session_state.submitted_items.extend(st.session_state.pending_items)
                st.session_state.pending_items = []
                st.success("Submitted pending items to submitted list (demo). In a real app this would push to Google Sheets.")

    # Main area: form inputs + pending list + submitted list
    st.subheader(f"Add new item — {selected_form}")

    with st.form(key="item_form"):
        # Responsive columns: if narrow, Streamlit will wrap
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1:
            barcode = st.text_input("Barcode")
            product_name = st.text_input("Product Name")
            qty = st.number_input("Qty [PCS]", min_value=0, step=1)
        with c2:
            cost = st.number_input("Cost", min_value=0.0, format="%.2f")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=0.0)
            # auto-calc amount if user leaves it default 0
            if amount == 0 and qty > 0 and cost > 0:
                amount = round(qty * cost, 2)
        with c3:
            expiry = st.date_input("Expiry Date")
            supplier = st.text_input("Supplier Name")
            remarks = st.text_area("Remarks (if any)")

        add_btn = st.form_submit_button("➕ Add to List")

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
            st.success("Added to pending list")
            st.experimental_rerun()

    st.markdown("---")

    # Pending items table with remove option
    st.subheader("Pending Items (will be sent together on Full Submit)")
    if len(st.session_state.pending_items) == 0:
        st.info("No pending items. Add items using the form above.")
    else:
        df_pending = pd.DataFrame(st.session_state.pending_items)
        st.dataframe(df_pending, use_container_width=True)

        # allow removing rows by index
        remove_idx = st.number_input("Enter row index to remove (0-based)", min_value=0, max_value=max(0, len(st.session_state.pending_items) - 1), step=1)
        if st.button("Remove Row"):
            try:
                st.session_state.pending_items.pop(int(remove_idx))
                st.success(f"Removed row {remove_idx}")
                st.experimental_rerun()
            except Exception as e:
                st.error("Could not remove the row. Check the index.")

        # Full submit button (demo pushes to 'submitted_items' list). In production this is where you'd push to Google Sheets.
        if st.button("✅ Full Submit (push all pending to Google Sheet - demo)"):
            # demo action: append to submitted_items and clear pending
            st.session_state.submitted_items.extend(st.session_state.pending_items)
            st.session_state.pending_items = []
            st.success("All pending items moved to submitted list (demo). In a real app these would be written to Google Sheets.")

    st.markdown("---")

    # Submitted items table (history)
    st.subheader("Submitted Items (demo history)")
    if len(st.session_state.submitted_items) == 0:
        st.info("No submitted items yet.")
    else:
        df_sub = pd.DataFrame(st.session_state.submitted_items)
        st.dataframe(df_sub, use_container_width=True)

    # -------------------------------
    # Notes for integrating with Google Sheets
    # -------------------------------
    with st.expander("How to connect this to Google Sheets (instructions)"):
        st.markdown(
            """
- Use `gspread` or `gspread-dataframe` together with a service account JSON key.
- Share the target Google Sheet with the service account email.
- Example (pseudo):

```python
import gspread
from gspread_dataframe import set_with_dataframe

gc = gspread.service_account(filename='service_account.json')
sheet = gc.open_by_key('<SHEET_KEY>').worksheet('<SHEET_NAME>')
# write a DataFrame
set_with_dataframe(sheet, df_sub, include_index=False)
```

For security, don't hardcode credentials in your repo. Use Streamlit Cloud secrets or environment variables.
"""
        )

    st.caption("This is a fully client-side demo — no Google Sheets calls are made. Use the instructions above to activate the real write path.")

    st.markdown("\n\n---\nPowered by a lightweight demo Streamlit app. Responsive layout and suitable for mobile/tablet/desktop previews.")

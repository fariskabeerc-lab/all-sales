import streamlit as st
import pandas as pd
import os

# --- Configuration ---
st.set_page_config(page_title="Variance Dashboard", layout="wide")

# --- Password Protection ---
password = st.text_input("Enter Password", type="password")
if password != "safa123":
    st.warning("⚠️ Incorrect password or not entered.")
    st.stop()

# --- File Mapping ---
OUTLET_FILES = {
    "Hilal": "Hilal oct.Xlsx",
    "Safa Super": "Safa super oct.Xlsx",
    "Azhar HP": "azhar HP oct.Xlsx",
    "Azhar": "azhar Oct.Xlsx",
    "Blue Pearl": "blue pearl oct.Xlsx",
    "Fida": "fida oct.Xlsx",
    "Hadeqat": "hadeqat oct.Xlsx",
    "Jais": "jais oct.Xlsx",
    "Sabah": "sabah oct.Xlsx",
    "Sahat": "sahat oct.Xlsx",
    "Shams HM": "shams HM oct.Xlsx",
    "Shams LLC": "shams llc oct.Xlsx",
    "Superstore": "superstore oct.Xlsx",
    "Tay Tay": "tay tay oct.Xlsx"
}

# --- File Loader ---
@st.cache_data
def load_excel(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        st.error(f"⚠️ File not found: {file_name}")
        return None

# --- Outlet Selection ---
selected_outlet = st.selectbox("Select Outlet", list(OUTLET_FILES.keys()))

file_name = OUTLET_FILES[selected_outlet]
df = load_excel(file_name)

if df is not None:
    st.success(f"✅ Loaded data for {selected_outlet}")
    st.dataframe(df.head())

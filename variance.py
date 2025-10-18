import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ==========================
# Page Configuration
# ==========================
st.set_page_config(page_title="Variance Dashboard", layout="wide")
st.title("📊 October Variance Dashboard")

# ==========================
# Password Protection
# ==========================
password = st.text_input("Enter Password", type="password")
if password != "safa123":
    st.warning("⚠️ Please enter the correct password to access the dashboard.")
    st.stop()

# ==========================
# File Mapping
# ==========================
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

# ==========================
# Load Excel Function
# ==========================
@st.cache_data
def load_excel(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            st.error(f"❌ Error reading {file_name}: {e}")
            return None
    else:
        st.error(f"⚠️ File not found: {file_name}")
        return None

# ==========================
# Outlet Selection
# ==========================
selected_outlet = st.selectbox("🏪 Select Outlet", list(OUTLET_FILES.keys()))
file_name = OUTLET_FILES[selected_outlet]
df = load_excel(file_name)

# ==========================
# Display Data
# ==========================
if df is not None:
    st.success(f"✅ Data loaded successfully for **{selected_outlet}**")

    # Show first few rows
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    # Try to find sales/profit columns if available
    num_cols = df.select_dtypes(include=["number"]).columns
    if len(num_cols) >= 2:
        sales_col = num_cols[0]
        profit_col = num_cols[1]

        # Key Metrics
        total_sales = df[sales_col].sum()
        total_profit = df[profit_col].sum()

        col1, col2 = st.columns(2)
        col1.metric("💰 Total Sales", f"{total_sales:,.2f}")
        col2.metric("📈 Total Profit", f"{total_profit:,.2f}")

        # Plot (if meaningful data exists)
        fig = px.bar(df.head(20), x=df.columns[0], y=sales_col,
                     title=f"Top 20 Items - {selected_outlet}",
                     labels={sales_col: "Sales", df.columns[0]: "Item"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ No numeric columns found for visualization.")
else:
    st.warning("⚠️ Please check if the Excel file name matches exactly and is in the same folder as this script.")

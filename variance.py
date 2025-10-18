import streamlit as st
import pandas as pd
import os

# ==========================
# Page Configuration
# ==========================
st.set_page_config(page_title="Outlet Item Comparison", layout="wide")
st.title("📊 All Outlets Item Sales Dashboard (October)")

# ==========================
# Password Protection
# ==========================
password = st.text_input("Enter Password", type="password")
if password != "safa123":
    st.warning("🔒 Enter correct password to access the dashboard.")
    st.stop()

# ==========================
# Outlet File Mapping
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
# Load Data Function
# ==========================
@st.cache_data
def load_all_data():
    combined_data = {}
    for outlet, file_name in OUTLET_FILES.items():
        if os.path.exists(file_name):
            try:
                df = pd.read_excel(file_name)
                df.columns = [c.strip() for c in df.columns]  # clean column names
                combined_data[outlet] = df
            except Exception as e:
                st.error(f"❌ Error reading {file_name}: {e}")
        else:
            st.warning(f"⚠️ File not found: {file_name}")
    return combined_data

data_dict = load_all_data()

# ==========================
# Search Section
# ==========================
st.subheader("🔍 Search Item Across Outlets")

search_query = st.text_input("Enter Item Name or Item Code:")

if search_query:
    results = []

    for outlet, df in data_dict.items():
        # find matching rows by item code or item name (case insensitive)
        match = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
        if not match.empty:
            for _, row in match.iterrows():
                results.append({
                    "Outlet": outlet,
                    "Item Code": row.get("Item Code", ""),
                    "Item": row.get("Items", ""),
                    "Category": row.get("Category", ""),
                    "Total Sales": row.get("Total Sales", 0),
                    "Total Profit": row.get("Total Profit", 0),
                    "Excise Margin (%)": row.get("Excise Margin (%)", 0)
                })

    if results:
        st.success(f"✅ Found results for '{search_query}'")
        result_df = pd.DataFrame(results)
        st.dataframe(result_df, use_container_width=True)

        # Summary section
        st.subheader("📈 Summary Across All Outlets")
        summary = result_df[["Total Sales", "Total Profit"]].sum()
        avg_margin = result_df["Excise Margin (%)"].mean()

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Sales (All Outlets)", f"{summary['Total Sales']:,.2f}")
        c2.metric("📊 Total Profit (All Outlets)", f"{summary['Total Profit']:,.2f}")
        c3.metric("📈 Average Margin (%)", f"{avg_margin:.2f}%")

    else:
        st.warning(f"❌ No matching items found for '{search_query}' in any outlet.")
else:
    st.info("👆 Enter an item name or code to search across all outlets.")

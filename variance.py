import streamlit as st
import pandas as pd
import os

# ==========================
# Page Configuration
# ==========================
st.set_page_config(page_title="Outlet Item Comparison", layout="wide")
st.title("📊 October Outlet & Item Sales Dashboard")

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
# Load All Data
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
# Search Item
# ==========================
st.subheader("🔍 Search Item Across Outlets")
search_query = st.text_input("Enter Item Name or Item Code:")

# ==========================
# Prepare Result Table
# ==========================
results = []

for outlet, df in data_dict.items():
    if df.empty:
        continue

    # If search query exists, filter rows
    if search_query:
        match = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
    else:
        match = df

    if not match.empty:
        for _, row in match.iterrows():
            results.append({
                "Outlet": outlet,
                "Item Code": row.get("Item Code", ""),
                "Item": row.get("Items", ""),
                "Category": row.get("Category", ""),
                "Total Sales": pd.to_numeric(row.get("Total Sales", 0), errors="coerce"),
                "Total Profit": pd.to_numeric(row.get("Total Profit", 0), errors="coerce"),
                "Excise Margin (%)": pd.to_numeric(row.get("Excise Margin (%)", 0), errors="coerce")
            })

# ==========================
# Show Item Table (if search)
# ==========================
if search_query:
    if results:
        st.success(f"✅ Found results for '{search_query}'")
        result_df = pd.DataFrame(results)
        st.dataframe(result_df, use_container_width=True)
    else:
        st.warning(f"❌ No matching items found for '{search_query}' in any outlet.")

# ==========================
# Key Insights
# ==========================
st.subheader("📈 Key Insights")
if results:
    result_df_numeric = pd.DataFrame(results)
    total_sales = result_df_numeric["Total Sales"].sum()
    total_profit = result_df_numeric["Total Profit"].sum()
    avg_margin = result_df_numeric["Excise Margin (%)"].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Sales", f"{total_sales:,.2f}")
    c2.metric("📊 Total Profit", f"{total_profit:,.2f}")
    c3.metric("📈 Average Margin (%)", f"{avg_margin:.2f}%")
else:
    st.info("Insights will appear here after search.")

# ==========================
# Outlet-wise Total Table (dynamic with search)
# ==========================
st.subheader("🏪 Outlet-wise Total Sales, Profit & Avg Margin")

outlet_summary = []

for outlet, df in data_dict.items():
    if df.empty:
        continue

    # Filter rows if search query exists
    if search_query:
        df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
    else:
        df_filtered = df

    if not df_filtered.empty:
        total_sales = pd.to_numeric(df_filtered.get("Total Sales", 0), errors="coerce").sum()
        total_profit = pd.to_numeric(df_filtered.get("Total Profit", 0), errors="coerce").sum()
        avg_margin = pd.to_numeric(df_filtered.get("Excise Margin (%)", 0), errors="coerce").mean()
        outlet_summary.append({
            "Outlet": outlet,
            "Total Sales": total_sales,
            "Total Profit": total_profit,
            "Average Margin (%)": avg_margin
        })

summary_df = pd.DataFrame(outlet_summary).sort_values(by="Total Sales", ascending=False)
st.dataframe(summary_df, use_container_width=True)

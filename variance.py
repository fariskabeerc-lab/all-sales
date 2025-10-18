import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(page_title="📊 Multi-Outlet Sales Dashboard", layout="wide")
st.title("📊 Multi-Outlet Sales & Category Insights")

# ================================
# OUTLET FILE MAPPING
# ================================
OUTLET_FILES = {
    "Azhar GT": "azhar Oct.Xlsx", 
    "Azhar HP": "azhar HP oct.Xlsx",
    "Blue pearl": "blue pearl oct.Xlsx",
    "Fidha al madina": "fida oct.Xlsx",
    "Hadeqat": "hadeqat oct.Xlsx",
    "Hilal Al madina": "Hilal oct.Xlsx",
    "Jais": "jais oct.Xlsx",
    "Super Store": "superstore oct.Xlsx",
    "Sahath": "sahat oct.Xlsx",
    "Safa al madina Super": "Safa super oct.Xlsx",
    "Sabah": "sabah oct.Xlsx",
    "shams HM": "shams HM oct.Xlsx",
    "shams llc": "shams llc oct.Xlsx",
    "tay tay": "tay tay oct.Xlsx"
}

# Folder where all Excel files are stored
DATA_DIR = "data"  # 👈 Change to your folder path

# ================================
# LOAD ALL OUTLETS DATA
# ================================
@st.cache_data
def load_all_outlet_data():
    all_data = []
    for outlet, filename in OUTLET_FILES.items():
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            df["Outlet"] = outlet
            all_data.append(df)
        else:
            st.warning(f"⚠️ File not found: {filename}")
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)
        df_all.columns = df_all.columns.str.strip()
        return df_all
    else:
        st.error("❌ No valid Excel files found in the folder.")
        return pd.DataFrame()

df_all = load_all_outlet_data()

# ================================
# SIDEBAR: SEARCH
# ================================
st.sidebar.header("🔎 Search Item")
search_input = st.sidebar.text_input("Enter Item Code or Item Name")

# ================================
# ITEM SEARCH SECTION
# ================================
st.subheader("🧾 Item-Wise Comparison Across Outlets")

if search_input:
    result = df_all[
        df_all["Item Code"].astype(str).str.contains(search_input, case=False, na=False)
        | df_all["Items"].astype(str).str.contains(search_input, case=False, na=False)
    ]

    if not result.empty:
        st.success(f"✅ Found {len(result)} entries across {result['Outlet'].nunique()} outlets.")

        display_cols = ["Outlet", "Item Code", "Items", "Category", "Total Sales", "Total Profit", "Excise Margin (%)"]
        st.dataframe(result[display_cols].sort_values(by="Outlet"))

        # --- Total Sales Bar Chart ---
        fig = px.bar(result, x="Outlet", y="Total Sales", color="Outlet",
                     title=f"💰 Total Sales Comparison for '{search_input}' Across Outlets",
                     text_auto=".2s")
        st.plotly_chart(fig, use_container_width=True)

        # --- Total Profit Bar Chart ---
        fig2 = px.bar(result, x="Outlet", y="Total Profit", color="Outlet",
                      title=f"📈 Total Profit Comparison for '{search_input}' Across Outlets",
                      text_auto=".2s")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ No matching item found in any outlet.")
else:
    st.info("👈 Enter an Item Code or Item Name in the sidebar to view comparisons.")

# ================================
# OUTLET vs CATEGORY ANALYSIS
# ================================
st.subheader("🏪 Outlet vs Category Sales Analysis")

if not df_all.empty:
    cat_summary = (
        df_all.groupby(["Outlet", "Category"], as_index=False)["Total Sales"]
        .sum()
        .sort_values(by="Total Sales", ascending=False)
    )

    # --- Category Sales Chart ---
    fig3 = px.bar(
        cat_summary,
        x="Outlet",
        y="Total Sales",
        color="Category",
        barmode="stack",
        title="📦 Category-wise Total Sales per Outlet"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # --- Top Categories per Outlet Table ---
    st.subheader("🏆 Top 3 Categories by Outlet")
    top_cats = cat_summary.groupby("Outlet").apply(lambda x: x.nlargest(3, "Total Sales")).reset_index(drop=True)
    st.dataframe(top_cats)
else:
    st.error("No data loaded. Please check the file names and folder path.")

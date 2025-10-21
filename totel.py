import streamlit as st
import pandas as pd
import plotly.express as px

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(page_title="Sales & Profit Dashboard", layout="wide")
st.title("📊 Monthly Sales & Profit Dashboard (2025)")

# ================================
# LOAD EXCEL FILE (CHANGE NAME IF NEEDED)
# ================================
FILE_PATH = "salestillsep.xlsx"  # 👈 change to your actual Excel filename
df = pd.read_excel(FILE_PATH)
df.columns = df.columns.str.strip()

# ================================
# CLEANUP & TRANSFORM
# ================================
months = [
    "Jan-2025", "Feb-2025", "Mar-2025", "Apr-2025", "May-2025",
    "Jun-2025", "Jul-2025", "Aug-2025", "Sep-2025"
]

sales_cols = [f"{m} Total Sales" for m in months if f"{m} Total Sales" in df.columns]
profit_cols = [f"{m} Total Profit" for m in months if f"{m} Total Profit" in df.columns]

# Convert wide to long format
melted_sales = df.melt(
    id_vars=["Category", "outlet"],
    value_vars=sales_cols,
    var_name="Month",
    value_name="Total Sales"
)
melted_profit = df.melt(
    id_vars=["Category", "outlet"],
    value_vars=profit_cols,
    var_name="Month",
    value_name="Total Profit"
)

# Merge both
long_df = pd.merge(melted_sales, melted_profit, on=["Category", "outlet", "Month"], how="left")
long_df["Month"] = long_df["Month"].str.replace(" Total Sales", "", regex=False)

# ================================
# TOTAL SUMMARY
# ================================
st.subheader("🌍 Overall Performance Summary")

total_sales = long_df["Total Sales"].sum()
total_profit = long_df["Total Profit"].sum()
avg_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales (All Outlets)", f"{total_sales:,.2f}")
col2.metric("📈 Total Profit", f"{total_profit:,.2f}")
col3.metric("💹 Avg. Profit Margin", f"{avg_margin:.2f}%")

# ================================
# FILTERS
# ================================
st.divider()
st.subheader("🎯 Filter Data")

outlets = ["All"] + sorted(long_df["outlet"].unique().tolist())
selected_outlet = st.selectbox("🏪 Select Outlet", outlets)

categories = sorted(long_df["Category"].unique().tolist())
selected_category = st.multiselect("📦 Select Category", categories, default=categories)

filtered_df = long_df.copy()
if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["outlet"] == selected_outlet]
if selected_category:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_category)]

# ================================
# OUTLET-WISE CATEGORY SALES
# ================================
st.divider()
st.subheader("🏷️ Outlet-wise Category Sales")

outlet_category_sales = (
    filtered_df.groupby(["outlet", "Category"], as_index=False)["Total Sales"]
    .sum()
    .sort_values("Total Sales", ascending=False)
)

fig = px.bar(
    outlet_category_sales,
    x="outlet",
    y="Total Sales",
    color="Category",
    text_auto=".2s",
    barmode="stack",
    title="Outlet-wise Category Sales (2025)",
    color_discrete_sequence=px.colors.qualitative.Safe
)
fig.update_layout(height=550, xaxis_title="Outlet", yaxis_title="Total Sales")
st.plotly_chart(fig, use_container_width=True)

# ================================
# MONTHLY TREND (OPTIONAL)
# ================================
st.divider()
st.subheader("📆 Monthly Sales Trend")

monthly_sales = (
    filtered_df.groupby(["Month", "outlet"], as_index=False)["Total Sales"]
    .sum()
    .sort_values("Month")
)

fig2 = px.line(
    monthly_sales,
    x="Month",
    y="Total Sales",
    color="outlet",
    markers=True,
    title="Monthly Sales Trend by Outlet"
)
fig2.update_traces(line=dict(width=3))
fig2.update_layout(height=450)
st.plotly_chart(fig2, use_container_width=True)

# ================================
# DATA TABLE
# ================================
st.divider()
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df.style.format({
    "Total Sales": "{:,.2f}",
    "Total Profit": "{:,.2f}"
}))

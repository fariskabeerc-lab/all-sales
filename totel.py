import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="📊 Monthly Sales Dashboard", layout="wide")

# ============================================
# LOAD DATA
# ============================================
FILE_PATH = "jan to sep all.xlsx"  # change file name if needed
df = pd.read_excel(FILE_PATH)

# ============================================
# DATA CLEANING & TRANSFORMATION
# ============================================
month_order = [
    "Jan-2025", "Feb-2025", "Mar-2025", "Apr-2025",
    "May-2025", "Jun-2025", "Jul-2025", "Aug-2025", "Sep-2025"
]

# Melt the dataframe for visualization
sales_cols = [f"{m} Total Sales" for m in month_order]
profit_cols = [f"{m} Total Profit" for m in month_order]

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

# Merge sales and profit
merged_df = pd.merge(melted_sales, melted_profit, on=["Category", "outlet", "Month"])

# Extract month names correctly
merged_df["Month"] = merged_df["Month"].str.replace(" Total Sales", "")
merged_df["Month"] = pd.Categorical(merged_df["Month"], categories=month_order, ordered=True)

# ============================================
# FILTERS
# ============================================
st.sidebar.header("🔍 Filters")

# Filter 1: Outlet
outlet_options = ["All"] + sorted(merged_df["outlet"].unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlet_options)

# Filter 2: Category
category_options = ["All"] + sorted(merged_df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", category_options)

# Filter 3: Month
month_options = ["All"] + month_order
selected_month = st.sidebar.selectbox("Select Month", month_options)

# Apply filters one by one
filtered_df = merged_df.copy()
if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["outlet"] == selected_outlet]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
if selected_month != "All":
    filtered_df = filtered_df[filtered_df["Month"] == selected_month]

# ============================================
# METRICS
# ============================================
total_sales = filtered_df["Total Sales"].sum()
total_profit = filtered_df["Total Profit"].sum()

col1, col2 = st.columns(2)
col1.metric("💰 Total Sales", f"{total_sales:,.0f}")
col2.metric("📈 Total Profit", f"{total_profit:,.0f}")

# ============================================
# CHART
# ============================================
st.markdown("### 📊 Sales Overview")

if selected_month == "All":
    # Vertical bar chart by Month
    chart_data = (
        filtered_df.groupby("Month")["Total Sales"].sum().reset_index()
    )
    fig = px.bar(
        chart_data,
        x="Month",
        y="Total Sales",
        text_auto=".2s",
        title="Total Sales by Month",
    )
else:
    # Vertical bar chart by Category or Outlet
    if selected_outlet == "All":
        chart_data = (
            filtered_df.groupby("outlet")["Total Sales"].sum().reset_index()
        )
        fig = px.bar(
            chart_data,
            x="outlet",
            y="Total Sales",
            text_auto=".2s",
            title=f"Total Sales by Outlet ({selected_month})",
        )
    else:
        chart_data = (
            filtered_df.groupby("Category")["Total Sales"].sum().reset_index()
        )
        fig = px.bar(
            chart_data,
            x="Category",
            y="Total Sales",
            text_auto=".2s",
            title=f"Total Sales by Category ({selected_month})",
        )

fig.update_traces(textposition='outside')
fig.update_layout(xaxis_title="", yaxis_title="Total Sales", height=600)
st.plotly_chart(fig, use_container_width=True)

# ============================================
# KEY INSIGHTS
# ============================================
st.markdown("### 🧠 Key Insights")

top_category = (
    filtered_df.groupby("Category")["Total Sales"].sum().idxmax()
    if not filtered_df.empty else "N/A"
)
top_outlet = (
    filtered_df.groupby("outlet")["Total Sales"].sum().idxmax()
    if not filtered_df.empty else "N/A"
)
best_month = (
    filtered_df.groupby("Month")["Total Sales"].sum().idxmax()
    if not filtered_df.empty else "N/A"
)

st.write(f"🏆 **Top Category:** {top_category}")
st.write(f"🏬 **Top Outlet:** {top_outlet}")
st.write(f"📅 **Best Month:** {best_month}")

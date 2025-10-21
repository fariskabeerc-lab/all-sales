import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# ==============================
# Page Setup
# ==============================
st.set_page_config(page_title="Sales & Profit Dashboard", layout="wide")
st.title("📊 Monthly Sales & Profit Dashboard")

# ==============================
# Load Data
# ==============================
@st.cache_data
def load_data():
    df = pd.read_excel("jan to sep all.xlsx")  # <-- replace with your file
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ==============================
# Preprocess Columns
# ==============================
month_cols = [col for col in df.columns if "Total Sales" in col]
profit_cols = [col for col in df.columns if "Total Profit" in col]

month_order = []
for col in month_cols:
    month = col.split()[0]
    if month not in month_order:
        month_order.append(month)

sales_melted = df.melt(id_vars=["Category", "outlet"], value_vars=month_cols,
                       var_name="Month", value_name="Sales")
profit_melted = df.melt(id_vars=["Category", "outlet"], value_vars=profit_cols,
                        var_name="Month", value_name="Profit")

sales_melted["Month"] = sales_melted["Month"].str.extract(r"(\w+-\d{4})")
profit_melted["Month"] = profit_melted["Month"].str.extract(r"(\w+-\d{4})")

merged_df = pd.merge(sales_melted, profit_melted, on=["Category", "outlet", "Month"])

# ==============================
# Filters
# ==============================
st.sidebar.header("🔍 Filters")
categories = ["All"] + sorted(merged_df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

outlets = ["All"] + sorted(merged_df["outlet"].unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

months = ["All"] + month_order
selected_month = st.sidebar.selectbox("Select Month", months)

filtered_df = merged_df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["outlet"] == selected_outlet]
if selected_month != "All":
    filtered_df = filtered_df[filtered_df["Month"] == selected_month]

# ==============================
# Key Metrics
# ==============================
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"{total_sales:,.2f}")
col2.metric("📈 Total Profit", f"{total_profit:,.2f}")
col3.metric("📊 Profit Margin (%)", f"{profit_margin:.2f}%")
if selected_category != "All":
    avg_monthly_sales = filtered_df.groupby("Month")["Sales"].sum().mean()
    col4.metric("📅 Avg Monthly Sales", f"{avg_monthly_sales:,.2f}")

# ==============================
# Visualization
# ==============================

import plotly.graph_objects as go
import time

if selected_month == "All":
    # Show line charts for all months
    st.markdown("### 📦 Sales & Profit Trend by Month")

    monthly_summary = filtered_df.groupby("Month")[["Sales", "Profit"]].sum().reindex(month_order)

    # Sales line chart
    fig_sales = px.line(
        monthly_summary,
        x=monthly_summary.index,
        y="Sales",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["royalblue"],
        hover_data={"Sales": ":,.2f"},
        title="Total Sales Trend by Month"
    )
    fig_sales.update_traces(marker=dict(size=10, symbol="circle"), line=dict(width=4))
    fig_sales.update_layout(height=400, xaxis_title="Month", yaxis_title="Total Sales", template="plotly_white", title_x=0.5)
    st.plotly_chart(fig_sales, use_container_width=True)

    # Profit line chart
    fig_profit = px.line(
        monthly_summary,
        x=monthly_summary.index,
        y="Profit",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["green"],
        hover_data={"Profit": ":,.2f"},
        title="Total Profit Trend by Month"
    )
    fig_profit.update_traces(marker=dict(size=10, symbol="diamond"), line=dict(width=4))
    fig_profit.update_layout(height=400, xaxis_title="Month", yaxis_title="Total Profit", template="plotly_white", title_x=0.5)
    st.plotly_chart(fig_profit, use_container_width=True)

else:
    # Show vertical category-wise bar chart for single month
    st.markdown(f"### 📊 Category-wise Sales & Profit for {selected_month}")

    category_summary = filtered_df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()
    categories_list = category_summary["Category"].tolist()
    sales_values = category_summary["Sales"].tolist()
    profit_values = category_summary["Profit"].tolist()
    max_value = max(max(sales_values), max(profit_values)) * 1.2

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Sales", y=categories_list, x=[0]*len(sales_values),
                             orientation='h', marker_color="royalblue"))
    fig_bar.add_trace(go.Bar(name="Profit", y=categories_list, x=[0]*len(profit_values),
                             orientation='h', marker_color="green"))

    fig_bar.update_layout(
        barmode="group",
        xaxis=dict(title="Amount", range=[0, max_value]),
        yaxis=dict(title="Category", autorange="reversed"),
        template="plotly_white",
        height=600
    )

    chart = st.plotly_chart(fig_bar, use_container_width=True)

    # Animate bars faster
    steps = 15  # fewer steps for faster animation
    delay = 0.03  # shorter delay
    for i in range(1, steps + 1):
        fig_bar.data[0].x = [v * i / steps for v in sales_values]
        fig_bar.data[1].x = [v * i / steps for v in profit_values]
        chart.plotly_chart(fig_bar, use_container_width=True)
        time.sleep(delay)

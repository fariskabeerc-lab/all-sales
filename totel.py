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
if selected_month != "All":
    st.markdown(f"### 📊 Animated Category-wise Sales & Profit for {selected_month}")
    category_summary = filtered_df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()
    
    categories_list = category_summary["Category"].tolist()
    sales_values = category_summary["Sales"].tolist()
    profit_values = category_summary["Profit"].tolist()
    
    # Set outer constant y-axis
    max_y = max(max(sales_values), max(profit_values)) * 1.2
    
    fig = go.Figure()
    
    # Initialize bars with zero height
    fig.add_trace(go.Bar(name="Sales", x=categories_list, y=[0]*len(sales_values), marker_color="royalblue"))
    fig.add_trace(go.Bar(name="Profit", x=categories_list, y=[0]*len(profit_values), marker_color="green"))
    
    fig.update_layout(
        barmode="group",
        xaxis_title="Category",
        yaxis_title="Amount",
        yaxis=dict(range=[0, max_y]),
        template="plotly_white",
        height=600,
    )
    
    # Animate bars by gradually increasing height
    chart = st.plotly_chart(fig, use_container_width=True)
    steps = 30  # number of animation steps
    for i in range(1, steps + 1):
        new_sales = [v * i/steps for v in sales_values]
        new_profit = [v * i/steps for v in profit_values]
        fig.data[0].y = new_sales
        fig.data[1].y = new_profit
        chart.plotly_chart(fig, use_container_width=True)
        time.sleep(0.05)  # small delay to simulate movement

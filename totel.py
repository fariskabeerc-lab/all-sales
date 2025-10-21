import streamlit as st
import pandas as pd
import plotly.express as px

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
    df = pd.read_excel("jan to sep all.xlsx")  # <-- replace with your file name
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ==============================
# Preprocess Columns
# ==============================
# Identify columns dynamically
month_cols = [col for col in df.columns if "Total Sales" in col]
profit_cols = [col for col in df.columns if "Total Profit" in col]

# Extract month names in correct order
month_order = []
for col in month_cols:
    month = col.split()[0]
    if month not in month_order:
        month_order.append(month)

# Melt data for better filtering
sales_melted = df.melt(id_vars=["Category", "outlet"], value_vars=month_cols,
                       var_name="Month", value_name="Sales")
profit_melted = df.melt(id_vars=["Category", "outlet"], value_vars=profit_cols,
                        var_name="Month", value_name="Profit")

# Clean month names
sales_melted["Month"] = sales_melted["Month"].str.extract(r"(\w+-\d{4})")
profit_melted["Month"] = profit_melted["Month"].str.extract(r"(\w+-\d{4})")

# Merge
merged_df = pd.merge(sales_melted, profit_melted, on=["Category", "outlet", "Month"])

# ==============================
# Filters
# ==============================
st.sidebar.header("🔍 Filters")

# Category Filter
categories = ["All"] + sorted(merged_df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Outlet Filter
outlets = ["All"] + sorted(merged_df["outlet"].unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

# Month Filter
months = ["All"] + month_order
selected_month = st.sidebar.selectbox("Select Month", months)

# ==============================
# Apply Filters
# ==============================
filtered_df = merged_df.copy()

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["outlet"] == selected_outlet]

if selected_month != "All":
    filtered_df = filtered_df[filtered_df["Month"] == selected_month]

# ==============================
# Key Insights
# ==============================
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"{total_sales:,.2f}")
col2.metric("📈 Total Profit", f"{total_profit:,.2f}")
col3.metric("📊 Profit Margin (%)", f"{profit_margin:.2f}%")

# Show average monthly sales if a category is selected
if selected_category != "All":
    avg_monthly_sales = filtered_df.groupby("Month")["Sales"].sum().mean()
    col4.metric("📅 Avg Monthly Sales", f"{avg_monthly_sales:,.2f}")

# ==============================
# Visualization
# ==============================
if selected_month == "All":
    st.markdown("### 📦 Sales Trend by Month")
    
    monthly_summary = (
        filtered_df.groupby("Month")[["Sales", "Profit"]].sum().reindex(month_order)
    )
    
    # Enhanced Line Chart for Sales
    fig = px.line(
        monthly_summary,
        x=monthly_summary.index,
        y="Sales",
        markers=True,
        title="Total Sales Trend by Month",
        line_shape="spline",  # smooth curve
        color_discrete_sequence=["royalblue"],
        hover_data={"Sales": ":,.2f"},
    )
    fig.update_traces(marker=dict(size=10, symbol="circle"), line=dict(width=4))
    fig.update_layout(height=500, xaxis_title="Month", yaxis_title="Total Sales", template="plotly_white", title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 💹 Profit Trend by Month")
    
    # Enhanced Line Chart for Profit
    fig2 = px.line(
        monthly_summary,
        x=monthly_summary.index,
        y="Profit",
        markers=True,
        title="Total Profit Trend by Month",
        line_shape="spline",
        color_discrete_sequence=["green"],
        hover_data={"Profit": ":,.2f"},
    )
    fig2.update_traces(marker=dict(size=10, symbol="diamond"), line=dict(width=4))
    fig2.update_layout(height=500, xaxis_title="Month", yaxis_title="Total Profit", template="plotly_white", title_x=0.5)
    st.plotly_chart(fig2, use_container_width=True)
    
else:
    # Single month selected: show category-wise Sales and Profit bar chart
    st.markdown(f"### 📊 Category-wise Sales & Profit for {selected_month}")
    category_summary = filtered_df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()
    
    fig = px.bar(
        category_summary,
        x="Category",
        y=["Sales", "Profit"],
        barmode="group",
        text_auto=True,
        title=f"Category-wise Sales & Profit ({selected_month})",
        color_discrete_sequence=["royalblue", "green"]
    )
    fig.update_layout(height=500, xaxis_title="Category", yaxis_title="Amount", template="plotly_white", title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# Data Table
# ==============================
st.markdown("### 📋 Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

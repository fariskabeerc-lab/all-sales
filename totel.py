import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# Page Setup
# ==============================
st.set_page_config(page_title="Sales & Profit Dashboard", layout="wide")
st.title("📊Al Madina : Monthly Sales & Profit")

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
# Sidebar Filters
# ==============================
st.sidebar.header("🔍 Filters")
categories = ["All"] + sorted(merged_df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

outlets = ["All"] + sorted(merged_df["outlet"].unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

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
# Metrics
# ==============================
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

# Determine if Avg Monthly Sales should be shown
show_avg = (selected_category != "All" or (selected_outlet != "All" and selected_category == "All"))

# Create columns dynamically
if show_avg:
    col1, col2, col3, col4 = st.columns(4)
else:
    col1, col2, col3 = st.columns(3)

# Display metrics
col1.metric("💰 Total Sales", f"{total_sales:,.2f}")
col2.metric("📈 Total Profit (GP)", f"{total_profit:,.2f}")
col3.metric("📊 Profit Margin (%)", f"{profit_margin:.2f}%")

if show_avg:
    avg_monthly_sales = filtered_df.groupby("Month")["Sales"].sum().mean()
    col4.metric("📅 Avg Monthly Sales", f"{avg_monthly_sales:,.2f}")

# ==============================
# Visualizations
# ==============================
if selected_month == "All":
    # Line charts for all months
    st.markdown("### 📦 Sales Trend by Month")
    monthly_summary = filtered_df.groupby("Month")[["Sales", "Profit"]].sum().reindex(month_order)

    fig = px.line(
        monthly_summary,
        x=monthly_summary.index,
        y="Sales",
        markers=True,
        line_shape="linear",
        title="Total Sales by Month",
        color_discrete_sequence=["royalblue"]
    )
    fig.update_traces(line=dict(width=4), marker=dict(size=8))
    fig.update_layout(height=500, xaxis_title="Month", yaxis_title="Total Sales", template="plotly_white", title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 💹 Profit Trend by Month")
    fig2 = px.line(
        monthly_summary,
        x=monthly_summary.index,
        y="Profit",
        markers=True,
        line_shape="linear",
        title="Total Profit by Month",
        color_discrete_sequence=["green"]
    )
    fig2.update_traces(line=dict(width=4), marker=dict(size=8))
    fig2.update_layout(height=500, xaxis_title="Month", yaxis_title="Total Profit", template="plotly_white", title_x=0.5)
    st.plotly_chart(fig2, use_container_width=True)

else:
    # Horizontal category-wise bar chart for single month
    st.subheader(f"📊 Category-wise Sales & Profit for {selected_month}")

    category_summary = filtered_df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()
    category_summary = category_summary.sort_values("Sales", ascending=True)

    # 🔹 Add GP% and Market Share %
    category_summary["GP%"] = (category_summary["Profit"] / category_summary["Sales"] * 100).round(2)
    total_filtered_sales = category_summary["Sales"].sum()
    category_summary["Market Share (%)"] = (category_summary["Sales"] / total_filtered_sales * 100).round(2)

    max_value = max(category_summary["Sales"].max(), category_summary["Profit"].max()) * 1.2

    fig_bar = go.Figure()
    custom_hover = category_summary[["Sales", "Profit", "GP%", "Market Share (%)"]].values

    fig_bar.add_trace(go.Bar(
        y=category_summary["Category"],
        x=category_summary["Sales"],
        name="Sales",
        orientation="h",
        text=category_summary["Sales"],
        textposition="outside",
        marker_color="red",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Sales: %{x:,.0f}<br>Profit: %{customdata[1]:,.0f}<br>GP%: %{customdata[2]}%<br>Market Share: %{customdata[3]}%<extra></extra>",
        customdata=custom_hover
    ))
    fig_bar.add_trace(go.Bar(
        y=category_summary["Category"],
        x=category_summary["Profit"],
        name="Profit (GP)",
        orientation="h",
        text=category_summary["Profit"],
        textposition="outside",
        marker_color="green",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Sales: %{customdata[0]:,.0f}<br>Profit: %{x:,.0f}<br>GP%: %{customdata[2]}%<br>Market Share: %{customdata[3]}%<extra></extra>",
        customdata=custom_hover
    ))

    # Dynamic height
    num_categories = category_summary.shape[0]
    if num_categories <= 3:
        chart_height = 400
    elif num_categories <= 6:
        chart_height = 600
    else:
        chart_height = 850

    fig_bar.update_layout(
        barmode="group",
        bargap=0.3,
        xaxis=dict(title="Amount", range=[0, max_value], tickfont=dict(size=14)),
        yaxis=dict(title="Category", tickfont=dict(size=14), automargin=True),
        height=chart_height,
        template="plotly_white",
        margin=dict(l=220, r=50, t=50, b=50),
        legend=dict(font=dict(size=14)),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ==============================
# Outlet-wise Sales & GP% chart when a category is selected
# ==============================
if selected_category != "All" and selected_outlet == "All":
    st.subheader(f"📊 Outlet-wise Sales & GP% for Category: {selected_category}")

    outlet_summary = filtered_df.groupby("outlet")[["Sales", "Profit"]].sum().reset_index()
    outlet_summary = outlet_summary.sort_values("Sales", ascending=True)

    # 🔹 Calculate GP% and Market Share %
    outlet_summary["GP%"] = (outlet_summary["Profit"] / outlet_summary["Sales"] * 100).round(2)
    total_outlet_sales = outlet_summary["Sales"].sum()
    outlet_summary["Market Share (%)"] = (outlet_summary["Sales"] / total_outlet_sales * 100).round(2)

    # Create figure
    fig_outlet = go.Figure()

    # Sales Bar
    fig_outlet.add_trace(go.Bar(
        y=outlet_summary["outlet"],
        x=outlet_summary["Sales"],
        name="Sales",
        orientation="h",
        marker_color="red",
        text=outlet_summary["Sales"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Sales: %{x:,.0f}<br>GP%: %{customdata[1]}%<br>Market Share: %{customdata[2]}%<extra></extra>",
        customdata=outlet_summary[["Sales", "GP%", "Market Share (%)"]].values
    ))

    # GP% Line
    fig_outlet.add_trace(go.Scatter(
        y=outlet_summary["outlet"],
        x=outlet_summary["GP%"],
        name="GP%",
        mode='lines+markers+text',
        text=outlet_summary["GP%"].astype(str) + '%',
        textposition="top center",
        line=dict(color='green', width=3),
        marker=dict(size=10),
        hovertemplate="<b>%{y}</b><br>GP%: %{x}%<extra></extra>"
    ))

    # Dynamic height based on number of outlets
    num_outlets = outlet_summary.shape[0]
    if num_outlets <= 3:
        chart_height_outlet = 400
    elif num_outlets <= 6:
        chart_height_outlet = 600
    else:
        chart_height_outlet = 850

    fig_outlet.update_layout(
        height=chart_height_outlet,
        template='plotly_white',
        margin=dict(l=220, r=50, t=50, b=50),
        xaxis=dict(title='Sales / GP%'),
        yaxis=dict(title='Outlet', automargin=True),
        legend=dict(font=dict(size=14))
    )

    st.plotly_chart(fig_outlet, use_container_width=True)


# ==============================
# Data Table
# ==============================
st.markdown("### 📋 Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

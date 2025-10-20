import streamlit as st
import pandas as pd
import os

# ===============================
# CONFIGURATION
# ===============================
st.set_page_config(page_title="🔒 Sales & Profit Dashboard", layout="wide")

# --- Outlet Mapping ---
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

# ===============================
# PASSWORD PROTECTION
# ===============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("🔑 Enter Password to Access Dashboard", type="password")
    if st.button("Login"):
        if password == "123123":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password. Try again.")
    st.stop()

# ===============================
# LOAD ALL DATA
# ===============================
@st.cache_data
def load_all_outlet_data():
    all_data = []
    for outlet, file in OUTLET_FILES.items():
        if os.path.exists(file):
            df = pd.read_excel(file)
            df["Outlet"] = outlet
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

df = load_all_outlet_data()

# Remove items without category
df = df[df["Category"].notna()]

# Ensure numeric
for col in ["Total Sales", "Total Profit"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Margin %"] = df["Total Profit"] / df["Total Sales"] * 100
df["Margin %"] = df["Margin %"].fillna(0).round(2)

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("🔍 Filters")

# Category Filter
categories = ["All"] + sorted(df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Outlet Filter
outlets = ["All"] + sorted(df["Outlet"].unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

# Margin Filter
margin_filters = ["All", "< 0", "< 5", "10 - 20", "20 - 30", "30 +"]
selected_margin = st.sidebar.selectbox("Select Margin Range (%)", margin_filters)

# Apply Filters
filtered_df = df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["Outlet"] == selected_outlet]
if selected_margin != "All":
    if selected_margin == "< 0":
        filtered_df = filtered_df[filtered_df["Margin %"] < 0]
    elif selected_margin == "< 5":
        filtered_df = filtered_df[filtered_df["Margin %"] < 5]
    elif selected_margin == "10 - 20":
        filtered_df = filtered_df[(filtered_df["Margin %"] >= 10) & (filtered_df["Margin %"] < 20)]
    elif selected_margin == "20 - 30":
        filtered_df = filtered_df[(filtered_df["Margin %"] >= 20) & (filtered_df["Margin %"] < 30)]
    elif selected_margin == "30 +":
        filtered_df = filtered_df[filtered_df["Margin %"] >= 30]

# ===============================
# SEARCH BAR (Sticky on top)
# ===============================
st.markdown("""
    <style>
    div[data-testid="stToolbar"] {visibility: hidden;}
    .search-bar {
        position: fixed;
        top: 0;
        background-color: white;
        width: 100%;
        z-index: 1000;
        padding: 15px 0;
        border-bottom: 1px solid #ddd;
    }
    .stApp { margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="search-bar">', unsafe_allow_html=True)
search_term = st.text_input("🔎 Search Item Name", placeholder="Type an item name...")
st.markdown('</div>', unsafe_allow_html=True)

if search_term:
    filtered_df = filtered_df[filtered_df["Items"].str.contains(search_term, case=False, na=False)]

# ===============================
# KEY INSIGHTS
# ===============================
if not filtered_df.empty:
    total_sales = filtered_df["Total Sales"].sum()
    total_profit = filtered_df["Total Profit"].sum()
    avg_margin = filtered_df["Margin %"].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Sales", f"{total_sales:,.2f}")
    c2.metric("📈 Total Profit", f"{total_profit:,.2f}")
    c3.metric("⚙️ Avg. Margin %", f"{avg_margin:.2f}%")
else:
    st.warning("No data found for the selected filters or search term.")

# ===============================
# ITEM-WISE DETAILS
# ===============================
st.subheader("📋 Item-wise Sales, Profit & Margin")

if not filtered_df.empty:
    st.dataframe(
        filtered_df[["Outlet", "Category", "Items", "Total Sales", "Total Profit", "Margin %"]]
        .sort_values(by="Margin %", ascending=True)
        .reset_index(drop=True),
        use_container_width=True,
        height=400
    )

# ===============================
# OUTLET-WISE TOTALS
# ===============================
st.subheader("🏪 Outlet-wise Total Sales, Profit & Avg Margin")

if not filtered_df.empty:
    outlet_summary = (
        filtered_df.groupby("Outlet")
        .agg({"Total Sales": "sum", "Total Profit": "sum", "Margin %": "mean"})
        .reset_index()
        .sort_values("Total Sales", ascending=False)
    )
    st.dataframe(outlet_summary, use_container_width=True, height=300)
else:
    st.info("No outlet data to display.")

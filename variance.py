Vimport streamlit as st
import pandas as pd
import os

# ======================
# AUTHENTICATION
# ======================
st.set_page_config(page_title="All Outlets Dashboard", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Secure Access")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == "123123":
            st.session_state["authenticated"] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    st.stop()

# ======================
# LOAD DATA
# ======================
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

@st.cache_data
def load_all_data():
    all_data = []
    for outlet, file in OUTLET_FILES.items():
        if os.path.exists(file):
            df = pd.read_excel(file)
            df["Outlet"] = outlet
            all_data.append(df)
        else:
            st.warning(f"⚠️ File not found: {file}")
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

df = load_all_data()

if df.empty:
    st.error("No data files found. Please make sure all outlet Excel files are in the same folder.")
    st.stop()

# Normalize column names
df.columns = df.columns.str.strip()
if "Excise Margin (%)" not in df.columns:
    df["Excise Margin (%)"] = ((df["Total Profit"] / df["Total Sales"]) * 100).round(2)

# ======================
# SIDEBAR FILTERS
# ======================
st.sidebar.header("🔍 Filters")

# Category Filter
categories = ["All"] + sorted(df["Category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)
if selected_category != "All":
    df = df[df["Category"] == selected_category]

# Outlet Filter
outlets = ["All"] + sorted(df["Outlet"].unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)
if selected_outlet != "All":
    df = df[df["Outlet"] == selected_outlet]

# Margin Filter
margin_options = [
    "All",
    "< 0%",
    "< 5%",
    "10–20%",
    "20–30%",
    "30%+"
]
selected_margin = st.sidebar.selectbox("Select Margin Range", margin_options)

if selected_margin != "All":
    if selected_margin == "< 0%":
        df = df[df["Excise Margin (%)"] < 0]
    elif selected_margin == "< 5%":
        df = df[df["Excise Margin (%)"] < 5]
    elif selected_margin == "10–20%":
        df = df[(df["Excise Margin (%)"] >= 10) & (df["Excise Margin (%)"] < 20)]
    elif selected_margin == "20–30%":
        df = df[(df["Excise Margin (%)"] >= 20) & (df["Excise Margin (%)"] < 30)]
    elif selected_margin == "30%+":
        df = df[df["Excise Margin (%)"] >= 30]

# ======================
# SEARCH BAR
# ======================
search_term = st.text_input("🔎 Search for an Item:")
if search_term:
    df = df[df["Items"].astype(str).str.contains(search_term, case=False, na=False)]

# ======================
# KEY INSIGHTS (TOP)
# ======================
total_sales = df["Total Sales"].sum()
total_profit = df["Total Profit"].sum()
avg_margin = df["Excise Margin (%)"].mean()

st.markdown("### 📊 Key Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"{total_sales:,.2f}")
col2.metric("Total Profit", f"{total_profit:,.2f}")
col3.metric("Average Margin (%)", f"{avg_margin:.2f}%")

# ======================
# ITEM-LEVEL TABLE
# ======================
st.markdown("### 🧾 Item-wise Details")
st.dataframe(
    df[["Outlet", "Item Code", "Items", "Category", "Total Sales", "Total Profit", "Excise Margin (%)"]],
    use_container_width=True
)

# ======================
# OUTLET-WISE TOTALS TABLE
# ======================
st.markdown("### 🏬 Outlet-wise Total Sales, Profit & Avg Margin")
outlet_summary = (
    df.groupby("Outlet")[["Total Sales", "Total Profit"]]
    .sum()
    .reset_index()
)
outlet_summary["Avg Margin (%)"] = (
    df.groupby("Outlet")["Excise Margin (%)"].mean().values.round(2)
)
st.dataframe(outlet_summary, use_container_width=True)

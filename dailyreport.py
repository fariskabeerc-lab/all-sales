import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Outlet Dashboard", layout="wide")

# ==========================================
# SESSION STATE INIT
# ==========================================
for key in ["logged_in", "selected_outlet", "page", "customer_feedback"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else []

# Feedback keys
for key in ["feedback_name", "feedback_text", "feedback_rating"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "feedback_rating" else 3

# ==========================================
# LOGIN SIMULATION
# ==========================================
outlets = ["Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl"]
password = "123123"

if not st.session_state.logged_in:
    st.title("🔐 Outlet Login")
    username = st.text_input("Username")
    outlet = st.selectbox("Select Outlet", outlets)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "almadina" and pwd == password:
            st.session_state.logged_in = True
            st.session_state.selected_outlet = outlet
            st.session_state.page = "Customer Feedback"
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ==========================================
# DASHBOARD
# ==========================================
if st.session_state.logged_in:

    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.session_state.page = st.sidebar.radio("Go to", ["Customer Feedback", "Outlet Form"])

    # ==========================================
    # CUSTOMER FEEDBACK PAGE
    # ==========================================
    if st.session_state.page == "Customer Feedback":
        st.header(f"💬 Customer Feedback - {st.session_state.selected_outlet}")

        # Feedback form
        name = st.text_input("Customer Name", key="feedback_name")
        feedback = st.text_area("Feedback / Comments", key="feedback_text")

        # Slider rating
        labels = ["Very Bad", "Bad", "Neutral", "Good", "Excellent"]
        rating = st.slider("Rating", min_value=1, max_value=5, value=st.session_state.feedback_rating, key="feedback_rating")
        st.write(f"**Selected Rating:** {labels[rating-1]}")

        # Submit
        if st.button("📤 Submit Feedback"):
            # Save feedback
            st.session_state.customer_feedback.append({
                "Customer Name": name,
                "Feedback": feedback,
                "Rating": labels[rating-1],
                "Outlet": st.session_state.selected_outlet,
                "Date": datetime.now().strftime("%d-%b-%Y %H:%M")
            })
            st.success("✅ Feedback submitted successfully!")

            # Instead of direct assignment, use a temporary flag to clear after rerun
            st.session_state["clear_feedback_form"] = True
            st.experimental_rerun()

        # Clear after rerun
        if st.session_state.get("clear_feedback_form", False):
            st.session_state.update({
                "feedback_name": "",
                "feedback_text": "",
                "feedback_rating": 3
            })
            st.session_state["clear_feedback_form"] = False

    # ==========================================
    # LOGOUT
    # ==========================================
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

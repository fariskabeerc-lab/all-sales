import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Customer Feedback Form",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("📝 Customer Feedback Form")
st.markdown("Please share your experience with our outlet below.")

# Store submitted feedback in session state
if "submitted_feedback" not in st.session_state:
    st.session_state.submitted_feedback = []

# --- Use a form with clear_on_submit=True ---
# This parameter ensures all form widgets reset to their default values after a successful submission.
with st.form("feedback_form", clear_on_submit=True):
    # Use keys for all widgets for Streamlit best practices, even though the values are read locally.
    name = st.text_input("Customer Name", key="form_name")
    email = st.text_input("Email (Optional)", key="form_email")
    
    # Rating slider defaults to 5
    rating = st.slider(
        "Rate Your Experience", 
        min_value=1, 
        max_value=5, 
        value=5, 
        step=1, 
        key="form_rating",
        help="1 = Poor, 5 = Excellent"
    )
    
    feedback = st.text_area("Your Detailed Feedback (Required)", key="form_feedback")
    
    # Custom styling for the submit button
    submitted = st.form_submit_button("📤 Submit Feedback")

# Handle submission
if submitted:
    # Validate that required fields (Name and Feedback) are filled
    if name.strip() and feedback.strip():
        # Append the new feedback to the session state list
        st.session_state.submitted_feedback.append({
            "Customer Name": name,
            "Email": email if email else "N/A",
            "Rating": f"{rating} / 5",
            "Feedback": feedback,
            "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success("✅ Feedback submitted successfully! The form has been cleared.")
        
    else:
        st.error("⚠️ Submission failed. Please provide your **Customer Name** and **Detailed Feedback**.")

# --- Display all feedback ---
if st.session_state.submitted_feedback:
    st.markdown("---")
    st.markdown("### 🗂 Recent Feedback Records")
    
    # Convert the list of dicts to a pandas DataFrame for a better display widget
    df = pd.DataFrame(st.session_state.submitted_feedback)
    
    # Reverse the order to show the latest submission first
    st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
    
    # Provide an option to clear all collected data (for demonstration purposes)
    if st.button("🗑 Clear All Feedback", type="primary"):
        st.session_state.submitted_feedback = []
        st.rerun()

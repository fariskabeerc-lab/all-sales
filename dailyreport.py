import streamlit as st
from datetime import datetime

st.title("📝 Customer Feedback Form")

# Initialize submitted feedback list
if "submitted_feedback" not in st.session_state:
    st.session_state.submitted_feedback = []

with st.form("feedback_form"):
    name = st.text_input("Customer Name")
    email = st.text_input("Email (Optional)")
    rating = st.slider("Rate Our Outlet", 1, 5, 5)
    feedback = st.text_area("Your Feedback")

    submitted = st.form_submit_button("📤 Submit Feedback")

if submitted:
    if name.strip() and feedback.strip():
        st.session_state.submitted_feedback.append({
            "Customer Name": name,
            "Email": email,
            "Rating": rating,
            "Feedback": feedback,
            "Submitted At": datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        })
        st.success("✅ Feedback submitted successfully!")
        # The form automatically clears after submit
    else:
        st.warning("⚠️ Please fill at least your name and feedback.")

# Display all feedback
if st.session_state.submitted_feedback:
    st.markdown("### 🗂 Submitted Feedback")
    st.dataframe(st.session_state.submitted_feedback, use_container_width=True)

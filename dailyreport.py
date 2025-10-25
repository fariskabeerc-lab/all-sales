import streamlit as st
from datetime import datetime

st.title("📝 Customer Feedback Form")

# Initialize submitted feedback list
if "submitted_feedback" not in st.session_state:
    st.session_state.submitted_feedback = []

# Initialize input keys if not exists
for key in ["customer_name", "customer_email", "rating", "feedback"]:
    if key not in st.session_state:
        if key == "rating":
            st.session_state[key] = 5
        else:
            st.session_state[key] = ""

with st.form("feedback_form"):
    # Notice: we only set key, not value
    name = st.text_input("Customer Name", key="customer_name")
    email = st.text_input("Email (Optional)", key="customer_email")
    rating = st.slider("Rate Our Outlet", 1, 5, key="rating")
    feedback = st.text_area("Your Feedback", key="feedback")

    submitted = st.form_submit_button("📤 Submit Feedback")

if submitted:
    if name.strip() and feedback.strip():
        # Append feedback
        st.session_state.submitted_feedback.append({
            "Customer Name": name,
            "Email": email,
            "Rating": rating,
            "Feedback": feedback,
            "Submitted At": datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        })
        st.success("✅ Feedback submitted successfully!")

        # CLEAR FORM INPUTS by resetting session_state keys
        st.session_state.customer_name = ""
        st.session_state.customer_email = ""
        st.session_state.rating = 5
        st.session_state.feedback = ""
    else:
        st.warning("⚠️ Please fill at least your name and feedback.")

# Display all feedback
if st.session_state.submitted_feedback:
    st.markdown("### 🗂 Submitted Feedback")
    st.dataframe(st.session_state.submitted_feedback, use_container_width=True)

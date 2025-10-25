import streamlit as st
from datetime import datetime

st.title("📝 Customer Feedback Form")

# Initialize submitted feedback list
if "submitted_feedback" not in st.session_state:
    st.session_state.submitted_feedback = []

if "form_counter" not in st.session_state:
    st.session_state.form_counter = 0  # Will increase each submission

with st.form(f"feedback_form_{st.session_state.form_counter}"):
    name = st.text_input("Customer Name", key=f"name_{st.session_state.form_counter}")
    email = st.text_input("Email (Optional)", key=f"email_{st.session_state.form_counter}")
    rating = st.slider("Rate Our Outlet", 1, 5, 5, key=f"rating_{st.session_state.form_counter}")
    feedback = st.text_area("Your Feedback", key=f"feedback_{st.session_state.form_counter}")

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
        # Increment counter to reset form
        st.session_state.form_counter += 1
    else:
        st.warning("⚠️ Please fill at least your name and feedback.")

# Display all feedback
if st.session_state.submitted_feedback:
    st.markdown("### 🗂 Submitted Feedback")
    st.dataframe(st.session_state.submitted_feedback, use_container_width=True)

import streamlit as st
from datetime import datetime

# Initialize session_state keys safely at the top
for key in ["feedback_name", "feedback_text", "feedback_rating", "clear_feedback_form", "customer_feedback"]:
    if key not in st.session_state:
        if key == "feedback_rating":
            st.session_state[key] = 3
        elif key == "customer_feedback":
            st.session_state[key] = []
        else:
            st.session_state[key] = ""
st.session_state.setdefault("clear_feedback_form", False)

st.title("💬 Customer Feedback")

# Feedback Form
name = st.text_input("Customer Name", key="feedback_name")
feedback = st.text_area("Feedback", key="feedback_text")
rating = st.slider("Rating (1=Very Bad, 5=Excellent)", 1, 5, key="feedback_rating")

# Submit Button
if st.button("Submit Feedback"):
    st.session_state.customer_feedback.append({
        "Name": name,
        "Feedback": feedback,
        "Rating": rating,
        "Date": datetime.now().strftime("%d-%b-%Y %H:%M")
    })
    st.success("✅ Feedback submitted!")
    st.session_state.clear_feedback_form = True
    st.experimental_rerun()  # rerun safely

# Clear the form after rerun
if st.session_state.clear_feedback_form:
    st.session_state.feedback_name = ""
    st.session_state.feedback_text = ""
    st.session_state.feedback_rating = 3
    st.session_state.clear_feedback_form = False

# Optional: Display feedback (for demo)
st.markdown("### Submitted Feedback (demo)")
st.write(st.session_state.customer_feedback)

import streamlit as st
import requests

st.title("LLaMA Text Summarizer")

user_input = st.text_area("Enter your text here:")

if st.button("Summarize"):
    response = requests.post(
        "http://localhost:8000/summarize/",
        data={"text": user_input}
    )
    summary = response.json().get("summary", "Error generating summary.")
    st.subheader("Summary:")
    st.write(summary)

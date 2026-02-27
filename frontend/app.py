import streamlit as st
import requests

st.title("LLaMA Text Summarizer")

user_input = st.text_area("Enter your text here:")

if st.button("Summarize"):
    if not user_input.strip():
        st.warning("Please enter some text first.")
    else:
        try:
            response = requests.post(
                "http://localhost:8000/summarize/",
                data={"text": user_input},
                timeout=60,
            )
            response.raise_for_status()
            summary = response.json().get("summary", "Error generating summary.")
            st.subheader("Summary:")
            st.write(summary)
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend at http://localhost:8000. Start FastAPI first.")
        except requests.exceptions.Timeout:
            st.error("Request timed out. The model may be busy; try again.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")

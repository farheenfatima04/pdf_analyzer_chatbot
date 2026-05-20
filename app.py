import streamlit as st
import pdfplumber
from openai import OpenAI

# ------------------------------
# API Key Setup (Streamlit Secrets)
# ------------------------------
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# ------------------------------
# Extract text from PDF
# ------------------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# ------------------------------
# Initialize session state
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# ------------------------------
# Streamlit App
# ------------------------------
def main():
    st.title("📄 PDF Chatbot with AI")

    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file:
        # Extract text only once
        if not st.session_state.pdf_text:
            st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)

            if not st.session_state.pdf_text.strip():
                st.error("No text could be extracted from this PDF.")
                return

            st.success("PDF loaded successfully! Start chatting below.")

        # Show chat history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**AI:** {msg['content']}")

        # User input
        user_input = st.text_input("Type your question here...")

        if st.button("Send") and user_input:
            # Save user message
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )

            # System prompt + chat history
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Answer ONLY based on this PDF content:\n\n"
                        f"{st.session_state.pdf_text}"
                    )
                }
            ] + st.session_state.messages

            # OpenAI response
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7
                )

                answer = response.choices[0].message.content

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()

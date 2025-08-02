import streamlit as st
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px
import requests
import json

# ---------------- FRONT PAGE ----------------
def show_front_page():
    front_html = """
    <section class="hero">
      <div class="hero-text">
        <span class="tag">HIGH SCHOOL STUDENTS</span>
        <h1><span class="highlight">AI-Powered</span> Student Tools & <span class="highlight2">Lessons.</span></h1>
        <p>Study smarter with StudyMate – your intelligent study companion. Upload PDFs, ask questions, and generate quizzes with ease.</p>
        <a href="?page=app" class="cta-button">Start For Free</a>
      </div>
      <div class="hero-img">
        <img src="https://img.freepik.com/free-vector/smart-ai-technology-illustration_23-2149211072.jpg" alt="StudyMate Student AI" />
      </div>
    </section>
    <style>
    body {
      margin: 0;
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #0b0b3c, #003e4d);
      color: white;
    }
    .hero {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      padding: 4rem 2rem;
    }
    .hero-text {
      max-width: 550px;
    }
    .tag {
      background: #1dd1a1;
      color: #000;
      padding: 5px 10px;
      border-radius: 15px;
      font-size: 0.8rem;
      display: inline-block;
      margin-bottom: 1rem;
    }
    .hero-text h1 {
      font-size: 3rem;
      color: white;
      margin: 0;
    }
    .highlight { color: #ff6ec4; }
    .highlight2 { color: #48dbfb; }
    .hero-text p {
      margin: 1rem 0 2rem;
      line-height: 1.5;
      font-size: 1.1rem;
      color: #dcdcdc;
    }
    .cta-button {
      background: white;
      color: #000;
      border: none;
      padding: 0.9rem 2rem;
      font-size: 1rem;
      border-radius: 25px;
      cursor: pointer;
      font-weight: bold;
      text-decoration: none;
    }
    .hero-img img {
      max-width: 400px;
      width: 100%;
      border-radius: 15px;
    }
    @media (max-width: 768px) {
      .hero { flex-direction: column; text-align: center; }
      .hero-text, .hero-img { max-width: 100%; }
    }
    </style>
    """
    components.html(front_html, height=700, scrolling=False)

# ---------------- MAIN APP ----------------
def show_studymate_app():
    st.title("📚 Studymate: AI-powered PDF Q&A for Students")

    # Onboarding
    if "onboarded" not in st.session_state:
        st.session_state["onboarded"] = False

    if not st.session_state["onboarded"]:
        st.header("Welcome! Complete onboarding")
        if st.button("Finish Onboarding"):
            st.session_state["onboarded"] = True
            st.success("🎉 Onboarding complete!")
        st.stop()

    # PDF Upload
    uploaded_pdf = st.file_uploader("Upload your study PDF", type="pdf")
    pdf_text = ""
    if uploaded_pdf:
        with st.spinner("Extracting PDF..."):
            try:
                reader = PdfReader(uploaded_pdf)
                txt_chunks = [page.extract_text() for page in reader.pages if page.extract_text()]
                pdf_text = "".join(txt_chunks)
                st.success("✅ PDF loaded!")
                st.text_area("Extracted Text (Preview)", pdf_text[:1200]+"..." if len(pdf_text) > 1200 else pdf_text, height=150)
            except Exception as e:
                st.error(f"❌ Failed to read PDF: {e}")

    # Hugging Face Q&A
    hf_api_key = st.secrets.get("hf_api_key") or st.text_input("Paste your Hugging Face API Key:", type="password")
    headers = {"Authorization": f"Bearer {hf_api_key}"}

    if pdf_text and hf_api_key:
        st.subheader("💬 Ask your AI tutor about this PDF")
        question = st.text_input("Ask a question:")
        if st.button("Ask"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2",
                    headers=headers,
                    json={"inputs": {"question": question, "context": pdf_text[:3500]}}
                )
                if response.status_code == 200:
                    result = response.json()
                    st.markdown(f"*Answer:* {result.get('answer', 'Not found')}")
                else:
                    st.error("❌ Error from Hugging Face API.")

    # Quiz Generation
    if pdf_text and hf_api_key:
        if st.button("📘 Generate Quiz from PDF"):
            with st.spinner("Generating..."):
                prompt = f"""
Read the following and generate 3 multiple-choice questions. For each: 
- Provide question
- 4 options
- The correct answer
Format JSON:
[
  {{
    "question": "...",
    "choices": ["A", "B", "C", "D"],
    "answer": "B"
  }},
  ...
]
Content: \"\"\"{pdf_text[:2000]}\"\"\"
"""
                response = requests.post(
                    "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
                    headers=headers,
                    json={"inputs": prompt}
                )
                try:
                    quiz = json.loads(response.json()[0]["generated_text"])
                    st.session_state["quiz"] = quiz
                    st.success("✅ Quiz Ready!")
                except:
                    st.error("⚠ Could not parse the quiz. Try again or simplify the PDF.")

    # Quiz UI
    if "quiz" in st.session_state:
        st.subheader("📝 Quiz Time!")
        score = 0
        quiz = st.session_state["quiz"]
        for i, q in enumerate(quiz):
            st.write(f"*Q{i+1}:* {q['question']}")
            ans = st.radio("Options:", q['choices'], key=f"q_{i}")
            if st.button(f"Check Q{i+1}"):
                if ans == q['answer']:
                    st.success("✅ Correct!")
                    score += 1
                else:
                    st.warning(f"❌ Correct answer: {q['answer']}")
        if st.button("🎯 Finish Quiz"):
            st.success(f"Total Score: {score}/{len(quiz)}")
            st.balloons()

# ---------------- ROUTING ----------------
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["home"])[0]

if page == "home":
    show_front_page()
elif page == "app":
    show_studymate_app()

import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px
import requests

# ========== CONFIG ==========

# Google Analytics tracking (optional: replace with real ID if needed)
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date()); gtag('config', 'G-XXXXXXXXXX');
</script>
""", unsafe_allow_html=True)

# Custom styles
st.markdown("""
<style>
.animated-card { transition: box-shadow 0.3s; }
.animated-card:hover { box-shadow: 0 0 20px rgba(0,0,0,0.2); }
.big-font { font-size:30px !important; color:#4B8BBE; font-family:sans-serif; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Studymate: AI-powered PDF Q&A for Students")
st.markdown('<div class="big-font animated-card">Learn Smarter with AI</div>', unsafe_allow_html=True)

# ========== ONBOARDING ==========import streamlit as st
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px
import requests
import json

# --- HTML Frontpage (Hero Section) ---
frontpage_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>StudyMate - AI Q&A Tool</title>
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

    .highlight {
      color: #ff6ec4;
    }

    .highlight2 {
      color: #48dbfb;
    }

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

    .cta-note {
      margin-top: 0.5rem;
      font-size: 0.8rem;
      color: #a9a9a9;
    }

    .hero-img img {
      max-width: 400px;
      width: 100%;
      border-radius: 15px;
    }

    @media (max-width: 768px) {
      .hero {
        flex-direction: column;
        text-align: center;
      }
      .hero-text, .hero-img {
        max-width: 100%;
      }
    }
  </style>
</head>
<body>

  <section class="hero">
    <div class="hero-text">
      <span class="tag">HIGH SCHOOL & COLLEGE STUDENTS</span>
      <h1><span class="highlight">AI-Powered</span> Student Tools & <span class="highlight2">Lessons.</span></h1>
      <p>Study smarter with StudyMate – your intelligent study companion. Upload PDFs, ask questions, and generate quizzes with ease.</p>
      <a href="#app-section" class="cta-button">Start For Free</a>
    </div>

    <div class="hero-img">
      <img src="https://www.your-image-link.com" alt="StudyMate Student AI" />
    </div>
  </section>

</body>
</html>
"""

# --- Show HTML Frontpage in Streamlit ---
components.html(frontpage_html, height=800, scrolling=True)

# --- Streamlit App Below ---
st.markdown('<div id="app-section"></div>', unsafe_allow_html=True)
st.title("📚 Studymate: AI-powered PDF Q&A for Students")
st.markdown('<div class="big-font animated-card">Learn Smarter with AI</div>', unsafe_allow_html=True)

# ========== ONBOARDING ==========
if "onboarded" not in st.session_state:
    st.session_state["onboarded"] = False

if not st.session_state["onboarded"]:
    st.header("Welcome! Complete onboarding")
    st.write("A quick onboarding step to get you started.")
    if st.button("Finish Onboarding"):
        st.session_state["onboarded"] = True
        st.success("🎉 Onboarding complete!")
    st.stop()

# ========== PDF UPLOAD & TEXT EXTRACTION ==========
uploaded_pdf = st.file_uploader("Upload your study PDF", type="pdf")
pdf_text = ""
if uploaded_pdf:
    with st.spinner("Extracting PDF..."):
        try:
            reader = PdfReader(uploaded_pdf)
            txt_chunks = []
            for page in reader.pages:
                if page.extract_text():
                    txt_chunks.append(page.extract_text())
            pdf_text = "".join(txt_chunks)
            st.success("PDF loaded!")
            st.text_area("Extracted Text (Preview)", pdf_text[:1200]+"..." if len(pdf_text) > 1200 else pdf_text, height=150)
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")

# ========== AI Q&A with Hugging Face ==========
hf_api_key = st.secrets.get("hf_api_key") or st.text_input("Paste your Hugging Face API Key:", type="password", key="hf_key")
headers = {"Authorization": f"Bearer {hf_api_key}"}

if pdf_text and hf_api_key:
    st.subheader("Ask your AI tutor about this PDF")
    if "questions_asked" not in st.session_state:
        st.session_state["questions_asked"] = 0

    question = st.text_input("Type your question about the document:")
    if st.button("Ask"):
        with st.spinner("AI is thinking..."):
            payload = {
                "inputs": {
                    "question": question,
                    "context": pdf_text[:3500]
                }
            }
            response = requests.post(
                "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "Could not find a clear answer.")
                st.markdown(f"AI Answer: {answer}")
                st.session_state["questions_asked"] += 1
            else:
                st.error(f"❌ Hugging Face API error {response.status_code}: {response.text}")

# ========== QUIZ GENERATION ==========
if pdf_text and hf_api_key:
    if st.button("📘 Generate Quiz from this PDF"):
        with st.spinner("Generating quiz..."):
            quiz_prompt = f"""
Read the following content and generate 3 multiple-choice quiz questions based on it.
For each question, provide:
- the question text
- 4 answer options in a list
- the correct answer exactly as written in the options

Return your answer in JSON format like this:
[
  {{
    "question": "Question text?",
    "choices": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Correct Option"
  }},
  ...
]

Content:
\"\"\"
{pdf_text[:2000]}
\"\"\"
"""

            payload = {
                "inputs": quiz_prompt
            }

            response = requests.post(
                "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
                headers={"Authorization": f"Bearer {hf_api_key}"},
                json=payload
            )

            if response.status_code == 200:
                try:
                    result = response.json()
                    quiz_json = result[0]["generated_text"]
                    quiz = json.loads(quiz_json)

                    st.session_state["quiz"] = quiz  # Save for later use
                    st.success("✅ Quiz generated!")
                except Exception as e:
                    st.error("⚠ Could not parse the quiz. Try again or use simpler PDFs.")
                    st.text(result)
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

# ========== INTERACTIVE QUIZ SECTION ==========
if "quiz" in st.session_state:
    st.subheader("📝 Quiz Section")
    score = 0
    quiz = st.session_state["quiz"]
    for idx, q in enumerate(quiz):
        st.write(f"Q{idx+1}: {q['question']}")
        choice = st.radio(
            f"Choose your answer for Q{idx+1}:",
            q['choices'],
            key=f"quiz_choice_{idx}"
        )
        if st.button(f"Check Q{idx+1}", key=f"quiz_btn_{idx}"):
            if choice == q['answer']:
                st.success("✅ Correct!")
                score += 1
            else:
                st.warning(f"❌ Incorrect. Correct answer: {q['answer']}")
    if st.button("🎯 Finish Quiz"):
        st.success(f"Total Score: {score}/{len(quiz)}")
        st.balloons()

# ========== DASHBOARD ==========
if pdf_text:
    st.header("📊 Your Activity Dashboard")
    stats = [
        {"Action": "Questions", "Count": st.session_state.get("questions_asked", 0)},
        {"Action": "Quizzes", "Count": 1 if 'quiz' in globals() else 0}
    ]
    df = pd.DataFrame(stats)
    fig = px.bar(df, x="Action", y="Count", title="Your Progress")
    st.plotly_chart(fig, use_container_width=True)
if "onboarded" not in st.session_state:
    st.session_state["onboarded"] = False

if not st.session_state["onboarded"]:
    st.header("Welcome! Complete onboarding")
    st.write("A quick onboarding step to get you started.")
    if st.button("Finish Onboarding"):
        st.session_state["onboarded"] = True
        st.success("🎉 Onboarding complete!")
    st.stop()

# ========== PDF UPLOAD & TEXT EXTRACTION ==========
uploaded_pdf = st.file_uploader("Upload your study PDF", type="pdf")
pdf_text = ""
if uploaded_pdf:
    with st.spinner("Extracting PDF..."):
        try:
            reader = PdfReader(uploaded_pdf)
            txt_chunks = []
            for page in reader.pages:
                if page.extract_text():
                    txt_chunks.append(page.extract_text())
            pdf_text = "".join(txt_chunks)
            st.success("PDF loaded!")
            st.text_area("Extracted Text (Preview)", pdf_text[:1200]+"..." if len(pdf_text) > 1200 else pdf_text, height=150)
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")

# ========== AI Q&A with Hugging Face ==========
hf_api_key = st.secrets.get("hf_api_key") or st.text_input("Paste your Hugging Face API Key:", type="password", key="hf_key")
headers = {"Authorization": f"Bearer {hf_api_key}"}

if pdf_text and hf_api_key:
    st.subheader("Ask your AI tutor about this PDF")
    if "questions_asked" not in st.session_state:
        st.session_state["questions_asked"] = 0

    question = st.text_input("Type your question about the document:")
    if st.button("Ask"):
        with st.spinner("AI is thinking..."):
            payload = {
                "inputs": {
                    "question": question,
                    "context": pdf_text[:3500]
                }
            }
            response = requests.post(
                "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "Could not find a clear answer.")
                st.markdown(f"*AI Answer:* {answer}")
                st.session_state["questions_asked"] += 1
            else:
                st.error(f"❌ Hugging Face API error {response.status_code}: {response.text}")

# ========== QUIZ GENERATION & INTERACTIVE QUIZ ==========
import json

if pdf_text and hf_api_key:
    if st.button("📘 Generate Quiz from this PDF"):
        with st.spinner("Generating quiz..."):
            quiz_prompt = f"""
Read the following content and generate 3 multiple-choice quiz questions based on it.
For each question, provide:
- the question text
- 4 answer options in a list
- the correct answer exactly as written in the options

Return your answer in JSON format like this:
[
  {{
    "question": "Question text?",
    "choices": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Correct Option"
  }},
  ...
]

Content:
\"\"\"
{pdf_text[:2000]}
\"\"\"
"""

            payload = {
                "inputs": quiz_prompt
            }

            response = requests.post(
                "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
                headers={"Authorization": f"Bearer {hf_api_key}"},
                json=payload
            )

            if response.status_code == 200:
                try:
                    result = response.json()
                    quiz_json = result[0]["generated_text"]
                    quiz = json.loads(quiz_json)

                    st.session_state["quiz"] = quiz  # Save for later use
                    st.success("✅ Quiz generated!")
                except Exception as e:
                    st.error("⚠ Could not parse the quiz. Try again or use simpler PDFs.")
                    st.text(result)
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

# ========== INTERACTIVE QUIZ SECTION ==========
if "quiz" in st.session_state:
    st.subheader("📝 Quiz Section")
    score = 0
    quiz = st.session_state["quiz"]
    for idx, q in enumerate(quiz):
        st.write(f"Q{idx+1}: {q['question']}")
        choice = st.radio(
            f"Choose your answer for Q{idx+1}:",
            q['choices'],
            key=f"quiz_choice_{idx}"
        )
        if st.button(f"Check Q{idx+1}", key=f"quiz_btn_{idx}"):
            if choice == q['answer']:
                st.success("✅ Correct!")
                score += 1
            else:
                st.warning(f"❌ Incorrect. Correct answer: {q['answer']}")
    if st.button("🎯 Finish Quiz"):
        st.success(f"*Total Score: {score}/{len(quiz)}*")
        st.balloons()




# ========== DASHBOARD ==========
if pdf_text:
    st.header("📊 Your Activity Dashboard")
    stats = [
        {"Action": "Questions", "Count": st.session_state.get("questions_asked", 0)},
        {"Action": "Quizzes", "Count": 1 if 'quiz' in globals() else 0}
    ]
    df = pd.DataFrame(stats)
    fig = px.bar(df, x="Action", y="Count", title="Your Progress")
    st.plotly_chart(fig, use_container_width=True)
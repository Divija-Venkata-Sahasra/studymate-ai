import openai, streamlit as st
def generate_quiz(pdf_text):
    prompt = f"Generate 3 MCQs (options a-d, answer indicated) on: {pdf_text[:1000]}"
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": "Make quizzes."},
            {"role": "user", "content": prompt}
    ])
    return resp.choices[0].message.content

if st.button("Generate Quiz"):
    quiz = generate_quiz(text)
    st.text_area("Quiz", quiz, height=250)
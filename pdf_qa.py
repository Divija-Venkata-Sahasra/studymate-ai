import streamlit as st
import openai
from PyPDF2 import PdfReader

openai.api_key = st.secrets["openai_api_key"]

def extract_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "
".join(page.extract_text() for page in reader.pages if page.extract_text())

def ask_pdf(pdf_text, query):
    prompt = f"Content: '''{pdf_text}'''

Answer the following question: {query}"
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": "You answer questions based on provided content."},
            {"role": "user", "content": prompt}])
    return completion.choices[0].message.content.strip()
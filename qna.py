uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")
if uploaded_pdf:
    text = extract_text(uploaded_pdf)
    st.success("PDF loaded!")
    st.text_area("Extracted Content", text, height=150)
    question = st.text_input("Type your question about the PDF:")
    if st.button("Ask"):
        with st.spinner("Thinking..."):
            answer = ask_pdf(text, question)
            st.markdown(f"*AI Answer:* {answer}")
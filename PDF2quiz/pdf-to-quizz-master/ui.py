import streamlit as st
from ui_utils import check_password
from pdf_to_quizz import pdf_to_quizz
from text_to_quizz import txt_to_quizz
from generate_pdf import generate_pdf_quiz
import json
import asyncio

st.title("PDF to Quiz")

def build_question(count, json_question):
    if json_question.get("question") is not None:
        st.write("Question:", json_question.get("question", ""))
        choices = ['A', 'B', 'C', 'D']
        selected_answer = st.selectbox("Select your answer:", choices, key=f"select_{count}")
        for choice in choices:
            choice_str = json_question.get(choice, "None")
            st.write(f"{choice} {choice_str}")
                    
        color = ""
        if st.button("Submit", key=f"button_{count}"):
            rep = json_question.get("reponse")
            if selected_answer == rep:
                color = ":green"
                st.write(f":green[Correct answer: {rep}]")
            else:
                color = ":red"
                st.write(f":red[Wrong answer. The correct answer is {rep}.]")

        st.write(f"{color}[Your answer: {selected_answer}]")
        count += 1

    return count

# Upload PDF file
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
txt = st.text_area("Enter the text you want to generate the quiz from")

if st.button("Generate Quiz", key="button_generate"):
    if txt:
        with st.spinner("Generating quiz..."):
            st.session_state['questions'] = asyncio.run(txt_to_quizz(txt))
            st.write("Quiz generated successfully!")

if uploaded_file is not None:
    old_file_name = st.session_state.get('uploaded_file_name', None)
    if old_file_name != uploaded_file.name:
        with st.spinner("Generating quiz..."):
            with open(f"data/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.getvalue())

            st.session_state['uploaded_file_name'] = uploaded_file.name
            st.session_state['questions'] = asyncio.run(pdf_to_quizz(f"data/{uploaded_file.name}"))
            st.write("Quiz generated successfully!")

if 'questions' in st.session_state:
    count = 0
    for json_question in st.session_state['questions']:
        count = build_question(count, json_question)

    # Moved outside the loop to avoid DuplicateWidgetID error
    if st.button("Generate PDF Quiz", key="button_generate_pdf_quiz"):
        with st.spinner("Generating PDF quiz..."):
            json_questions = st.session_state['questions']
            file_name = uploaded_file.name

            # Remove .pdf extension
            if file_name.endswith(".pdf"):
                file_name = file_name[:-4]

            json_path = f"data/quiz-{file_name}.json"
            with open(json_path, "w", encoding='latin-1', errors='ignore') as f:
                f.write(json.dumps(json_questions))

            generate_pdf_quiz(json_path, json_questions)
            st.write("PDF Quiz generated successfully!")

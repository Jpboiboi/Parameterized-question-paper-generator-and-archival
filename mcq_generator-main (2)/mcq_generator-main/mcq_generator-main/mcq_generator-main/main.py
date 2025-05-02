import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import json
from question_generator import QuestionGenerator
from question_translator import QuestionTranslator
from question_prerequsite import QuestionPrerequisite
from similar_question_generator import SimilarQuestionGenerator
from llm_model import OpenAIModel
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, filename='mcqapp.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

def save_to_json_in_english(filename, questions):
    with open(filename, 'w') as f:
        json.dump(questions, f)

def main():
    st.sidebar.title("MCQ Generator")

    # Select model type
    model_name = st.sidebar.selectbox("Select Model", ["gpt-4o-mini", "gpt-4o", "gpt-4"])
    model = OpenAIModel(model_name)

    # Language selection and input fields
    language = st.sidebar.selectbox("Select Language", ["English", "Hindi"])
    specialization = st.sidebar.text_input("Enter the specialization:")
    difficulty = st.sidebar.selectbox("Select difficulty level:", ["Easy", "Medium", "Hard"])
    num_questions = st.sidebar.number_input("Number of questions:", min_value=1, max_value=100, value=5)
    max_tokens_question = st.sidebar.number_input("Max Tokens for Question Generation", min_value=100, max_value=4000, value=3000)
    max_tokens_explanation = st.sidebar.number_input("Max Tokens for Explanation", min_value=100, max_value=4000, value=1500)

    if "original_questions" not in st.session_state:
        st.session_state.original_questions = {}
    if "last_index" not in st.session_state:
        st.session_state.last_index = {}

    if st.sidebar.button("Generate Questions"):
        if not specialization or not difficulty or not language:
            st.sidebar.error("Please fill out all fields.")
        else:
            # Update the last index for the specialization
            if specialization not in st.session_state.last_index:
                st.session_state.last_index[specialization] = 0
            else:
                st.session_state.last_index[specialization] += 1

            # Initialize dictionary for original questions
            if specialization not in st.session_state.original_questions:
                st.session_state.original_questions[specialization] = {}

            with st.spinner("Generating questions..."):
                try:
                    question_generator = QuestionGenerator(model)
                    questions = question_generator.generate_questions(
                        specialization, difficulty, num_questions, max_tokens_question)

                    if not questions:
                        st.error("No questions were generated. Please check your API key or try changing the inputs.")
                    else:
                        # Display each question in a clean format
                        for index, raw_q in enumerate(questions, start=1):
                            question_text = raw_q.get("question", "No question found")
                            answer_text = raw_q.get("answer", "No answer found")
                            st.markdown(f"### Question {index}")
                            st.write(f"**Q:** {question_text}")
                            st.write(f"**Answer:** {answer_text}")

                except Exception as e:
                    st.error(f"An error occurred while generating questions: {e}")

if __name__ == "__main__":
    main()
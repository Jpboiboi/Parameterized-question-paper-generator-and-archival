import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain.globals import set_verbose
from langchain_community.callbacks import get_openai_callback
from src.mcq_generator.utils import read_file, get_table_data
from src.mcq_generator.logger import logging
from src.mcq_generator.MCQGenerator import generate_and_evaluate_quiz

import re  # <-- for the regex option

set_verbose(True)

with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQ Generator")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a pdf or text file")
    mcq_count     = st.number_input("No of Questions", min_value=3, max_value=50)
    subject       = st.text_input("Insert the Subject", max_chars=20)
    tone          = st.text_input("Complexity level of Questions", max_chars=20, placeholder="Simple")
    button        = st.form_submit_button("Create MCQs")

    if button and uploaded_file and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                text = read_file(uploaded_file)
                with get_openai_callback() as cb:
                    response = generate_and_evaluate_quiz({
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error(f"Error: {e}")
            else:
                # Log token usage
                print(f"Total Tokens:      {cb.total_tokens}")
                print(f"Prompt Tokens:     {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost:        {cb.total_cost}")

                if not isinstance(response, dict):
                    st.write(response)
                else:
                    quiz = response.get("quiz")
                    if not quiz:
                        st.error("Error: No quiz data returned.")
                    else:
                        table_data = get_table_data(quiz)
                        print(f"Table Data: {table_data}")
                        print(f"Type of Table Data: {type(table_data)}")

                        if not isinstance(table_data, list):
                            st.error("Error: table_data is not an iterable.")
                        else:
                            for i, row in enumerate(table_data):
                                st.markdown(f"**Q{i+1}. {row['Question']}**")
                                raw_options = row.get('Options', '')
                                print(f"Raw Options: {raw_options}")

                                # Split on '||'
                                option_parts = [opt.strip() for opt in raw_options.split('||')]
                                options_dict = {}

                                # --- Option A: arrow‐based split ----
                                for part in option_parts:
                                    if '->' in part:
                                        key, val = part.split('->', 1)
                                    elif '→' in part:
                                        key, val = part.split('→', 1)
                                    else:
                                        continue
                                    options_dict[key.strip().upper()] = val.strip()

                                # --- Option B: regex‐based split (uncomment to use) ---
                                # options_dict = {}
                                # for part in option_parts:
                                #     m = re.match(r'^([A-Da-d])\s*(?:->|→|:|\))\s*(.+)$', part)
                                #     if m:
                                #         options_dict[m.group(1).upper()] = m.group(2).strip()

                                print(f"Options Dict: {options_dict}")

                                if options_dict:
                                    st.radio(
                                        label="Options:",
                                        options=list(options_dict.keys()),
                                        format_func=lambda x: f"{x}. {options_dict[x]}",
                                        key=f"q{i}"
                                    )
                                else:
                                    st.error(f"No valid options for question {i+1}.")
                                st.markdown("---")

                            st.text_area(label="Review", value=response.get("review", ""))

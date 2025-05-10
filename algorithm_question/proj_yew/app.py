import os
from dotenv import load_dotenv
import logging
import random
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import mysql.connector

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Utility: merge question halves randomly
def merge_question_halves(db1, db2, n):
    merged = []
    for _ in range(n):
        first = random.choice(db1).rstrip("?. ")
        second = random.choice(db2).strip()
        merged.append(f"{first} {second}")
    return merged

# Utility: repair/rephrase any raw question using OpenAI LLM
# Updated prompt to enforce high-quality, varied, self-contained questions
def repair_question(raw_question, client):
    system_prompt = (
        "You are an expert question-generation assistant. "
        "You will be given a programming question fragment. "
        "Your task is to rephrase or correct it so that it becomes a clear, self-contained, grammatically correct programming question. "
        "Use varied templates and ensure the question is precise and natural. "
        "Return only the final corrected question."
    )
    user_prompt = (
        f"Here is the raw question fragment to improve:\n"  
        f"\"{raw_question}\""
    )
    # Send system + user messages for better control
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate merged questions and run each one through the LLM for correction."""
    try:
        # 1) Determine how many questions to build
        num_questions = int(request.form.get('num_questions', 5))
        num_questions = max(1, min(num_questions, 20))

        # 2) Fetch the two halves from MySQL
        db = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "questions")
        )
        cursor = db.cursor()
        cursor.execute("SELECT text FROM question_starts")
        starts = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT text FROM question_ends")
        ends = [row[0] for row in cursor.fetchall()]
        cursor.close()
        db.close()

        # 3) Randomly merge them into raw questions
        raw_questions = merge_question_halves(starts, ends, num_questions)

        # 4) Initialize the OpenAI client
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # 5) Repair *every* question, regardless of correctness
        corrected_questions = []
        for raw_q in raw_questions:
            corrected = repair_question(raw_q, client)
            corrected_questions.append(corrected)

        # 6) Return the polished list of questions
        return jsonify({
            'success': True,
            'questions': corrected_questions
        })

    except Exception as e:
        logging.error(f"Error generating questions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

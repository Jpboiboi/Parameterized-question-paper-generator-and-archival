import os
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Add this line to load environment variables from .env
import logging
from flask import Flask, render_template, request, jsonify
from question_generator import generate_questions
from openai import OpenAI  # Updated import
import mysql.connector

# Configure logging
logging.basicConfig(level=logging.DEBUG)
# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')
def parse_llm_reply(llm_reply):
    import re
    # Look for a score at the start of the reply, e.g. "95% - Suggestion"
    percent_match = re.search(r'(\d{1,3})\s*%', llm_reply)
    percent = percent_match.group(1) if percent_match else None
    # Remove the percentage part from the feedback
    feedback = llm_reply
    if percent:
        feedback = llm_reply[llm_reply.find(percent) + len(percent):].lstrip(' %:-')
    return percent, feedback

@app.route('/generate', methods=['POST'])
def generate():
    """Generate random programming questions and verify them using the LLM."""
    try:
        num_questions = int(request.form.get('num_questions', 5))
        if num_questions < 1:
            num_questions = 1
        elif num_questions > 20:
            num_questions = 20

        questions = generate_questions(num_questions)

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        verified_questions = []

        for q in questions:
            prompt = (
                f"Evaluate the following programming question for correctness and clarity. "
                f"Reply in the format: '<score>% - <suggestion or Correct if perfect>'. "
                f"Score should be from 0 to 100. If not perfect, suggest improvements.\n\n{q}"
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            llm_reply = response.choices[0].message.content.strip()
            percent, feedback = parse_llm_reply(llm_reply)
            verified_questions.append({
                'question': q,
                'llm_percent': percent or '0',
                'llm_feedback': feedback or llm_reply
            })

        return jsonify({
            'success': True,
            'questions': verified_questions
        })
    except Exception as e:
        logging.error(f"Error generating questions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@app.route('/llm', methods=['POST'])
def llm():
    """Endpoint to interact with an LLM model."""
    try:
        prompt = request.json.get('prompt', '')
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required.'}), 400

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Updated client initialization
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        llm_reply = response.choices[0].message.content

        return jsonify({'success': True, 'response': llm_reply})
    except Exception as e:
        logging.error(f"Error with LLM: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/verify_questions', methods=['GET'])
def verify_questions():
    """Fetch all questions from the database and verify them using the LLM."""
    try:
        db = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database="questions"
        )
        cursor = db.cursor()
        cursor.execute("SELECT text FROM question_starts")
        starts = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT text FROM question_ends")
        ends = [row[0] for row in cursor.fetchall()]
        questions = [f"{start} {end}" for start in starts for end in ends]

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        verified_questions = []

        for q in questions:
            prompt = (
                f"Evaluate the following programming question for correctness and clarity. "
                f"Reply in the format: '<score>% - <suggestion or Correct if perfect>'. "
                f"Score should be from 0 to 100. If not perfect, suggest improvements.\n\n{q}"
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            llm_reply = response.choices[0].message.content.strip()
            percent, feedback = parse_llm_reply(llm_reply)
            verified_questions.append({
                'question': q,
                'llm_percent': percent or '0',
                'llm_feedback': feedback or llm_reply
            })

        return jsonify({
            'success': True,
            'questions': verified_questions
        })
    except Exception as e:
        logging.error(f"Error verifying questions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
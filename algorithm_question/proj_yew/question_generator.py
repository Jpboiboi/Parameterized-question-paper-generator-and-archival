import mysql.connector
import random

def get_db_connection():
    """Establish a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",      # Database host (e.g., "localhost")
        user="root",  # Your MySQL username
        password="",  # Your MySQL password
        database="questions"  # The name of your database
    )

def fetch_question_fragments():
    """Fetch question fragments from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch the first set of question fragments (question_starts)
    cursor.execute("SELECT text FROM question_starts")
    question_starts = [row[0] for row in cursor.fetchall()]

    # Fetch the second set of question fragments (question_ends)
    cursor.execute("SELECT text FROM question_ends")
    question_ends = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    connection.close()

    return question_starts, question_ends

def generate_questions(n=5):
    """
    Generate n random programming/algorithm questions by combining elements from the database.
    
    Args:
        n (int): Number of questions to generate.
        
    Returns:
        list: A list of generated questions.
    """
    # Fetch the question fragments from the database
    question_starts, question_ends = fetch_question_fragments()
    
    merged = []
    for _ in range(n):
        first_half = random.choice(question_starts).rstrip("? .")
        second_half = random.choice(question_ends).strip()
        # Combine into a clean sentence
        question = f"{first_half} {second_half}?"
        merged.append(question)
    
    return merged

import re
from prompt_builder import PromptBuilder
from llm_model import LLMModel
import logging

# Configure logging to write to a file
logging.basicConfig(filename='question_generator.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class QuestionGenerator:
    def __init__(self, model: LLMModel):
        self.model = model
        self.prompt_builder = PromptBuilder()

    def parse_phrase_questions(self, response_text: str) -> list:
        """
        Parses simple Q&A phrase pairs from a model response.
        Format:
        Q: <question>
        Answer: <answer>
        """
        pattern = r"Q:\s*(.*?)\s*Answer:\s*(.*?)(?=Q:|$)"
        matches = re.findall(pattern, response_text, re.DOTALL)

        questions = []
        for question, answer in matches:
            questions.append({
                "question": question.strip(),
                "answer": answer.strip()
            })

        return questions

    def generate_questions(self, specialization: str, difficulty: str, num_questions: int, max_tokens: int) -> list:
        """
        Generates simple phrase-based questions and answers using the model and returns them as a list.
        """
        # Build the prompt for generating phrase-based questions
        prompt = self.prompt_builder.get_phrase_question_generation_prompt(specialization, difficulty, num_questions)
        logging.info("Generating questions with prompt:\n%s", prompt)

        try:
            # Send the request to the model and get the response
            response_chunks = self.model.get_response(
                [{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )

            logging.info("Model response: %s", response_chunks)  # Log the raw response for debugging

            # Check if the response is valid
            if not response_chunks or not isinstance(response_chunks, list):
                logging.warning("Received invalid or empty response.")
                return []

            all_questions = []
            for chunk in response_chunks:
                parsed = self.parse_phrase_questions(chunk)
                if parsed:
                    logging.info("Parsed %d question(s) from one chunk.", len(parsed))
                    all_questions.extend(parsed)
                else:
                    logging.warning("Failed to parse any question from chunk:\n%s", chunk)

            return all_questions

        except Exception as e:
            logging.error("Exception during question generation: %s", e)
            return []


# Example usage for testing
if __name__ == "__main__":
    from llm_model import OpenAIModel
    model = OpenAIModel("gpt-4")  # Use your OpenAIModel class with the correct model
    generator = QuestionGenerator(model)
    
    # Example usage to generate 3 history questions at easy difficulty
    result = generator.generate_questions("History", "Easy", 3, 1000)
    for idx, qa in enumerate(result, 1):
        print(f"Question {idx}")
        print(f"Q: {qa['question']}\n")
        print(f"Answer: {qa['answer']}\n")

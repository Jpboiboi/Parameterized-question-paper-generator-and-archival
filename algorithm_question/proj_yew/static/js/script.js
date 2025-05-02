// script.js - JavaScript code
document.addEventListener('DOMContentLoaded', function() {
    const generatorForm = document.getElementById('generator-form');
    const generateBtn = document.getElementById('generate-btn');
    const newBatchBtn = document.getElementById('new-batch-btn');
    const copyAllBtn = document.getElementById('copy-all-btn');
    const numQuestionsInput = document.getElementById('num-questions');
    const questionsList = document.getElementById('questions-list');
    const resultsContainer = document.getElementById('results-container');
    const loadingElement = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    // Generate questions when the form is submitted
    generatorForm.addEventListener('submit', function(e) {
        e.preventDefault();
        generateQuestions();
    });
    // Generate new batch when the button is clicked
    newBatchBtn.addEventListener('click', function() {
        generateQuestions();
    });
    // Copy all questions when the button is clicked
    copyAllBtn.addEventListener('click', function() {
        const questions = Array.from(questionsList.querySelectorAll('.list-group-item'))
            .map(item => item.querySelector('.question-text').textContent)
            .join('\n\n');
        
        navigator.clipboard.writeText(questions)
            .then(() => {
                // Show temporary success message
                const originalText = copyAllBtn.innerHTML;
                copyAllBtn.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
                setTimeout(() => {
                    copyAllBtn.innerHTML = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Error copying text: ', err);
            });
    });
    // Function to generate questions
    function generateQuestions() {
        // Show loading indicator
        loadingElement.classList.remove('d-none');
        resultsContainer.classList.add('d-none');
        errorMessage.classList.add('d-none');
        generateBtn.disabled = true;
        
        // Get the form data
        const formData = new FormData(generatorForm);
        
        // Send request to the server
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingElement.classList.add('d-none');
            generateBtn.disabled = false;
            
            if (data.success) {
                // Display the results
                displayQuestions(data.questions);
                newBatchBtn.classList.remove('d-none');
            } else {
                // Show error message
                errorText.textContent = data.error || 'An error occurred while generating questions.';
                errorMessage.classList.remove('d-none');
            }
        })
        .catch(error => {
            // Hide loading indicator and show error
            loadingElement.classList.add('d-none');
            generateBtn.disabled = false;
            errorText.textContent = 'Network error: Could not connect to the server.';
            errorMessage.classList.remove('d-none');
            console.error('Error:', error);
        });
    }
    // Function to display questions in the UI
    function displayQuestions(questions) {
        // Clear previous questions
        questionsList.innerHTML = '';
        
        // Add each question to the list
        questions.forEach((item, index) => {
            const listItem = document.createElement('div');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-start';
            
            const content = document.createElement('div');
            content.className = 'ms-2 me-auto';
            
            const questionNumber = document.createElement('div');
            questionNumber.className = 'fw-bold';
            questionNumber.textContent = `Question ${index + 1}`;
            
            const questionText = document.createElement('div');
            questionText.className = 'question-text';
            questionText.textContent = item.question; // Access the 'question' property
            
            // Add LLM feedback and percent
            const llmInfo = document.createElement('div');
            llmInfo.className = 'text-secondary mt-1';
            llmInfo.innerHTML = `<strong>LLM Score:</strong> ${item.llm_percent || 'N/A'}%<br><em>${item.llm_feedback}</em>`;
            
            content.appendChild(questionNumber);
            content.appendChild(questionText);
            content.appendChild(llmInfo);
            
            const copyButton = document.createElement('button');
            copyButton.className = 'btn btn-sm btn-outline-secondary ms-2';
            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            copyButton.title = 'Copy question';
            copyButton.addEventListener('click', function() {
                navigator.clipboard.writeText(item.question)
                    .then(() => {
                        const originalHTML = copyButton.innerHTML;
                        copyButton.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => {
                            copyButton.innerHTML = originalHTML;
                        }, 1000);
                    })
                    .catch(err => {
                        console.error('Error copying text: ', err);
                    });
            });
            
            listItem.appendChild(content);
            listItem.appendChild(copyButton);
            questionsList.appendChild(listItem);
        });
        
        // Show the results container
        resultsContainer.classList.remove('d-none');
    }
    // Validate the input for number of questions
    numQuestionsInput.addEventListener('change', function() {
        let value = parseInt(this.value);
        if (isNaN(value) || value < 1) {
            this.value = 1;
        } else if (value > 20) {
            this.value = 20;
        }
    });
});

function renderQuestions(questions) {
    const questionsList = document.getElementById('questions-list');
    questionsList.innerHTML = '';
    questions.forEach((item, idx) => {
        const questionItem = document.createElement('div');
        questionItem.className = 'list-group-item d-flex justify-content-between align-items-center flex-wrap';
        questionItem.innerHTML = `
            <div>
                <strong>Question ${idx + 1}:</strong> ${item.question}
                <br>
                <span class="text-secondary">
                    <strong>LLM Score:</strong> ${item.llm_percent || 'N/A'}%
                    <br>
                    <em>${item.llm_feedback}</em>
                </span>
            </div>
            <button class="btn btn-outline-secondary btn-sm ms-2" onclick="copyToClipboard('${item.question.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i>
            </button>
        `;
        questionsList.appendChild(questionItem);
    });
}

// Example usage after fetching questions from backend:
fetch('/verify_questions')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderQuestions(data.questions);
            document.getElementById('results-container').classList.remove('d-none');
        }
    });
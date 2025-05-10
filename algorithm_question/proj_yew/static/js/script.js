// script.js - JavaScript code
document.addEventListener('DOMContentLoaded', function() {
    const generatorForm   = document.getElementById('generator-form');
    const generateBtn     = document.getElementById('generate-btn');
    const newBatchBtn     = document.getElementById('new-batch-btn');
    const copyAllBtn      = document.getElementById('copy-all-btn');
    const numQuestionsInput = document.getElementById('num-questions');
    const questionsList   = document.getElementById('questions-list');
    const resultsContainer= document.getElementById('results-container');
    const loadingElement  = document.getElementById('loading');
    const errorMessage    = document.getElementById('error-message');
    const errorText       = document.getElementById('error-text');

    // Form submit or New Batch button both call generateQuestions()
    generatorForm.addEventListener('submit', e => { e.preventDefault(); generateQuestions(); });
    newBatchBtn.addEventListener('click', generateQuestions);

    // Copy all corrected questions
    copyAllBtn.addEventListener('click', () => {
        const allText = Array.from(questionsList.querySelectorAll('.question-text'))
            .map(el => el.textContent)
            .join('\n\n');
        navigator.clipboard.writeText(allText)
          .then(() => {
            const orig = copyAllBtn.innerHTML;
            copyAllBtn.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
            setTimeout(() => copyAllBtn.innerHTML = orig, 2000);
          })
          .catch(console.error);
    });

    function generateQuestions() {
        loadingElement.classList.remove('d-none');
        resultsContainer.classList.add('d-none');
        errorMessage.classList.add('d-none');
        generateBtn.disabled = true;

        const formData = new FormData(generatorForm);

        fetch('/generate', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            loadingElement.classList.add('d-none');
            generateBtn.disabled = false;

            if (data.success) {
                displayQuestions(data.questions);
                newBatchBtn.classList.remove('d-none');
            } else {
                errorText.textContent = data.error || 'An error occurred.';
                errorMessage.classList.remove('d-none');
            }
        })
        .catch(err => {
            loadingElement.classList.add('d-none');
            generateBtn.disabled = false;
            errorText.textContent = 'Network error: Could not connect.';
            errorMessage.classList.remove('d-none');
            console.error(err);
        });
    }

    // UPDATED to expect an array of strings instead of objects
    function displayQuestions(questions) {
        // Clear previous questions
        questionsList.innerHTML = '';

        questions.forEach((qText, index) => {
            const listItem = document.createElement('div');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-start';

            // Left side: question number + text
            const content = document.createElement('div');
            content.className = 'ms-2 me-auto';

            const questionNumber = document.createElement('div');
            questionNumber.className = 'fw-bold';
            questionNumber.textContent = `Question ${index + 1}`;

            const questionText = document.createElement('div');
            questionText.className = 'question-text';
            questionText.textContent = qText;

            content.appendChild(questionNumber);
            content.appendChild(questionText);

            // Right side: copy button
            const copyButton = document.createElement('button');
            copyButton.className = 'btn btn-sm btn-outline-secondary ms-2';
            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            copyButton.title = 'Copy question';
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(qText)
                  .then(() => {
                    const orig = copyButton.innerHTML;
                    copyButton.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => copyButton.innerHTML = orig, 1000);
                  })
                  .catch(console.error);
            });

            listItem.appendChild(content);
            listItem.appendChild(copyButton);
            questionsList.appendChild(listItem);
        });

        resultsContainer.classList.remove('d-none');
    }

    // Input validation for number of questions
    numQuestionsInput.addEventListener('change', function() {
        let v = parseInt(this.value);
        if (isNaN(v) || v < 1) this.value = 1;
        else if (v > 20) this.value = 20;
    });
});

// Therapist_Chatbot/frontend/static/js/script.js
let isLoading = false;

async function sendMessage() {
    if (isLoading) return;
    
    const userInput = document.getElementById('user-input').value;
    if (!userInput.trim()) return;

    // Get selected model
    const model = document.querySelector('input[name="model"]:checked').value;

    // Display user message
    appendMessage('You', userInput, 'user-message');

    // Clear input field
    document.getElementById('user-input').value = '';

    try {
        isLoading = true;
        toggleLoadingIndicator(true);

        console.log('Sending request:', {
            message: userInput,
            model: model
        });

        const response = await fetch('/chat', {  // Relative URL since served by FastAPI
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: userInput,
                model: model
            })
        });

        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);

        if (response.ok) {
            appendMessage('Therapist', data.response, 'bot-message');
        } else {
            appendMessage('Error', data.detail || 'Failed to get response', 'error-message');
        }
    } catch (error) {
        console.error('Error:', error);
        appendMessage('Error', 'Failed to connect to server. Please try again.', 'error-message');
    } finally {
        isLoading = false;
        toggleLoadingIndicator(false);
    }
}

function appendMessage(sender, message, className) {
    const chatContainer = document.getElementById('chat-container');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;
    
    const timestamp = new Date().toLocaleTimeString();
    messageElement.innerHTML = `
        <div class="message-header">
            <strong>${sender}</strong>
            <span class="timestamp">${timestamp}</span>
        </div>
        <div class="message-content">${message}</div>
    `;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function toggleLoadingIndicator(show) {
    const button = document.querySelector('button');
    if (show) {
        button.disabled = true;
        button.innerHTML = 'Sending...';
    } else {
        button.disabled = false;
        button.innerHTML = 'Send';
    }
}

// Debounced input handler
let typingTimer;
const doneTypingInterval = 1000;

document.getElementById('user-input').addEventListener('keyup', function() {
    clearTimeout(typingTimer);
    if (this.value) {
        typingTimer = setTimeout(() => {
            // Enable send button when typing is done
            document.querySelector('button').disabled = false;
        }, doneTypingInterval);
    }
});

// Enter key to send message
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Model selection handler
document.querySelectorAll('input[name="model"]').forEach(radio => {
    radio.addEventListener('change', function() {
        // Clear chat when model changes
        if (confirm('Changing models will clear the current chat. Continue?')) {
            document.getElementById('chat-container').innerHTML = '';
        } else {
            // Revert selection
            this.checked = false;
            // Re-check the other option
            const otherModel = this.value === 'azure' ? 'gemini' : 'azure';
            document.querySelector(`input[value="${otherModel}"]`).checked = true;
        }
    });
});
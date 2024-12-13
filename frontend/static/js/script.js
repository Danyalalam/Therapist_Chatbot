// DOM Elements
const textModeBtn = document.getElementById('text-mode-btn');
const speechModeBtn = document.getElementById('speech-mode-btn');
const textInputContainer = document.getElementById('text-input-container');
const speechInputContainer = document.getElementById('speech-input-container');
const startRecordBtn = document.getElementById('start-record-btn');
const stopSpeechBtn = document.getElementById('stop-speech-btn');
const userInput = document.getElementById('user-input');
const cancelVoiceBtn = document.getElementById('cancel-voice-btn');
const voiceOverlay = document.getElementById('voice-overlay');
const overlayStatus = document.getElementById('overlay-status');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.querySelector('aside');
const typingIndicator = document.getElementById('typing-indicator');
const toggleMusicPlayerBtn = document.getElementById('toggle-music-player');
const musicPlayer = document.getElementById('music-player');
const moodSelect = document.getElementById('mood-select');
const playMusicBtn = document.getElementById('play-music-btn');
const stopMusicBtn = document.getElementById('stop-music-btn');
const toggleSpeechModeBtn = document.getElementById('toggle-speech-mode');

// Initialize Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'en-US';
recognition.interimResults = false;

// Initialize Speech Synthesis
let utterance;

// Initialize Music
let music = new Audio();
music.loop = true;

// Modes
let currentMode = 'text'; // default mode

// Toggle Sidebar on Mobile
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');
});

// Toggle Music Player Visibility
toggleMusicPlayerBtn.addEventListener('click', () => {
    musicPlayer.classList.toggle('hidden');
});

// Mode Selection Handlers
textModeBtn.addEventListener('click', () => {
    currentMode = 'text';
    textModeBtn.classList.add('bg-blue-700');
    speechModeBtn.classList.remove('bg-green-700');
    textInputContainer.classList.remove('hidden');
    speechInputContainer.classList.add('hidden');
});

speechModeBtn.addEventListener('click', () => {
    currentMode = 'speech';
    speechModeBtn.classList.add('bg-green-700');
    textModeBtn.classList.remove('bg-blue-700');
    speechInputContainer.classList.remove('hidden');
    textInputContainer.classList.add('hidden');
});

// Toggle Speech Mode (Alternative Toggle)
toggleSpeechModeBtn.addEventListener('click', () => {
    if (currentMode !== 'speech') {
        currentMode = 'speech';
        speechModeBtn.click();
    } else {
        currentMode = 'text';
        textModeBtn.click();
    }
});

// Start Recognition
startRecordBtn.addEventListener('click', () => {
    showVoiceOverlay('Listening...');
    recognition.start();
});

// Stop Recognition
stopSpeechBtn.addEventListener('click', () => {
    recognition.stop();
    hideVoiceOverlay();
});

// Cancel Voice Input
cancelVoiceBtn.addEventListener('click', () => {
    recognition.stop();
    hideVoiceOverlay();
});

// Handle Recognition Result
recognition.addEventListener('result', (event) => {
    const transcript = event.results[0][0].transcript;
    sendMessage(transcript);
});

// Handle Recognition Errors
recognition.addEventListener('error', (event) => {
    console.error('Speech recognition error:', event.error);
    hideVoiceOverlay();
    alert('Speech recognition error: ' + event.error);
});

// Text-to-Speech Function
function speakMessage(message) {
    const synthesis = window.speechSynthesis;
    synthesis.cancel(); // Cancel any ongoing speech
    utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = 'en-US';
    synthesis.speak(utterance);
    showStopSpeechButton();

    // Hide Stop Button when Speech Ends
    utterance.onend = () => {
        hideStopSpeechButton();
    };
}

// Speak User Message in Speech Mode
function speakUserMessage(message) {
    const synthesis = window.speechSynthesis;
    const userUtterance = new SpeechSynthesisUtterance(`You said: ${message}`);
    userUtterance.lang = 'en-US';
    synthesis.speak(userUtterance);
}

// Stop Speech Function
function stopSpeech() {
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        hideStopSpeechButton();
    }
}

// Show Stop Speech Button
function showStopSpeechButton() {
    stopSpeechBtn.classList.remove('hidden');
}

// Hide Stop Speech Button
function hideStopSpeechButton() {
    stopSpeechBtn.classList.add('hidden');
}

// Show Typing Indicator
function showTypingIndicator() {
    typingIndicator.classList.remove('hidden');
    typingIndicator.style.display = 'flex';
}

// Hide Typing Indicator
function hideTypingIndicator() {
    typingIndicator.classList.add('hidden');
    typingIndicator.style.display = 'none';
}

// Voice Overlay Functions
function showVoiceOverlay(status) {
    overlayStatus.textContent = status;
    voiceOverlay.classList.remove('hidden');
}

function hideVoiceOverlay() {
    voiceOverlay.classList.add('hidden');
}

// Send Message Function
let isLoading = false;

async function sendMessage(inputText = null) {
    if (isLoading) return;

    let message = inputText || userInput.value;
    if (!message.trim()) return;

    // Determine mode
    const isSpeechMode = currentMode === 'speech';

    if (isSpeechMode) {
        appendMessage('You', message, 'user-message');
    } else {
        appendMessage('You', message, 'user-message');
        userInput.value = '';
    }

    try {
        isLoading = true;
        toggleLoadingIndicator(true);
        showTypingIndicator(); // Show typing indicator when sending a message
        if (!isSpeechMode) {
            showVoiceOverlay('Thinking...');
        }

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                model: document.querySelector('input[name="model"]:checked').value
            })
        });

        const data = await response.json();

        if (response.ok) {
            appendMessage('Therapist', data.response, 'bot-message');
            speakMessage(data.response); // Speak bot response
        } else {
            appendMessage('Error', data.detail || 'Failed to get response', 'error-message');
        }
    } catch (error) {
        appendMessage('Error', 'Failed to connect to server. Please try again.', 'error-message');
    } finally {
        isLoading = false;
        toggleLoadingIndicator(false);
        hideTypingIndicator(); // Hide typing indicator after response
        if (!isSpeechMode) {
            hideVoiceOverlay(); // Hide overlay after response
        }
    }
}

// Append Message to Chat
function appendMessage(sender, message, className) {
    const chatContainer = document.getElementById('chat-container');

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', className, 'shadow-lg', 'max-w-md', 'break-words');

    const messageHeader = document.createElement('div');
    messageHeader.classList.add('message-header', 'flex', 'justify-between', 'mb-1', 'text-sm', 'opacity-80');

    const senderSpan = document.createElement('span');
    senderSpan.textContent = sender;

    const timestampSpan = document.createElement('span');
    timestampSpan.classList.add('timestamp');
    timestampSpan.textContent = new Date().toLocaleTimeString();

    messageHeader.appendChild(senderSpan);
    messageHeader.appendChild(timestampSpan);

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content', 'text-base');
    messageContent.textContent = message;

    messageDiv.appendChild(messageHeader);
    messageDiv.appendChild(messageContent);

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Loading Indicator (Optional Enhancement)
function toggleLoadingIndicator(show) {
    const sendButton = document.querySelector('button[onclick="sendMessage()"]');
    const startRecordButton = document.getElementById('start-record-btn');
    if (show) {
        sendButton.disabled = true;
        sendButton.classList.add('opacity-50', 'cursor-not-allowed');
        startRecordButton.disabled = true;
        startRecordButton.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        sendButton.disabled = false;
        sendButton.classList.remove('opacity-50', 'cursor-not-allowed');
        startRecordButton.disabled = false;
        startRecordButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// Music Player Functionality
playMusicBtn.addEventListener('click', () => {
    const selectedMood = moodSelect.value;
    switch (selectedMood) {
        case 'happy':
            music.src = '/static/music/happy.mp3'; // Ensure the path is correct
            break;
        case 'sad':
            music.src = '/static/music/sad.mp3';
            break;
        case 'relaxed':
            music.src = '/static/music/relaxed.mp3';
            break;
        default:
            music.src = '/static/music/default.mp3';
    }
    music.play();
});

stopMusicBtn.addEventListener('click', () => {
    music.pause();
    music.currentTime = 0;
});
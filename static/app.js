document.addEventListener("DOMContentLoaded", () => {
    // Initialize Particles JS for background
    if (window.particlesJS) {
        try {
            particlesJS("particles-js", {
                "particles": {
                    "number": { "value": 40, "density": { "enable": true, "value_area": 800 } },
                    "color": { "value": ["#9b51e0", "#1f8bfa", "#ffffff"] },
                    "shape": { "type": "circle" },
                    "opacity": { "value": 0.5, "random": true },
                    "size": { "value": 3, "random": true },
                    "line_linked": { "enable": false },
                    "move": { "enable": true, "speed": 1, "direction": "none", "random": true, "out_mode": "out" }
                },
                "interactivity": { "events": { "onhover": { "enable": false }, "onclick": { "enable": false } } },
                "retina_detect": true
            });
        } catch (e) {
            console.error("Particles JS initialization failed", e);
        }
    }

    const orb = document.getElementById("orb");
    const statusText = document.getElementById("status-text");
    const chatBox = document.getElementById("chat-box");
    const commandInput = document.getElementById("command-input");
    const sendBtn = document.getElementById("send-btn");
    const micBtn = document.getElementById("mic-btn");
    const statusIndicator = document.querySelector(".status-indicator");

    // UI State management
    function setOrbState(state, text) {
        orb.className = `orb ${state}`;
        statusText.innerText = text;
        
        if (state === 'idle') {
            micBtn.classList.remove('active');
            statusIndicator.style.backgroundColor = '#4cd137'; // Green
            statusIndicator.style.boxShadow = '0 0 10px #4cd137';
        } else if (state === 'listening') {
            micBtn.classList.add('active');
            statusIndicator.style.backgroundColor = '#ff416c'; // Red
            statusIndicator.style.boxShadow = '0 0 10px #ff416c';
        } else if (state === 'speaking') {
            statusIndicator.style.backgroundColor = '#00b4db'; // Blue
            statusIndicator.style.boxShadow = '0 0 10px #00b4db';
        }
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        contentDiv.innerText = text;
        
        msgDiv.appendChild(contentDiv);
        chatBox.appendChild(msgDiv);
        
        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Initialize Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-in';
    }


    // API Calls to Flask Backend
    async function sendCommand(commandText) {
        if (!commandText.trim()) return;
        
        addMessage(commandText, "user");
        commandInput.value = "";
        
        setOrbState("speaking", "Sofia is thinking...");

        try {
            const response = await fetch("/api/command", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ command: commandText })
            });
            
            const data = await response.json();
            
            if (data.response) {
                setOrbState("speaking", "Sofia is speaking...");
                addMessage(data.response, "system");
                const delay = data.response.length * 50 + 1000;
                // Wait a bit to simulate speaking time before going idle or listening again
                setTimeout(() => {
                    setOrbState("idle", "Sofia is ready");
                    if (window.continuousMode) {
                        triggerVoiceCommand();
                    }
                }, delay);
            } else {
                setOrbState("idle", "Sofia is ready");
                if (window.continuousMode) triggerVoiceCommand();
            }

        } catch (error) {
            addMessage("Sorry, I am having trouble connecting to my server.", "system");
            setOrbState("idle", "Connection Error");
            window.continuousMode = false;
        }
    }

    function triggerVoiceCommand() {
        if (!recognition) {
            addMessage("Your browser does not support voice recognition. Please use Google Chrome or Edge.", "system");
            return;
        }

        if (orb.classList.contains("listening")) {
            recognition.stop();
            window.continuousMode = false; // User manually stopped it
            return;
        }
        
        window.continuousMode = true; // Enable continuous listening loop
        setOrbState("listening", "Listening...");
        commandInput.value = "";
        commandInput.placeholder = "Listening...";
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            commandInput.value = finalTranscript || interimTranscript;
        };

        recognition.onend = () => {
            if (commandInput.value.trim() !== "") {
                const finalCommand = commandInput.value;
                sendCommand(finalCommand);
            } else {
                setOrbState("idle", "Sofia is ready");
                // If it timed out due to silence but continuous mode is active, restart listening
                if (window.continuousMode) {
                    triggerVoiceCommand();
                }
            }
            commandInput.placeholder = "Type a command...";
        };

        recognition.onerror = (event) => {
            setOrbState("idle", "Sofia is ready");
            if (event.error !== 'no-speech') {
                addMessage("Microphone error: " + event.error, "system");
            }
            commandInput.placeholder = "Type a command...";
        };

        try {
            recognition.start();
        } catch (e) {
            console.error("Could not start recognition:", e);
        }
    }

    // Event Listeners
    sendBtn.addEventListener("click", () => sendCommand(commandInput.value));
    
    commandInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendCommand(commandInput.value);
        }
    });

    micBtn.addEventListener("click", triggerVoiceCommand);
});

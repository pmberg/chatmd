import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import './App.css';

// ChatView Component
function ChatView({
                      messages,
                      input,
                      clarificationNeeded,
                      isBotThinking,
                      handleSendMessage,
                      setInput,
                      handleSelection
                  }) {
    return (
        <div className="chat-container">
            <div className="chat-window">
                {messages.map((message, index) => (
                    <div key={index} className={`message ${message.sender}`}>
                        {message.text}
                    </div>
                ))}
                {isBotThinking && <div className="message bot">Thinking...</div>}
            </div>

            {!clarificationNeeded ? (
                <div className="input-area">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => { if (e.key === 'Enter') handleSendMessage(); }}
                        placeholder="Describe your symptoms..."
                    />
                    <button onClick={handleSendMessage}>Send</button>
                </div>
            ) : (
                <div className="clarification-options">
                    <button onClick={() => handleSelection('Yes')}>Yes</button>
                    <button onClick={() => handleSelection('No')}>No</button>
                </div>
            )}
        </div>
    );
}

// DashboardView Component
function DashboardView({ subsequentMessages }) {
    const diseases = [];
    let startIndex = 1; // Skip the first summary message

    for (let i = startIndex; i < subsequentMessages.length; i+=2) {
        const description = subsequentMessages[i]?.text;
        if (!description) {
            console.error(`Expected a description at index ${i}, but found none.`);
            continue;
        }

        const potentialScore = subsequentMessages[i+1]?.text;
        if (!potentialScore || !potentialScore.includes(',')) {
            console.error(`Expected a score string at index ${i+1}, but found: ${potentialScore}`);
            continue;
        }

        const [diseaseName, scoreStr] = potentialScore.split(',');
        const score = parseFloat(scoreStr);

        if (!isNaN(score) && score >= 0 && score <= 100) {
            diseases.push({
                name: diseaseName,
                score: score,
                description: description
            });
        } else {
            console.error(`Invalid score for ${diseaseName}: ${scoreStr}`);
        }
    }



    return (
        <div className="dashboard-view">
            <h2>Disease Probability Analysis</h2>

            <BarChart width={600} height={300} data={diseases}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#82ca9d" />
            </BarChart>

            {/* You can also list the descriptions below the chart if needed */}
            <ul>
                {diseases.map((disease, index) => (
                    <li key={index}>{disease.description}</li>
                ))}
            </ul>
        </div>
    );
}


function App() {
    const [messages, setMessages] = useState([{ text: 'Hello! Please enter your symptoms.', sender: 'bot' }]);
    const [subsequentMessages, setSubsequentMessages] = useState([]);
    const [input, setInput] = useState('');
    const [clarificationNeeded, setClarificationNeeded] = useState(false);
    const [isBotThinking, setIsBotThinking] = useState(false);
    const [darkMode, setDarkMode] = useState(false);
    const [receivedMessageCount, setReceivedMessageCount] = useState(0);
    const [currentView, setCurrentView] = useState('chat'); // 'chat' or 'dashboard'



    async function listenForEvents(url, data, onMessageCallback) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.body) throw new Error("Failed to get response stream");

        const reader = response.body.getReader();
        let decoder = new TextDecoder();

        reader.read().then(function processStream(result) {
            if (result.done) return;
            const message = decoder.decode(result.value, { stream: true });
            if (message) {
                onMessageCallback(message);
            }
            return reader.read().then(processStream);
        });
    }


    const sendSymptomsToServer = async (symptoms) => {
        try {
            // Trigger initial diagnosis request
            const response = await fetch('http://localhost:8000/diagnose/request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ symptoms: symptoms })
            });

            // Check for errors from the server
            if(!response.ok) {
                throw new Error('Server response was not okay.');
            }

            // Listen for streamed events
            listenForEvents('http://localhost:8000/diagnose/stream', { symptoms: symptoms }, (message) => {
                console.log("Received message:", message);
                setIsBotThinking(false);

                setReceivedMessageCount(prevCount => {
                    const nextCount = prevCount + 1;

                    if (nextCount === 1) {
                        setMessages(prevMessages => [...prevMessages, { text: message, sender: 'bot' }]);
                    }
                    else if (nextCount === 2) {
                        setMessages(prevMessages => [...prevMessages, { text: message, sender: 'bot' }]);
                        setClarificationNeeded(true);
                    }
                    else if (!clarificationNeeded) {
                        setSubsequentMessages(prevSubsequent => [...prevSubsequent, { text: message, sender: 'bot' }]);
                    }

                    return nextCount;
                });
            });

        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
            setMessages(prevMessages => [...prevMessages, { text: "Sorry, I couldn't process your request at the moment.", sender: 'bot' }]);
        }
    };

    useEffect(() => {
        if (subsequentMessages.length >= 10) {
            setCurrentView('dashboard');
        }
    }, [subsequentMessages]);


    const handleSendMessage = async () => {
        if (input.trim() !== '') {
            setMessages([...messages, { text: input, sender: 'user' }]);
            setInput('');
            setIsBotThinking(true);
            await sendSymptomsToServer(input);
        }
    };

    const handleSelection = (selection) => {
        setMessages([...messages, { text: selection, sender: 'user' }]);
        setClarificationNeeded(false);
    };


    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
    }





    return (
        <div className={`App ${darkMode ? 'dark-mode' : ''}`}>
            <header className="App-header">
                <h2>ChatMD</h2>
                <div className="menu">
                    <ul>
                        <li><a href="#home">Home</a></li>
                        <li><a href="#about">About</a></li>
                        <li><a href="#services">Services</a></li>
                        <li><a href="#blog">Blog</a></li>
                        <li><a href="#contact">Contact</a></li>
                        <li><a href="#settings">Settings</a></li>
                    </ul>
                    <div className="dark-mode-toggle">
                        <label onClick={toggleDarkMode}>
                            {darkMode ? '☀️' : '🌙'}
                        </label>
                    </div>
                </div>
            </header>
            <div className="content-container">
                {currentView === 'chat' ? (
                    <ChatView
                        messages={messages}
                        input={input}
                        clarificationNeeded={clarificationNeeded}
                        isBotThinking={isBotThinking}
                        handleSendMessage={handleSendMessage}
                        setInput={setInput}
                        handleSelection={handleSelection}
                    />
                ) : (
                    <DashboardView subsequentMessages={subsequentMessages} />
                )}
            </div>
            <footer className="App-footer">
                <span>&copy; 2023 ChatMD. All rights reserved.</span>
            </footer>
        </div>
    );
}

export default App;

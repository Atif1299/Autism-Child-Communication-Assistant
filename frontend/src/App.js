import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

// --- Child Selection Component ---
const ChildSelector = ({ children, onSelect, onShowRegister }) => (
  <div className="card">
    <h2>Select a Child</h2>
    <div className="child-list">
      {children.map(child => (
        <button key={child.name} onClick={() => onSelect(child)} className="child-select-btn">
          {child.name}
        </button>
      ))}
    </div>
    <button onClick={onShowRegister} className="register-new-btn">
      Register New Child
    </button>
  </div>
);

// --- Registration Component ---
const RegistrationForm = ({ onRegister }) => {
  const [name, setName] = useState('');
  const [school, setSchool] = useState('');
  const [home, setHome] = useState('');

  const handleRegister = async () => {
    if (!name) {
      alert('Please enter a name.');
      return;
    }
    try {
      const result = await axios.post('/api/child', { name, school, home });
      onRegister(result.data); // Pass the new child data back up
      alert('Information saved!');
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Failed to save information.');
    }
  };

  return (
    <div className="card">
      <h2>Personal Information</h2>
      <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Child's Name*" />
      <input type="text" value={school} onChange={(e) => setSchool(e.target.value)} placeholder="School Name" />
      <input type="text" value={home} onChange={(e) => setHome(e.target.value)} placeholder="Home Location" />
      <button onClick={handleRegister}>Save & Start</button>
    </div>
  );
};

// --- Communication Component ---
const CommunicationUI = ({ child, onGoBack }) => {
  const [message, setMessage] = useState('');
  const [completedMessage, setCompletedMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [ttsText, setTtsText] = useState(''); // This will now hold the agent's response
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = speechSynthesis.getVoices();
      if (availableVoices.length > 0) {
        setVoices(availableVoices);
        setSelectedVoice(availableVoices[0]); // Set a default voice
      }
    };
    // Voices are loaded asynchronously
    speechSynthesis.onvoiceschanged = loadVoices;
    loadVoices(); // Initial call
  }, []);

  const handleCompleteSentence = async () => {
    if (!message) return;
    setIsLoading(true);
    setCompletedMessage('');
    setTtsText('');
    try {
      const result = await axios.post('/api/communicate', {
        text: message,
        user_info: { name: child.name },
      });
      setCompletedMessage(result.data.reply);
    } catch (error) {
      console.error('Sentence completion failed:', error);
      setCompletedMessage('Sorry, could not complete the sentence.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetResponse = async () => {
    if (!completedMessage) return;
    setIsLoading(true);
    try {
      const result = await axios.post('/api/respond', {
        text: completedMessage, // Send the *completed* message for context
        user_info: { name: child.name },
      });
      setTtsText(result.data.reply);
    } catch (error) {
      console.error('Getting response failed:', error);
      setTtsText('Sorry, something went wrong.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleListen = () => {
    if (isListening) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsListening(false);
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
        }
        if (finalTranscript) setMessage(prev => prev + finalTranscript);
      };
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      recognition.onend = () => setIsListening(false);
      setMessage('');
      recognition.start();
    } else {
      alert('Speech recognition is not supported in this browser.');
    }
  };

  const handleSpeak = () => {
    if (ttsText && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(ttsText);
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }
      speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="main-grid">
      <div className="card">
        <h2>Complete a Sentence for {child.name}</h2>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Type or speak..." rows="4" />
        <div className="button-group">
          <button onClick={handleCompleteSentence} disabled={isLoading}>{isLoading ? 'Completing...' : 'Complete'}</button>
          <button onClick={handleListen} className={isListening ? 'listening' : ''}>{isListening ? 'Stop' : 'Listen'}</button>
        </div>
        {completedMessage && (
          <div className="response-box">
            <h3>Completed Message:</h3>
            <p>{completedMessage}</p>
            <button onClick={handleGetResponse} disabled={isLoading} className="get-response-btn">
              {isLoading ? 'Getting Response...' : 'Get Agent Response'}
            </button>
          </div>
        )}
      </div>
      <div className="card">
        <h2>Agent's Response</h2>
        <textarea value={ttsText} readOnly placeholder="Agent's response will appear here..." rows="4" />
        <div className="voice-controls">
          <select 
            value={selectedVoice ? selectedVoice.name : ''} 
            onChange={(e) => setSelectedVoice(voices.find(v => v.name === e.target.value))}
            disabled={voices.length === 0}
          >
            {voices.map(voice => (
              <option key={voice.name} value={voice.name}>
                {voice.name} ({voice.lang})
              </option>
            ))}
          </select>
          <button onClick={handleSpeak} disabled={!ttsText}>Read Aloud</button>
        </div>
      </div>
    </div>
  );
};


// --- Main App Component ---
function App() {
  const [view, setView] = useState('loading'); // loading, select, register, chat
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);

  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const response = await axios.get('/api/children');
        setChildren(response.data);
        setView('select');
      } catch (error) {
        console.error("Failed to fetch children:", error);
        setView('register'); // Fallback to register if fetch fails
      }
    };
    fetchChildren();
  }, []);

  const handleSelectChild = (child) => {
    setSelectedChild(child);
    setView('chat');
  };

  const handleShowRegister = () => {
    setView('register');
  };

  const handleRegisterChild = (newChild) => {
    setChildren([...children, newChild]);
    setSelectedChild(newChild);
    setView('chat');
  };

  const renderView = () => {
    switch (view) {
      case 'select':
        return <ChildSelector children={children} onSelect={handleSelectChild} onShowRegister={handleShowRegister} />;
      case 'register':
        return <RegistrationForm onRegister={handleRegisterChild} />;
      case 'chat':
        return <CommunicationUI child={selectedChild} onGoBack={() => setView('select')} />;
      case 'loading':
      default:
        return <div className="card"><h2>Loading...</h2></div>;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Autism Child Communication Assistant</h1>
        {view === 'chat' && (
          <button onClick={() => setView('select')} className="back-btn">
            Change Child
          </button>
        )}
      </header>
      <main>{renderView()}</main>
    </div>
  );
}

export default App;

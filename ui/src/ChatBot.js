import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

const ML_MODEL_API_URL = 'https://8000-01j2p5y0y9ps76xz87h2x9efcj.cloudspaces.litng.ai/process';

function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const selectedCards = location.state?.selectedCards || [];

  useEffect(() => {
    setMessages([{ text: "Welcome! How can I assist you with your selected credit cards?", user: false }]);
  }, []);

  const formatResponse = (responseData) => {
    if (!Array.isArray(responseData) || responseData.length === 0) {
      return "I'm sorry, I couldn't find any relevant information.";
    }

    // Sort the cards by rate in descending order
    const sortedCards = responseData.sort((a, b) => b.rate - a.rate);

    let formattedResponse = '';

    if (sortedCards.length === 1) {
      const card = sortedCards[0];
      formattedResponse = `The best reward card for this category is:

${formatCardInfo(card)}`;
    } else {
      const bestCard = sortedCards[0];
      formattedResponse = `The best reward card for this category is:

${formatCardInfo(bestCard)}

Other cards and their rewards:

${sortedCards.slice(1).map(formatCardInfo).join('\n\n')}`;
    }

    return formattedResponse;
  };

  const formatCardInfo = (item) => {
    return `
${item.creditCard}:
• Category: ${item.categoryName}
• Rate: ${item.rate}%
• Additional Info: ${item.additionalInfo}
    `.trim();
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setMessages(prevMessages => [...prevMessages, { text: userMessage, user: true }]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(ML_MODEL_API_URL, {
        creditCards: selectedCards,
        query: userMessage
      });

      const formattedResponse = formatResponse(response.data);
      setMessages(prevMessages => [...prevMessages, { text: formattedResponse, user: false }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prevMessages => [...prevMessages, { text: 'Sorry, I encountered an error while processing your request. Please try again later.', user: false }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToSelection = () => {
    navigate('/');
  };

  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <button className="back-button" onClick={handleBackToSelection}>
          ← Back to Card Selection
        </button>
        <div className="selected-cards">
          Selected Cards: {selectedCards.join(', ')}
        </div>
      </div>
      <div className="message-list">
        {messages.map((message, index) => (
          <div key={index} className={`message-wrapper ${message.user ? 'user-message-wrapper' : 'bot-message-wrapper'}`}>
            <div className={`message ${message.user ? 'user-message' : 'bot-message'}`}>
              {message.text}
            </div>
          </div>
        ))}
      </div>
      <form className="input-area" onSubmit={sendMessage}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message here..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

export default ChatBot;
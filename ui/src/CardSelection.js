import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const CREDIT_CARDS = [
  { name: "RBC Cash Back Mastercard", icon: "💳" },
  { name: "BMO CashBack Mastercard", icon: "🥇" },
  { name: "CIBC Dividend Visa Card", icon: "🏆" },
  { name: "Amex SimplyCash Preferred Card", icon: "🔍" },
  { name: "Chase Sapphire", icon: "💎" }
];

function CardSelection() {
  const [selectedCards, setSelectedCards] = useState([]);
  const navigate = useNavigate();

  const handleCardToggle = (cardName) => {
    setSelectedCards(prevSelected =>
      prevSelected.includes(cardName)
        ? prevSelected.filter(name => name !== cardName)
        : [...prevSelected, cardName]
    );
  };

  const handleStartChat = () => {
    if (selectedCards.length > 0) {
      navigate('/chat', { state: { selectedCards } });
    }
  };

  return (
    <div className="card-selection-container">
      <div className="spendify-title">
        <h1>SPENDIFY</h1>
        <p className="tagline">spend wisely</p>
      </div>
      <h2 className="subtitle">Select Your Credit Cards</h2>
      <p className="description">Choose the cards you'd like to discuss in the chat</p>
      <div className="card-grid-container">
        <div className="card-grid">
          {CREDIT_CARDS.map(card => (
            <div
              key={card.name}
              className={`card ${selectedCards.includes(card.name) ? 'selected' : ''}`}
              onClick={() => handleCardToggle(card.name)}
            >
              <div className="card-icon">{card.icon}</div>
              <div className="card-name">{card.name}</div>
            </div>
          ))}
        </div>
      </div>
      <button 
        className="start-chat-button"
        onClick={handleStartChat} 
        disabled={selectedCards.length === 0}
      >
        Start Chat
      </button>
    </div>
  );
}

export default CardSelection;
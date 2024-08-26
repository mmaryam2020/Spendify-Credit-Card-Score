import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CardSelection from './CardSelection';

function Home() {
  const navigate = useNavigate();

  const handleStartChat = (selectedCards) => {
    navigate('/chat', { state: { selectedCards } });
  };

  return (
    <div className="home">
      <h1>Welcome to CREDBot</h1>
      <CardSelection onStartChat={handleStartChat} />
    </div>
  );
}

export default Home;
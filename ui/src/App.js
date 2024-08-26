import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CardSelection from './CardSelection';
import ChatBot from './ChatBot';

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<CardSelection />} />
          <Route path="/chat" element={<ChatBot />} />
          
        </Routes>
      </div>
    </Router>
  );
}

export default App;
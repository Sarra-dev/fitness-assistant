// src/App.js
import React from 'react';
import Header from './components/Header';
import ChatBox from './components/ChatBox';
import FitnessExercises from "./components/FitnessExercises";
import './App.css';

const App = () => {
  return (
    <div className="App">
      <Header />
      
      <div className="welcome-section">
        <h1>Your Personal Fitness Assistant</h1>
        <p>Get personalized workout plans and nutrition advice tailored to your fitness goals, 
          schedule, and preferences. Start your fitness journey today!</p>
      </div>
      
      <div className="app-content">
        <div className="chat-column">
          <ChatBox />
        </div>
        
        <div className="info-column">
          <div className="info-card">
            <h3>Benefits</h3>
            <ul>
              <li>Personalized workout plans</li>
              <li>Custom nutrition advice</li>
              <li>Progress tracking</li>
              <li>Expert guidance 24/7</li>
            </ul>
          </div>
        </div>
      </div>
      
      <FitnessExercises />
    </div>
  );
};

export default App;
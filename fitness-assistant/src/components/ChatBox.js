import React, { useState, useEffect, useRef } from 'react';
import { sendMessageToApi } from '../services/api';
import Message from './Message';

const ChatBox = () => {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your fitness assistant. I can help you create a personalized workout and diet plan. What are your fitness goals?", isUser: false }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (input.trim()) {
      const question = input.trim();
      const userMessage = { text: question, isUser: true };
      // previous conversation (without the greeting) so the assistant keeps context
      const history = messages.slice(1).map(m => ({
        role: m.isUser ? 'user' : 'assistant',
        text: m.text,
      }));
      setMessages(prev => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        const botResponse = await sendMessageToApi(question, history);
        // Handle both response formats (object or string)
        const responseText = typeof botResponse === 'object' ? botResponse.response : botResponse;
        const sources = typeof botResponse === 'object' ? botResponse.sources : null;
        
        setMessages(prev => [...prev, { 
          text: responseText, 
          isUser: false,
          sources: sources
        }]);
      } catch (error) {
        console.error("API Error:", error);
        setMessages(prev => [...prev, { 
          text: "Sorry, I could not reach the server. Make sure the backend is running and try again.", 
          isUser: false 
        }]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="chat-box">
      <div className="messages">
        {messages.map((msg, index) => (
          <Message 
            key={index} 
            text={msg.text} 
            isUser={msg.isUser} 
            sources={msg.sources}
          />
        ))}
        {isLoading && (
          <div className="bot-typing-indicator">
            <span>•</span>
            <span>•</span>
            <span>•</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="message-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask about workouts, nutrition, or fitness goals..."
          disabled={isLoading}
        />
        <button 
          onClick={handleSendMessage}
          disabled={isLoading}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
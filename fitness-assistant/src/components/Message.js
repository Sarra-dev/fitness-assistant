
import React from 'react';

const Message = ({ text, isUser, isReasoningStep, sources }) => {
  // Ensure text is not null or empty to avoid rendering issues
  if (!text || text.trim() === '') {
    return null;
  }

  // Function to format workout & diet plans
  const formatMessage = (text) => {
    const headers = ["WORKOUT PLAN:", "DIET PLAN:"];

    // Check if the message contains a workout or diet plan
    const hasPlan = headers.some(header => text.includes(header));

    if (hasPlan) {
      const parts = text.split(/(WORKOUT PLAN:|DIET PLAN:)/g);

      return (
        <>
          {parts.map((part, index) => {
            if (headers.includes(part)) {
              return <strong key={index} className="plan-header">{part}</strong>;
            } else if (index > 0 && headers.includes(parts[index - 1])) {
              return (
                <div key={index} className="plan-content">
                  {part.split('\n').map((line, i) => (
                    <p key={i}>{line.trim()}</p>
                  ))}
                </div>
              );
            } else {
              return <span key={index}>{part}</span>;
            }
          })}
        </>
      );
    }

    // Regular message formatting (preserving new lines)
    return text.split('\n').map((line, index) => (
      <p key={index} className="regular-message">{line}</p>
    ));
  };

  return (
    <div className={`message ${isUser ? 'user' : 'bot'} ${isReasoningStep ? 'reasoning-step' : ''}`}>
      {isReasoningStep && <span className="reasoning-icon">🧠</span>}
      {formatMessage(text)}
      {!isUser && sources && sources.length > 0 && (
        <div className="message-sources">
          <span>Sources: </span>
          {sources.map((s) => s.title).join(' · ')}
        </div>
      )}
    </div>
  );
};

export default Message;

// src/services/api.js
// The backend URL comes from the .env file (REACT_APP_API_URL).
const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json();
}

// Send a question (plus the previous messages, so the assistant keeps context)
export const sendMessageToApi = (message, history = []) =>
  request('/chatFitness', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: message, history }),
  });

// Load the exercise library
export const fetchFitnessExercises = () => request('/fitness-exercises');

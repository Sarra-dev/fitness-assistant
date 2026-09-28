import React, { useEffect, useState } from "react";
import { fetchFitnessExercises } from "../services/api";

const FitnessExercises = () => {
    const [exercises, setExercises] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadExercises = async () => {
            try {
                setLoading(true);
                const data = await fetchFitnessExercises();
                setExercises(data);
                setError(null);
            } catch (error) {
                console.error("Failed to load fitness exercises:", error);
                setError("Failed to load exercises. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        loadExercises();
    }, []);

    return (
        <div className="exercises-container">
            <h2>Fitness Exercises</h2>
            
            {loading ? (
                <p>Loading exercises...</p>
            ) : error ? (
                <p className="error-message">{error}</p>
            ) : (
                <div className="exercise-list">
                    {exercises.map((exercise, index) => (
                        <div key={index} className="exercise-card">
                            <h3>{exercise.title}</h3>
                            {exercise.description && (
                                <p>{exercise.description}</p>
                            )}
                            {exercise.category && (
                                <span className="exercise-category">{exercise.category}</span>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FitnessExercises;
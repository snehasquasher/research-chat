import React from 'react';

interface ScoreDisplayProps {
  label: string;
  score: number | string;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ label, score }) => (
  <div className="bg-white shadow-md rounded-lg p-4 border border-gray-200">
    <div className="text-sm font-semibold text-gray-700">{label}</div>
    <div className="text-lg font-bold text-green-600">{score}</div>
  </div>
);

export default ScoreDisplay;

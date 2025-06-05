import React from 'react';

interface SuggestionCardProps {
  imageUrl: string;
  text: string;
}

const SuggestionCard: React.FC<SuggestionCardProps> = ({ imageUrl, text }) => (
  <div className="flex flex-col items-center bg-[var(--color-secondary)]/80 rounded-2xl shadow-lg p-4 w-48 min-w-[180px] max-w-[200px] cursor-pointer hover:scale-105 transition-transform duration-200 border border-[var(--color-background)]">
    <img src={imageUrl} alt={text} className="w-20 h-20 object-cover rounded-lg mb-3 shadow-md" />
    <span className="text-[var(--color-text)] text-base font-medium text-center leading-tight line-clamp-2">{text}</span>
  </div>
);

export default SuggestionCard; 
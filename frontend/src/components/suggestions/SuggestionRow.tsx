import React from 'react';
import SuggestionCard from './SuggestionCard';

interface Suggestion {
  imageUrl: string;
  text: string;
}

interface SuggestionRowProps {
  suggestions: Suggestion[];
}

const SuggestionRow: React.FC<SuggestionRowProps> = ({ suggestions }) => (
  <div className="w-full max-w-5xl mx-auto mt-6 mb-10 overflow-x-auto scrollbar-hide">
    <div className="flex gap-6">
      {suggestions.map((s, idx) => (
        <SuggestionCard key={idx} imageUrl={s.imageUrl} text={s.text} />
      ))}
    </div>
  </div>
);

export default SuggestionRow; 
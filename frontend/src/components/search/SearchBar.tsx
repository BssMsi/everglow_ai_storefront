// frontend/src/components/search/SearchBar.tsx
'use client'; // For using hooks like useState

import { useState } from 'react';
import { Search, Mic, X, MessageSquare, PlusCircle } from 'lucide-react'; // Using lucide-react for icons

const SearchBar = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [conversationHistory, setConversationHistory] = useState([
    { user: 'Hi EverGlow!', agent: 'Hello! How can I help you glow today?' },
    { user: 'Any new serums?', agent: 'Yes! Our Radiant Glow Serum is a bestseller.' },
  ]);
  const latestResponse = "Agent: Radiant Glow Serum is popular!"; // Max 6-7 words

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Dummy action: add to conversation
    if (searchTerm.trim()) {
      setConversationHistory([
        ...conversationHistory,
        { user: searchTerm, agent: `Searching for ${searchTerm}... (dummy)` },
      ]);
      setSearchTerm('');
    }
  };

  return (
    <div className="my-8 p-4 bg-white shadow-lg rounded-lg">
      {!isExpanded ? (
        // Collapsed View
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setIsExpanded(true)}
        >
          <div className="flex items-center">
            <MessageSquare size={20} className="text-pink-500 mr-2" />
            <p className="text-gray-600 italic truncate">
              {latestResponse}
            </p>
          </div>
          <Search size={24} className="text-gray-500" />
        </div>
      ) : (
        // Expanded View
        <div>
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-gray-700">AI Assistant</h3>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-gray-500 hover:text-gray-700"
              aria-label="Collapse search"
            >
              <X size={24} />
            </button>
          </div>

          {/* Conversation History */}
          <div className="max-h-60 overflow-y-auto mb-4 p-3 bg-gray-50 rounded-md space-y-3">
            {conversationHistory.map((entry, index) => (
              <div key={index}>
                <p className="text-sm text-blue-600 font-medium">You: {entry.user}</p>
                <p className="text-sm text-pink-600">Agent: {entry.agent}</p>
              </div>
            ))}
          </div>

          {/* Search Input */}
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Ask EverGlow..."
              className="flex-grow p-2 border border-gray-300 rounded-md focus:ring-pink-500 focus:border-pink-500"
            />
            <button
              type="button" // To prevent form submission if not intended
              className="p-2 bg-green-500 text-white rounded-md hover:bg-green-600"
              aria-label="Activate voice search"
            >
              <Mic size={20} />
            </button>
            <button
              type="submit"
              className="p-2 bg-pink-500 text-white rounded-md hover:bg-pink-600"
              aria-label="Send search"
            >
              <Search size={20} />
            </button>
          </form>
          <button
            onClick={() => {
              setConversationHistory([]);
              // Potentially clear other session related state
              alert('New search session started (dummy action)');
            }}
            className="mt-3 text-sm text-blue-500 hover:text-blue-700 flex items-center"
          >
            <PlusCircle size={16} className="mr-1" /> Start New Session
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchBar;

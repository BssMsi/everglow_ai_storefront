"use client";

import * as React from "react";
import { useEffect, useRef, useCallback, useState } from "react";
import {
  Search,
  ArrowLeft,
  SendIcon,
  XIcon,
  LoaderIcon,
  MessageSquare,
  Bot,
  User,
} from "lucide-react";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";

interface Message {
  id: string;
  content: string;
  sender: "user" | "agent";
  timestamp: Date;
}

interface ChatSearchBarProps {
  placeholder?: string;
  onSearch?: (value: string) => void;
}

interface UseAutoResizeTextareaProps {
  minHeight: number;
  maxHeight?: number;
}

function useAutoResizeTextarea({
  minHeight,
  maxHeight,
}: UseAutoResizeTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`;
      const newHeight = Math.max(
        minHeight,
        Math.min(
          textarea.scrollHeight,
          maxHeight ?? Number.POSITIVE_INFINITY
        )
      );

      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight]
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = `${minHeight}px`;
    }
  }, [minHeight]);

  useEffect(() => {
    const handleResize = () => adjustHeight();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [adjustHeight]);

  return { textareaRef, adjustHeight };
}

function TypingDots() {
  return (
    <div className="flex items-center ml-1">
      {[1, 2, 3].map((dot) => (
        <motion.div
          key={dot}
          className="w-1.5 h-1.5 bg-foreground/90 rounded-full mx-0.5"
          initial={{ opacity: 0.3 }}
          animate={{ 
            opacity: [0.3, 0.9, 0.3],
            scale: [0.85, 1.1, 0.85]
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            delay: dot * 0.15,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

export function ChatSearchBar({
  placeholder = "Search or ask a question...",
  onSearch,
}: ChatSearchBarProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! How can I help you today?",
      sender: "agent",
      timestamp: new Date(),
    },
  ]);
  const containerRef = useRef<HTMLDivElement>(null);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 40,
    maxHeight: 120,
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const transition = {
    type: "spring",
    bounce: 0.15,
    duration: 0.5,
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        if (isExpanded) {
          setIsExpanded(false);
        }
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isExpanded]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    adjustHeight(true);
    
    // Simulate agent typing
    setIsTyping(true);
    
    // Simulate agent response after delay
    setTimeout(() => {
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `I found this information about "${inputValue}". Let me know if you need more details.`,
        sender: "agent",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, agentMessage]);
      setIsTyping(false);
    }, 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const latestAgentMessage = messages
    .filter(msg => msg.sender === "agent")
    .pop();

  return (
    <div className="flex flex-col items-center w-full mt-8 mb-8">
      <div className="w-full max-w-2xl">
        {!isExpanded ? (
          <div
            className="flex items-center bg-[var(--color-secondary)] rounded-full px-6 py-3 shadow-lg w-full cursor-pointer"
            onClick={() => setIsExpanded(true)}
          >
            <Search className="text-white opacity-70 mr-3" size={22} />
            <input
              type="text"
              value={latestAgentMessage?.content || ''}
              readOnly
              className="flex-1 bg-transparent text-white text-base border-none outline-none placeholder:text-white/60 cursor-pointer"
              placeholder="Ask something..."
            />
            <button
              className="ml-3 text-white/60 hover:text-white"
              onClick={e => { e.stopPropagation(); setInputValue(''); }}
            >
              <XIcon size={22} />
            </button>
          </div>
        ) : (
          <div className="bg-[var(--color-secondary)] rounded-2xl p-6 shadow-xl w-full">
            <div className="flex items-center mb-4">
              <Search className="text-white opacity-70 mr-3" size={22} />
              <input
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                className="flex-1 bg-transparent text-white text-base border-none outline-none placeholder:text-white/60"
                placeholder="Type your question..."
                onKeyDown={handleKeyDown}
              />
              <button
                className="ml-3 text-white/60 hover:text-white"
                onClick={() => setIsExpanded(false)}
              >
                <XIcon size={22} />
              </button>
            </div>
            <div className="max-h-60 overflow-y-auto space-y-4">
              {messages.map((msg, idx) => (
                <div key={msg.id} className="flex flex-col">
                  <span className="text-sm text-blue-300 font-semibold mb-1">{msg.sender === 'user' ? 'You' : 'Agent'}</span>
                  <span className="text-base text-white mb-2">{msg.content}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatSearchBarDemo() {
  return (
    <div className="min-h-screen bg-background text-foreground p-4 flex flex-col">
      <div className="flex-1 w-full max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Expandable Chat Search Bar</h1>
        <p className="mb-2">This is a demo of an expandable chat search bar component.</p>
        <p className="mb-8">Click on the search bar below to expand it and see the full chat interface.</p>
        
        <div className="border border-border rounded-lg p-4 mb-4">
          <h2 className="font-medium mb-2">Sample Content</h2>
          <p className="text-muted-foreground">
            This content will be pushed down when the chat expands. Try clicking on the search bar below.
          </p>
        </div>
        
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="border border-border rounded-lg p-4 mb-4">
            <h3 className="font-medium mb-2">Content Section {i + 1}</h3>
            <p className="text-muted-foreground">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod, nisl eget
              aliquam ultricies, nunc nisl aliquet nunc, quis aliquam nisl nunc quis nisl.
            </p>
          </div>
        ))}
      </div>
      
      <ChatSearchBar />
    </div>
  );
} 
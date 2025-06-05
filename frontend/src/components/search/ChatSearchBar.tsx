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
      id: "initial-agent-message",
      content: "Hello! How can I help you find the perfect vegan skincare?",
      sender: "agent",
      timestamp: new Date(),
    },
  ]);
  const containerRef = useRef<HTMLDivElement>(null);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 48, // Increased minHeight for better proportions
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => { // Changed HTMLInputElement to HTMLTextAreaElement for onKeyDown
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const latestAgentMessage = messages
    .filter(msg => msg.sender === "agent")
    .pop();

  return (
    <div className="flex flex-col items-center w-full mt-8 mb-4"> {/* Adjusted mb for suggestions */}
      <div className="w-full max-w-2xl" ref={containerRef}>
        <MotionConfig transition={transition}>
          <AnimatePresence mode="popLayout">
            {!isExpanded ? (
              <motion.div
                key="search-bar-condensed"
                layoutId="search-bar"
                className="flex items-center bg-[var(--color-secondary)] rounded-full px-5 py-3.5 shadow-lg w-full cursor-text group focus-within:ring-2 focus-within:ring-[var(--color-primary)] focus-within:ring-opacity-50 transition-all duration-300 ease-in-out"
                onClick={() => setIsExpanded(true)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
              >
                <Search className="h-5 w-5 text-gray-400 group-hover:text-gray-200 transition-colors" />
                <span className="ml-3 text-gray-400 group-hover:text-gray-300 transition-colors truncate">
                  {placeholder}
                </span>
              </motion.div>
            ) : (
              <motion.div
                key="search-bar-expanded"
                layoutId="search-bar"
                className="flex flex-col bg-[var(--color-secondary)] rounded-2xl shadow-2xl w-full overflow-hidden border border-[var(--color-accent-dark)]"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
              >
                {/* Header of expanded view */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--color-accent-dark)]">
                  <div className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-[var(--color-primary)]" />
                    <span className="text-sm font-medium text-white">EcoSkin Assistant</span>
                  </div>
                  <button 
                    onClick={() => setIsExpanded(false)} 
                    className="p-1.5 rounded-full hover:bg-[var(--color-accent-dark)] transition-colors text-gray-400 hover:text-white"
                    aria-label="Close chat"
                  >
                    <XIcon className="h-5 w-5" />
                  </button>
                </div>

                {/* Messages Area */}
                <div className="flex-grow p-4 space-y-4 overflow-y-auto h-72 scrollbar-thin scrollbar-thumb-[var(--color-accent-dark)] scrollbar-track-[var(--color-secondary)]">
                  {messages.map((msg) => (
                    <motion.div
                      key={msg.id}
                      layout
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div 
                        className={`max-w-[75%] p-3 rounded-xl text-sm ${ 
                          msg.sender === "user" 
                            ? "bg-[var(--color-primary)] text-white rounded-br-none"
                            : "bg-[var(--color-background)] text-gray-200 rounded-bl-none border border-[var(--color-accent-dark)]"
                        }`}
                      >
                        {msg.content}
                      </div>
                    </motion.div>
                  ))}
                  {isTyping && (
                    <motion.div 
                      className="flex justify-start"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                       <div className="max-w-[75%] p-3 rounded-xl bg-[var(--color-background)] text-gray-200 rounded-bl-none border border-[var(--color-accent-dark)] flex items-center">
                        <span className="mr-1 text-xs">EcoSkin is typing</span><TypingDots />
                       </div>
                    </motion.div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-3 border-t border-[var(--color-accent-dark)] bg-[var(--color-secondary)]">
                  <div className="flex items-end bg-[var(--color-background)] rounded-xl p-1.5 border border-[var(--color-accent-dark)] focus-within:ring-2 focus-within:ring-[var(--color-primary)] focus-within:ring-opacity-50">
                    <textarea
                      ref={textareaRef}
                      value={inputValue}
                      onChange={(e) => {
                        setInputValue(e.target.value);
                        adjustHeight();
                      }}
                      onKeyDown={handleKeyDown} // Make sure this is attached to the textarea
                      placeholder="Ask about vegan skincare..."
                      className="flex-grow bg-transparent text-white placeholder-gray-500 focus:outline-none resize-none overflow-y-auto scrollbar-thin scrollbar-thumb-[var(--color-accent-dark)] scrollbar-track-transparent p-2 text-sm"
                      rows={1}
                    />
                    <button 
                      onClick={handleSendMessage} 
                      disabled={!inputValue.trim() || isTyping}
                      className="p-2.5 rounded-lg bg-[var(--color-primary)] text-white hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-background)] focus-visible:ring-[var(--color-primary)] ml-2 self-end"
                      aria-label="Send message"
                    >
                      {isTyping ? (
                        <LoaderIcon className="h-4 w-4 animate-spin" />
                      ) : (
                        <SendIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </MotionConfig>
      </div>
    </div>
  );
}
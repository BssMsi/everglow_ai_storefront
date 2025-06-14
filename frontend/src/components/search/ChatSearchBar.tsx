"use client";

import * as React from "react";
import { useEffect, useRef, useCallback, useState } from "react";
import {
  Search,
  SendIcon,
  XIcon,
  Bot,
  Mic } from "lucide-react";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";
import { Product } from "@/types/product";
import { useTheme } from '@/context/ThemeContext';
import { changeTheme } from '@/utils/themeUtils';

interface Message {
  id: string;
  content: string;
  sender: "user" | "agent";
  timestamp: Date;
}

// Define a type for the AgentState object based on backend's AgentState.to_dict()
interface AgentState {
  history: Array<[string, string]>;
  entities: Record<string, unknown>;
  intent: string | null;
  active_agent: string | null;
  followup_questions: string[];
}

interface ChatSearchBarProps {
  // onSearch?: (value: string) => void; // Removed as it's not used. TODO: Re-evaluate if this prop is needed for future features.
  onProductsFound?: (products: Product[]) => void;
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
    <div className="flex items-center ml-[1px]">
      {[1, 2, 3].map((dot) => (
        <motion.div
          key={dot}
          className="size-[10px] bg-[var(--color-foreground)]/90 rounded-full mx-[0.5px]"
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

// Add this markdown-to-HTML converter function
function convertMarkdownToHtml(markdown: string): string {
  let html = markdown;
  
  // Convert headers
  html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mb-2 mt-3">$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mb-2 mt-4">$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mb-3 mt-4">$1</h1>');
  
  // Convert bold text
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
  html = html.replace(/__(.*?)__/g, '<strong class="font-semibold">$1</strong>');
  
  // Convert italic text
  html = html.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
  html = html.replace(/_(.*?)_/g, '<em class="italic">$1</em>');
  
  // Convert inline code
  html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>');
  
  // Convert code blocks
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto my-2"><code class="text-sm font-mono">$1</code></pre>');
  
  // Convert unordered lists
  html = html.replace(/^\* (.*$)/gim, '<li class="ml-4 list-disc">$1</li>');
  html = html.replace(/^- (.*$)/gim, '<li class="ml-4 list-disc">$1</li>');
  
  // Wrap consecutive list items in ul tags
  html = html.replace(/((<li[^>]*>.*<\/li>\s*)+)/g, '<ul class="my-2">$1</ul>');
  
  // Convert ordered lists
  html = html.replace(/^\d+\. (.*$)/gim, '<li class="ml-4 list-decimal">$1</li>');
  html = html.replace(/((<li class="ml-4 list-decimal"[^>]*>.*<\/li>\s*)+)/g, '<ol class="my-2">$1</ol>');
  
  // Convert links
  html = html.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" class="text-blue-500 hover:text-blue-700 underline" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // Convert line breaks
  html = html.replace(/\n/g, '<br>');
  
  return html;
}

export function ChatSearchBar({
  // onSearch,
  onProductsFound,
}: ChatSearchBarProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [placeholder, setPlaceholder] = useState("What can I help you with?");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "initial-agent-message",
      content: "Hello! How can I help you find the perfect vegan skincare?",
      sender: "agent",
      timestamp: new Date(),
    },
  ]);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [isListening, setIsListening] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [agentState, setAgentState] = useState<AgentState | null>(null); // <-- Add state for agentState

  // Add theme hook
  const { setThemeSettings } = useTheme();

  const containerRef = useRef<HTMLDivElement>(null);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 48, // Increased minHeight for better proportions
    maxHeight: 160, // Increased maxHeight for more input lines if needed
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
    if (isExpanded && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isExpanded]);

  const handleSendMessage = async () => { // Made async
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue; // Capture current input before clearing
    setInputValue("");
    adjustHeight(true);
    
    setIsTyping(true);
    
    try {
      // Replace with your backend API endpoint for text chat
      const response = await fetch('/api/chat', { // Assuming backend is on the same host or proxied
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Send current input and the *entire last agent state*
        body: JSON.stringify({ text: currentInput, state_dict: agentState }), 
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data:{ ai_message: string, state: unknown, product_ids?: string[], theme?: "default" | "dark" | "rose" | "teal" | "lavender" } = await response.json(); // Expecting { ai_message: "...", state: { ... }, product_ids: [] }
      
      const agentMessage: Message = {
        id: Date.now().toString(),
        content: data.ai_message,
        sender: "agent",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, agentMessage]);

      // Update agent state
      if (data.state) {
        setAgentState(data.state as AgentState); // Cast to AgentState
      }

      setPlaceholder(data.ai_message);
      if (data.product_ids && data.product_ids.length > 0){
        // Get request to the backend endpoint to retrieve product details based on the list of product_ids
        // Update the Product List on the UI
        try {
          // Using URLSearchParams (cleaner approach)
          const params = new URLSearchParams();
          data.product_ids.forEach((id: string) => params.append('ids', id));
          const productResponse = await fetch(`/api/products?${params.toString()}`);
          
          if (!productResponse.ok) {
            throw new Error(`HTTP error fetching products! status: ${productResponse.status}`);
          }
          const productsData: Product[] = await productResponse.json();
          if (onProductsFound) {
            onProductsFound(productsData);
            console.log("Products found and sent to ChatSearchBar.", productsData);
            setIsExpanded(false);
          }

          // Theme change logic: Check if theme is returned, otherwise use random theme
          if (data.theme) {
            // If backend returns a specific theme, use it
            changeTheme(data.theme, setThemeSettings);
            console.log(`Theme set from backend: ${data.theme}`);
          } else {
            // If no theme is returned, change to a random theme
            changeTheme(null, setThemeSettings);
            console.log('No theme returned from backend, switching to random theme');
          }
        } catch (productError) {
          console.error("Failed to fetch product details:", productError);
        }
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I couldn't connect to the assistant. Please try again later.",
        sender: "agent",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleVoiceSearch = () => {
    if (isListening) {
      // Stop listening
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        // Optionally send a signal that recording has stopped or rely on stream end
      }
      setIsListening(false);
      // Websocket will be closed in onclose or onerror, or kept open if desired
    } else {
      // Start listening
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Your browser does not support audio recording.");
        return;
      }

      const ws = new WebSocket('ws://localhost:8000/ws/voice-agent'); // Ensure this URL is correct
      setWebsocket(ws);

      ws.onopen = () => {
        setIsListening(true);
        console.log("WebSocket connection established for voice.");

        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(stream => {
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = event => {
              audioChunksRef.current.push(event.data);
              if (ws.readyState === WebSocket.OPEN) {
                ws.send(event.data);
              }
            };

            mediaRecorderRef.current.onstop = () => {
              // Stream is stopped, clean up
              stream.getTracks().forEach(track => track.stop());
              // The final audio chunk is sent via ondataavailable before onstop
              // If ws is still open, you might send a final signal or close it
              // For now, we assume the backend handles stream end gracefully
              if (ws.readyState === WebSocket.OPEN) {
                 // ws.close(); // Decide if to close here or let backend manage
              }
            };
            
            // Start recording, send data in chunks (e.g., every second)
            mediaRecorderRef.current.start(1000); 
          })
          .catch(err => {
            console.error("Error accessing microphone:", err);
            setIsListening(false);
            ws.close();
          });
      };

      ws.onmessage = async (event) => {
        // Assuming backend sends audio bytes (TTS response)
        if (event.data instanceof Blob) {
          const audioBlob = event.data;
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          audio.play();
          // TODO: Optionally, if the backend also sends the transcript of TTS,
          // add it to messages state.
          // For now, we only play audio.
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        // Add error message to chat
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: "Voice service connection error. Please try again.",
          sender: "agent",
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      };

      ws.onclose = () => {
        console.log("WebSocket connection closed.");
        if (mediaRecorderRef.current && mediaRecorderRef.current.stream) {
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
      };
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => { // Changed HTMLInputElement to HTMLTextAreaElement for onKeyDown
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col items-center w-full mt-8 mb-4 px-4">
      <div className="w-full max-w-3xl" ref={containerRef}>
        <MotionConfig transition={transition}>
          <AnimatePresence mode="popLayout">
            {!isExpanded ? (
              <motion.div
                key="search-bar-condensed"
                layoutId="search-bar"
                className="flex items-center bg-[var(--color-secondary)] rounded-full p-[10px] shadow-lg w-full cursor-text group focus-within:ring-2 focus-within:ring-[var(--color-primary)] focus-within:ring-opacity-50 transition-all duration-300 ease-in-out border border-[var(--color-accent-dark)]/30"
                onClick={() => setIsExpanded(true)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
              >
                <Search className="h-[32px] w-[32px] text-[var(--color-primary)] group-hover:text-[var(--color-primary)]/80 transition-colors" />
                <span className="ml-[10px] text-[var(--color-foreground)]/70 group-hover:text-[var(--color-foreground)]/90 transition-colors truncate font-medium">
                  {placeholder}
                </span>
              </motion.div>
            ) : (
              <motion.div
                key="search-bar-expanded"
                layoutId="search-bar"
                className="flex flex-col bg-[var(--color-secondary)] rounded-2xl shadow-2xl w-full overflow-hidden border border-[var(--color-accent-dark)]/50"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
              >
                {/* Header of expanded view */}
                <div className="flex items-center justify-between p-[10px] border-b border-[var(--color-accent-dark)]/30 bg-[var(--color-secondary)]">
                  <div className="flex items-center gap-3">
                    <Bot className="size-6 text-[var(--color-primary)]" />
                    <span className="text-lg font-semibold text-[var(--color-foreground)]">EverGlow Labs Assistant</span>
                  </div>
                  <button 
                    onClick={() => setIsExpanded(false)} 
                    className="rounded-full bg-[transparent] hover:bg-[var(--color-accent-dark)]/30 transition-colors text-[var(--color-foreground)]/60 hover:text-[var(--color-foreground)]"
                    aria-label="Close chat"
                  >
                    <XIcon className="size-5 text-[var(--color-accent-dark)" />
                  </button>
                </div>

                {/* Messages Area */}
                <div className="flex-grow p-[10px] space-y-[10px] overflow-y-auto h-[384px] bg-[var(--color-background)] scrollbar-thin scrollbar-thumb-[var(--color-accent-dark)] scrollbar-track-transparent">
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
                        className={`max-w-[80%] p-[5px] rounded-[10px] text-sm shadow-md ${
                          msg.sender === "user" 
                            ? "bg-[var(--color-primary)] text-white rounded-br-md"
                            : "bg-[var(--color-secondary)] text-[var(--color-foreground)] rounded-bl-md border border-[var(--color-accent-dark)]/30"
                        }`}
                      >
                        {msg.sender === "agent" ? (
                          <div 
                            className="prose prose-sm max-w-none dark:prose-invert"
                            dangerouslySetInnerHTML={{ __html: convertMarkdownToHtml(msg.content) }}
                          />
                        ) : (
                          msg.content
                        )}
                      </div>
                    </motion.div>
                  ))}
                  {isTyping && (
                    <motion.div 
                      className="flex justify-start"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                       <div className="max-w-[80%] p-[5px] rounded-xl bg-[var(--color-secondary)] text-[var(--color-foreground)] rounded-bl-md border border-[var(--color-accent-dark)]/30 flex items-center shadow-md">
                        <span className="mr-[10px] text-sm">EverGlow Labs is typing</span><TypingDots />
                       </div>
                    </motion.div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-[var(--color-accent-dark)]/30 bg-[var(--color-secondary)]">
                  <div className="relative flex items-end bg-[var(--color-background)] rounded-xl border border-[var(--color-accent-dark)]/30 focus-within:ring-2 focus-within:ring-[var(--color-primary)] focus-within:ring-opacity-50 focus-within:border-[var(--color-primary)]/50">
                    <textarea
                      ref={textareaRef}
                      value={inputValue}
                      onChange={(e) => {
                        setInputValue(e.target.value);
                        adjustHeight();
                      }}
                      onKeyDown={handleKeyDown}
                      placeholder={placeholder}
                      className="flex-1 bg-transparent text-[var(--color-foreground)] placeholder-[var(--color-foreground)]/50 resize-none overflow-y-auto focus:outline-none p-[10px] text-sm leading-relaxed pr-[32px]"
                      rows={1}
                      style={{ minHeight: `${textareaRef.current?.style.minHeight || 48}px` }}
                    />
                    <div className="absolute right-[2px] top-1/2 -translate-y-1/2 flex items-center gap-[3px]">
                      {inputValue && (
                        <button
                          type="button"
                          onClick={() => {
                            setInputValue("");
                            adjustHeight(true);
                            textareaRef.current?.focus();
                          }}
                          className="p-[5px] bg-[var(--color-primary)] text-[var(--color-foreground)]/50 hover:text-[var(--color-foreground)] transition-colors rounded-full hover:bg-[var(--color-secondary)]/90"
                          aria-label="Clear input"
                        >
                          <XIcon className="size-5 text-[var(--color-accent-dark)" />
                        </button>
                      )}
                      <button
                        type="button"
                        disabled
                        onClick={handleVoiceSearch}
                        className={`p-[5px] bg-[var(--color-primary)] rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
                          isListening 
                            ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg' 
                            : 'bg-[var(--color-accent-dark)]/20 hover:bg-[var(--color-secondary)]/90 text-[var(--color-foreground)]/50 hover:text-[var(--color-foreground)]'
                        }`}
                        aria-label={isListening ? "Stop voice search" : "Start voice search"}
                      >
                        <Mic className="size-5" />
                      </button>
                      <button
                        type="button"
                        onClick={handleSendMessage}
                        disabled={!inputValue.trim() || isTyping}
                        className="p-[5px] bg-[var(--color-primary)] text-[var(--color-foreground)]/50 rounded-full hover:bg-[var(--color-secondary)]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg"
                        aria-label="Send message"
                      >
                        <SendIcon className="size-5" />
                      </button>
                    </div>
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
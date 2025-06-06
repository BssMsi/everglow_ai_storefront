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
  Mic } from "lucide-react";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";
import { Product } from "@/types/product";

interface Message {
  id: string;
  content: string;
  sender: "user" | "agent";
  timestamp: Date;
}
interface ChatSearchBarProps {
  placeholder?: string;
  onSearch?: (value: string) => void;
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
  onProductsFound,
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
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [isWsConnected, setIsWsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

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
        body: JSON.stringify({ text: currentInput, state_dict: messages }), // Send current input and history
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json(); // Expecting { response: "agent's text", state: { ... } }
      
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        // Assuming backend returns { response: { response: "actual agent text" ... } ... }
        // Or if english_agent directly returns { response: "text", state: {} }
        // Adjust based on actual backend response structure for /api/chat
        content: data.ai_message,
        sender: "agent",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, agentMessage]);

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
        setIsWsConnected(true);
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
        setIsWsConnected(false);
        setIsListening(false);
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
        setIsWsConnected(false);
        setIsListening(false);
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

  const latestAgentMessage = messages
    .filter(msg => msg.sender === "agent")
    .pop();

  return (
    <div className="flex flex-col items-center w-full mt-8 mb-4 px-4"> {/* Added horizontal padding */} 
      <div className="w-full max-w-3xl" ref={containerRef}> {/* Increased max-width for a wider search bar */} 
        <MotionConfig transition={transition}>
          <AnimatePresence mode="popLayout">
            {!isExpanded ? (
              <motion.div
                key="search-bar-condensed"
                layoutId="search-bar"
                className="flex items-center bg-[var(--color-secondary)] rounded-full px-5 py-4 shadow-lg w-full cursor-text group focus-within:ring-2 focus-within:ring-[var(--color-primary)] focus-within:ring-opacity-50 transition-all duration-300 ease-in-out"
                onClick={() => setIsExpanded(true)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
              >
                <Search className="h-5 w-5 text-gray-400 group-hover:text-gray-200 transition-colors" />
                <span className="ml-4 text-gray-400 group-hover:text-gray-300 transition-colors truncate">
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
                  <div className="flex items-center gap-3"> {/* Increased gap */}
                    <Bot className="h-6 w-6 text-[var(--color-primary)]" /> {/* Slightly larger icon */}
                    <span className="text-md font-medium text-white">EcoSkin Assistant</span> {/* Increased font size */}
                  </div>
                  <button 
                    onClick={() => setIsExpanded(false)} 
                    className="p-2 rounded-full hover:bg-[var(--color-accent-dark)] transition-colors text-gray-400 hover:text-white"
                    aria-label="Close chat"
                  >
                    <XIcon className="h-5 w-5" />
                  </button>
                </div>

                {/* Messages Area */}
                <div className="flex-grow p-4 space-y-4 overflow-y-auto h-96 scrollbar-thin scrollbar-thumb-[var(--color-accent-dark)] scrollbar-track-[var(--color-secondary)]"> {/* Increased h-72 to h-96 */}
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
                        className={`max-w-[80%] p-3.5 rounded-xl text-sm shadow-md ${
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
                       <div className="max-w-[80%] p-3.5 rounded-xl bg-[var(--color-background)] text-gray-200 rounded-bl-none border border-[var(--color-accent-dark)] flex items-center shadow-md"> {/* Increased padding and max-width, added shadow */}
                        <span className="mr-1.5 text-xs">EcoSkin is typing</span><TypingDots />
                       </div>
                    </motion.div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-3 border-t border-[var(--color-accent-dark)] bg-[var(--color-secondary)]">
                  <div className="relative flex items-end bg-[var(--color-background)] rounded-xl p-1 border border-[var(--color-accent-dark)] focus-within:ring-2 focus-within:ring-[var(--color-primary)] focus-within:ring-opacity-50"> {/* Added relative positioning */}
                    <textarea
                      ref={textareaRef}
                      value={inputValue}
                      onChange={(e) => {
                        setInputValue(e.target.value);
                        adjustHeight();
                      }}
                      onKeyDown={handleKeyDown}
                      placeholder={placeholder}
                      className="flex-1 bg-transparent text-foreground placeholder-foreground/60 resize-none overflow-y-auto focus:outline-none py-3 px-4 text-sm leading-tight pr-28" /* Increased pr for buttons */
                      rows={1}
                      style={{ minHeight: `${textareaRef.current?.style.minHeight || 48}px` }}
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1"> {/* Adjusted positioning and gap */}
                      {inputValue && (
                        <button
                          type="button"
                          onClick={() => {
                            setInputValue("");
                            adjustHeight(true);
                            textareaRef.current?.focus();
                          }}
                          className="p-1.5 text-foreground/60 hover:text-foreground transition-colors rounded-full"
                          aria-label="Clear input"
                        >
                          <XIcon size={18} />
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={handleVoiceSearch} // Voice search button
                        className={`p-2 rounded-full transition-colors 
                                      ${isListening ? 'bg-red-500 hover:bg-red-600 text-white' 
                                                     : 'bg-transparent hover:bg-muted text-foreground/70 hover:text-foreground'}`}
                        aria-label={isListening ? "Stop voice search" : "Start voice search"}
                      >
                        <Mic size={20} />
                      </button>
                      <button
                        type="button"
                        onClick={handleSendMessage} // Text send button
                        disabled={!inputValue.trim() || isTyping}
                        className="p-2 bg-[var(--color-primary)] text-white rounded-full hover:bg-[var(--color-primary)]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors" /* Ensured text is white and added disabled cursor */
                        aria-label="Send message"
                      >
                        <SendIcon size={20} />
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
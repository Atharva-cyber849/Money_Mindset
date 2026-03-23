"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MessageSquare, Send, Sparkles, HelpCircle, DollarSign, PiggyBank, TrendingUp, AlertCircle } from 'lucide-react';

const suggestedQuestions = [
  {
    question: "How much should I save for an emergency fund?",
    icon: PiggyBank,
    category: "Savings"
  },
  {
    question: "What's the difference between a 401(k) and IRA?",
    icon: TrendingUp,
    category: "Investing"
  },
  {
    question: "How can I pay off my credit card debt faster?",
    icon: DollarSign,
    category: "Debt"
  },
  {
    question: "What is compound interest and how does it work?",
    icon: HelpCircle,
    category: "Education"
  },
];

interface Message {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export default function AITutorPage() {
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputMessage.trim()) return;

    // Add user message to chat
    const userMessage: Message = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // Get auth token from localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Not authenticated. Please login first.');
        return;
      }

      // Call the AI tutor API on the backend server with auth token
      const response = await fetch('http://localhost:8000/api/v1/ai-tutor/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      const data = await response.json();

      // Add AI response to chat
      const aiMessage: Message = {
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to get AI response';
      setError(errorMsg);
      console.error('AI Tutor error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuestionClick = (question: string) => {
    setInputMessage(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl">
      <div className="mb-8 text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <Sparkles className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-4xl font-bold mb-2">AI Finance Tutor</h1>
        <p className="text-muted-foreground text-lg">
          Get personalized financial guidance powered by AI
        </p>
      </div>

      {/* Chat Area */}
      <Card className="p-6 mb-6 min-h-[500px] flex flex-col">
        {/* Messages Display */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <MessageSquare className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Start a Conversation</h3>
                <p className="text-muted-foreground mb-4">
                  Ask me anything about personal finance, budgeting, investing, or debt management. 
                  I'm here to help you learn!
                </p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-2xl px-4 py-2 rounded-lg ${
                    msg.type === 'user'
                      ? 'bg-cyan-500 text-white rounded-br-none'
                      : 'bg-gray-100 text-gray-900 rounded-bl-none'
                  }`}>
                    {msg.type === 'ai' ? (
                      <div className="text-sm prose prose-sm max-w-none">
                        {/* Render markdown-like content */}
                        {msg.content.split('\n').map((line, i) => {
                          // Headers
                          if (line.startsWith('# ')) return <h1 key={i} className="text-lg font-bold mt-2 mb-1">{line.substring(2)}</h1>;
                          if (line.startsWith('## ')) return <h2 key={i} className="text-base font-bold mt-2 mb-1">{line.substring(3)}</h2>;
                          if (line.startsWith('### ')) return <h3 key={i} className="text-sm font-bold mt-1 mb-1">{line.substring(4)}</h3>;
                          
                          // Bold text
                          if (line.includes('**')) {
                            const parts = line.split(/\*\*(.*?)\*\*/);
                            return (
                              <p key={i} className="text-sm mb-1">
                                {parts.map((part, j) => j % 2 === 1 ? <strong key={j}>{part}</strong> : part)}
                              </p>
                            );
                          }
                          
                          // Italic text
                          if (line.includes('*') && !line.includes('**')) {
                            const parts = line.split(/\*(.*?)\*/);
                            return (
                              <p key={i} className="text-sm mb-1">
                                {parts.map((part, j) => j % 2 === 1 ? <em key={j}>{part}</em> : part)}
                              </p>
                            );
                          }
                          
                          // Skip empty lines (they'll render as spacing)
                          if (!line.trim()) return <div key={i} className="my-1" />;
                          
                          // Regular text
                          return <p key={i} className="text-sm mb-1 whitespace-pre-wrap">{line}</p>;
                        })}
                      </div>
                    ) : (
                      <p className="text-sm">{msg.content}</p>
                    )}
                    <span className="text-xs opacity-70 mt-1 block">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg rounded-bl-none">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="flex gap-2 mt-4">
          <input
            type="text"
            placeholder="Ask about budgeting, investing, debt, or any financial topic..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:bg-gray-50 disabled:text-gray-500"
          />
          <Button 
            onClick={handleSend}
            disabled={isLoading || !inputMessage.trim()}
            className="gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </Button>
        </div>
      </Card>

      {/* Suggested Questions */}
      {messages.length === 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Popular Questions</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {suggestedQuestions.map((item, idx) => {
              const Icon = item.icon;
              return (
                <Card 
                  key={idx} 
                  className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => handleQuestionClick(item.question)}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-cyan-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Icon className="w-5 h-5 text-cyan-600" />
                    </div>
                    <div className="flex-1">
                      <div className="text-xs text-cyan-600 font-semibold mb-1">{item.category}</div>
                      <p className="text-sm font-medium">{item.question}</p>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Info Banner */}
      <div className="mt-8 p-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg text-white">
        <div className="flex items-start gap-4">
          <Sparkles className="w-8 h-8 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-bold mb-2">Powered by GPT-4</h3>
            <p className="text-white/90 text-sm">
              Our AI tutor uses the latest language models combined with proven financial principles 
              to provide accurate, personalized guidance. Always here to help, never judgmental.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

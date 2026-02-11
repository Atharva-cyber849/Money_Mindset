"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MessageSquare, Send, Sparkles, HelpCircle, DollarSign, PiggyBank, TrendingUp } from 'lucide-react';

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

export default function AITutorPage() {
  const [message, setMessage] = useState('');

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
      <Card className="p-6 mb-6 min-h-[400px] flex flex-col">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md">
            <MessageSquare className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Start a Conversation</h3>
            <p className="text-muted-foreground mb-4">
              Ask me anything about personal finance, budgeting, investing, or debt management. 
              I'm here to help you learn!
            </p>
          </div>
        </div>

        {/* Input Area */}
        <div className="flex gap-2 mt-4">
          <input
            type="text"
            placeholder="Ask about budgeting, investing, debt, or any financial topic..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Button className="gap-2">
            <Send className="w-4 h-4" />
            Send
          </Button>
        </div>
      </Card>

      {/* Suggested Questions */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Popular Questions</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {suggestedQuestions.map((item, idx) => {
            const Icon = item.icon;
            return (
              <Card 
                key={idx} 
                className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setMessage(item.question)}
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-blue-600 font-semibold mb-1">{item.category}</div>
                    <p className="text-sm font-medium">{item.question}</p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

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

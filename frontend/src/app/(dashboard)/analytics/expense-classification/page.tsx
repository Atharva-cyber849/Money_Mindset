"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { classifyTransaction } from '@/lib/api/analytics';
import { Loader2, CheckCircle, AlertCircle, TrendingUp, Info, Brain, Zap, Shield } from 'lucide-react';
import { ConfidenceGauge, ComparisonBar, InsightCard, ExplanationCard, HowItWorks, ExampleShowcase } from '@/components/analytics';

export default function ExpenseClassificationPage() {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleClassify = async () => {
    if (!description) {
      setError('Please enter a transaction description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await classifyTransaction(
        description,
        amount ? parseFloat(amount) : undefined
      );
      setResult(data);
    } catch (err) {
      setError('Failed to classify transaction');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Expense Classification</h1>
        <p className="text-muted-foreground">
          AI-powered automatic categorization using supervised learning
        </p>
      </div>

      {/* Educational Infographics */}
      <div className="mb-12 space-y-6">
        {/* Explanation */}
        <ExplanationCard
          icon={Brain}
          title="What is Expense Classification?"
          description="Our AI system automatically categorizes your transactions (e.g., 'Starbucks' → Entertainment) using machine learning trained on millions of transactions. It analyzes descriptions, amounts, and patterns to classify with high accuracy."
          keyPoints={[
            'Uses supervised learning from millions of labeled transactions',
            'Analyzes transaction descriptions and amounts',
            'Provides confidence scores (0-100%) for each classification',
            'Flags low-confidence classifications for manual review',
            'Continuously improves with feedback',
          ]}
          color="green"
          example="'Starbucks Coffee' → Entertainment (95% confidence), 'Shell Gas' → Transportation (98% confidence)"
        />

        {/* How It Works */}
        <HowItWorks
          title="How Expense Classification Works"
          steps={[
            {
              number: 1,
              title: 'Enter Transaction Details',
              description: 'Type in your transaction description (e.g., merchant name) and optionally the amount. More details help improve accuracy.',
              icon: Zap,
            },
            {
              number: 2,
              title: 'AI Analyzes Pattern',
              description: 'Our machine learning model analyzes keywords, amounts, and patterns from millions of similar transactions.',
              icon: Brain,
            },
            {
              number: 3,
              title: 'Generate Prediction',
              description: 'The AI suggests the most likely expense category with a confidence score showing how certain it is.',
              icon: CheckCircle,
            },
            {
              number: 4,
              title: 'Review & Verify',
              description: 'Low confidence predictions are flagged for manual review. You can accept or change the suggested category.',
              icon: Shield,
            },
          ]}
          color="green"
        />

        {/* Example */}
        <ExampleShowcase
          title="Classification Example"
          description="See how AI predicts transaction categories"
          inputExample={[
            { label: 'Description', value: 'Whole Foods Market', highlight: true },
            { label: 'Amount', value: '$45.50' },
            { label: 'Text Analysis', value: 'Keywords: food, market' },
          ]}
          outputExample={[
            { label: 'Primary Category', value: 'Groceries', highlight: true },
            { label: 'Confidence Score', value: '92%' },
            { label: 'Alternative', value: 'Dining (5%)' },
            { label: 'Review Status', value: 'Auto-approved' },
          ]}
          color="green"
        />
      </div>

      <div className="grid gap-6">
        {/* Input Card */}
        <Card className="p-6">
          <h3 className="text-lg font-bold mb-2">Classify Transaction</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Enter a transaction description to automatically categorize it
          </p>
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="description" className="text-sm font-medium">Transaction Description</label>
              <Input
                id="description"
                placeholder="e.g., Starbucks Coffee, Amazon.com, Shell Gas Station"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleClassify()}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="amount" className="text-sm font-medium">Amount (Optional)</label>
              <Input
                id="amount"
                type="number"
                placeholder="50.00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 text-red-600 text-sm">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}

            <Button onClick={handleClassify} disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Classifying...
                </>
              ) : (
                'Classify Transaction'
              )}
            </Button>
          </div>
        </Card>

        {/* Results Card */}
        {result && (
          <div className="space-y-6">
            {/* Confidence Gauge */}
            <ConfidenceGauge
              confidence={Math.round(result.confidence * 100)}
              showWarning={result.needs_review}
            />

            {/* Primary Category with Icon */}
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Primary Category</h3>
                  <p className="text-2xl font-bold capitalize text-teal-600">
                    {result.category.replace('_', ' ')}
                  </p>
                </div>
                <CheckCircle className="w-12 h-12 text-green-600" />
              </div>
            </Card>

            {/* Alternative Suggestions */}
            {result.alternatives && result.alternatives.length > 0 && (
              <ComparisonBar
                title="Alternative Categories"
                items={[
                  {
                    label: 'Classification Alternatives',
                    values: result.alternatives.map((alt: any, idx: number) => ({
                      label: alt.category.replace('_', ' '),
                      value: Math.round(alt.confidence * 100),
                      color: idx === 0 ? '#0891B2' : idx === 1 ? '#06B6D4' : '#93C5FD',
                    })),
                  },
                ]}
                maxValue={100}
              />
            )}

            {/* Review Insight */}
            {result.needs_review && (
              <InsightCard
                icon={AlertCircle}
                title="Review Recommended"
                description="Confidence is below 70%. Please verify the suggested category manually."
                color="yellow"
              />
            )}
          </div>
        )}

        {/* Info Card */}
        <Card className="p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            How It Works
          </h3>
          <div className="space-y-3 text-sm text-muted-foreground">
            <p>
              Our expense classification system uses <strong>supervised learning</strong> to
              automatically categorize your transactions based on their descriptions.
            </p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Analyzes keywords and patterns in transaction descriptions</li>
              <li>Considers transaction amounts for better accuracy</li>
              <li>Learns from millions of labeled transactions</li>
              <li>Provides confidence scores and alternative suggestions</li>
            </ul>
            <p>
              Categories with confidence below 70% are flagged for review to ensure accuracy.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}

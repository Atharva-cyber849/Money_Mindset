"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { classifyTransaction } from '@/lib/api/analytics';
import { Loader2, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

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
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Classification Result
            </h3>
            <div className="space-y-4">
              {/* Primary Category */}
              <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Primary Category</div>
                  <div className="text-2xl font-bold capitalize">
                    {result.category.replace('_', ' ')}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-muted-foreground mb-1">Confidence</div>
                  <div className="flex items-center gap-2">
                    <div
                      className={`h-2 w-20 rounded-full ${getConfidenceColor(result.confidence)}`}
                    />
                    <span className="text-xl font-semibold">
                      {(result.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Review Status */}
              {result.needs_review && (
                <div className="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                  <div className="text-sm">
                    <div className="font-semibold text-yellow-900">Review Recommended</div>
                    <div className="text-yellow-700">
                      Confidence is below 70%. Please verify the suggested category.
                    </div>
                  </div>
                </div>
              )}

              {/* Alternative Suggestions */}
              {result.alternatives && result.alternatives.length > 0 && (
                <div>
                  <div className="text-sm font-medium mb-2">Alternative Suggestions</div>
                  <div className="space-y-2">
                    {result.alternatives.map((alt: any, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted transition-colors"
                      >
                        <span className="capitalize">
                          {alt.category.replace('_', ' ')}
                        </span>
                        <Badge variant="neutral">
                          {(alt.confidence * 100).toFixed(0)}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
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

"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { ExpenseClassificationDashboard } from '@/components/analytics';
import { classifyTransaction, createTransaction } from '@/lib/api/analytics';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

export default function ExpenseClassificationPage() {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [saveError, setSaveError] = useState('');
  const [saveSuccess, setSaveSuccess] = useState('');
  const [savingTransaction, setSavingTransaction] = useState(false);
  const [showClassifier, setShowClassifier] = useState(false);
  const [dashboardRefreshKey, setDashboardRefreshKey] = useState(0);
  const classifierSectionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (showClassifier) {
      classifierSectionRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }
  }, [showClassifier]);

  const openClassifier = () => {
    setShowClassifier(true);
  };

  const handleClassify = async () => {
    if (!description) {
      setError('Please enter a transaction description');
      return;
    }

    setLoading(true);
    setError('');
    setSaveError('');
    setSaveSuccess('');

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

  const handleSaveToHistory = async () => {
    const parsedAmount = Number(amount);

    if (!result?.category) {
      setSaveError('Classify the expense first, then save it.');
      return;
    }

    if (!parsedAmount || Number.isNaN(parsedAmount) || parsedAmount <= 0) {
      setSaveError('Enter a valid amount to save this expense.');
      return;
    }

    setSavingTransaction(true);
    setSaveError('');
    setSaveSuccess('');

    try {
      await createTransaction({
        date: new Date().toISOString(),
        description: description.trim(),
        category: result.category,
        amount: parsedAmount,
        transaction_type: 'debit',
      });

      setSaveSuccess('Expense saved to history. Analytics will refresh now.');
      setDashboardRefreshKey((prev) => prev + 1);
    } catch (err) {
      console.error(err);
      setSaveError('Failed to save expense to history.');
    } finally {
      setSavingTransaction(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.7) return 'Moderate Confidence';
    return 'Low Confidence';
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl space-y-8">
      <Card className="p-5 border-cyan-200 bg-cyan-50/40">
        <h2 className="text-lg font-bold">Where to add expenses on this page</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Click <span className="font-semibold text-slate-900">Add/Classify Expense</span> to open the input form, then enter description + amount.
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Note: Top analytics cards show expenses already stored in your transaction history for the last 30 days.
        </p>
        <div className="mt-3">
          <Button size="sm" onClick={openClassifier}>
            Open Expense Input
          </Button>
        </div>
      </Card>

      {/* Dashboard */}
      <ExpenseClassificationDashboard
        key={dashboardRefreshKey}
        days={30}
        onViewFullHistory={() => {
          openClassifier();
        }}
        onAnalyzeMore={() => {
          openClassifier();
        }}
      />

      {/* Individual Transaction Classifier */}
      {showClassifier && (
        <div ref={classifierSectionRef} className="space-y-6 border-t pt-8">
          <div>
            <h2 className="text-2xl font-bold mb-2">Expense Classification</h2>
            <p className="text-muted-foreground">
              Main focus: classify one transaction at a time and review only when confidence is low.
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

                {result && (
                  <Button
                    variant="outline"
                    onClick={handleSaveToHistory}
                    disabled={savingTransaction}
                    className="w-full"
                  >
                    {savingTransaction ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      'Save Expense to History'
                    )}
                  </Button>
                )}

                {saveError && (
                  <div className="flex items-center gap-2 text-red-600 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    {saveError}
                  </div>
                )}

                {saveSuccess && (
                  <div className="flex items-center gap-2 text-green-700 text-sm">
                    <CheckCircle className="w-4 h-4" />
                    {saveSuccess}
                  </div>
                )}
              </div>
            </Card>

            {/* Results Card */}
            {result && (
              <div className="space-y-6">
                {/* Classification Summary */}
                <Card className="p-6 border-cyan-200 bg-gradient-to-br from-cyan-50 to-transparent">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-1">Classification Outcome</h3>
                      <p className="text-lg font-bold text-slate-900">
                        {getConfidenceLabel(result.confidence)}
                      </p>
                    </div>
                    <Badge className="capitalize">
                      {result.needs_review ? 'Manual Review Needed' : 'Auto-Classified'}
                    </Badge>
                  </div>
                </Card>

                {/* Primary Category with Icon */}
                <Card className="p-6 bg-gradient-to-br from-green-50 to-transparent border-green-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-1">Primary Category</h3>
                      <p className="text-2xl font-bold capitalize text-green-600">
                        {result.category.replace('_', ' ')}
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                          <div
                            className={`h-full rounded-full transition-all ${getConfidenceColor(result.confidence)}`}
                            style={{ width: `${result.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold">
                          {Math.round(result.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    <CheckCircle className="w-12 h-12 text-green-600" />
                  </div>
                </Card>

                {/* Alternative Suggestions */}
                {result.alternatives && result.alternatives.length > 0 && (
                  <Card className="p-6">
                    <h3 className="text-lg font-bold mb-2">Alternative Categories</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Use these only if the primary category does not match the merchant or receipt context.
                    </p>
                    <div className="space-y-3">
                      {result.alternatives.map((alt: any, idx: number) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm font-medium capitalize">
                            {alt.category.replace('_', ' ')}
                          </span>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-1.5 w-20">
                              <div
                                className="h-full bg-blue-500 rounded-full transition-all"
                                style={{ width: `${alt.confidence * 100}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold text-gray-600">
                              {Math.round(alt.confidence * 100)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {/* Review Insight */}
                {result.needs_review && (
                  <Card className="p-6 bg-yellow-50 border-yellow-200">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h3 className="font-semibold text-yellow-900">Review Recommended</h3>
                        <p className="text-sm text-yellow-800 mt-1">
                          Confidence is below 70%. Please verify the suggested category manually.
                        </p>
                        <div className="mt-3 rounded-md border border-yellow-300 bg-yellow-100/60 p-3 text-sm text-yellow-900">
                          <p className="font-semibold">Where to review:</p>
                          <p>Check the transaction in your expense history, compare receipt/merchant details, then select the best-fit category from Primary or Alternatives.</p>
                        </div>
                      </div>
                    </div>
                  </Card>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

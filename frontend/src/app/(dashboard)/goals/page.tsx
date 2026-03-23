"use client";

import React, { useEffect, useMemo, useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { goalsAPI } from '@/lib/api/client';
import { Target, Plus, TrendingUp, AlertCircle, Calendar, Trash2 } from 'lucide-react';

interface GoalItem {
  id: number;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline?: string | null;
  priority: number;
  status: string;
}

export default function GoalsPage() {
  const [goals, setGoals] = useState<GoalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [newGoal, setNewGoal] = useState({
    name: '',
    target_amount: 100000,
    current_amount: 0,
    deadline: '',
    priority: 1,
  });

  const loadGoals = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await goalsAPI.getAll();
      setGoals(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGoals();
  }, []);

  const summary = useMemo(() => {
    const totalTarget = goals.reduce((sum, g) => sum + (g.target_amount || 0), 0);
    const totalCurrent = goals.reduce((sum, g) => sum + (g.current_amount || 0), 0);
    const completed = goals.filter((g) => (g.current_amount || 0) >= (g.target_amount || 0)).length;
    const avgProgress = totalTarget > 0 ? (totalCurrent / totalTarget) * 100 : 0;
    return { totalTarget, totalCurrent, completed, avgProgress };
  }, [goals]);

  const createGoal = async () => {
    if (!newGoal.name.trim()) return;

    try {
      setSaving(true);
      setError('');
      await goalsAPI.create({
        ...newGoal,
        deadline: newGoal.deadline ? new Date(newGoal.deadline).toISOString() : null,
      });
      setShowCreate(false);
      setNewGoal({ name: '', target_amount: 100000, current_amount: 0, deadline: '', priority: 1 });
      await loadGoals();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create goal');
    } finally {
      setSaving(false);
    }
  };

  const updateProgress = async (goal: GoalItem, amount: number) => {
    try {
      await goalsAPI.update(goal.id, {
        current_amount: Math.max(0, amount),
        status: amount >= goal.target_amount ? 'completed' : goal.status,
      });
      await loadGoals();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update goal');
    }
  };

  const deleteGoal = async (goalId: number) => {
    try {
      await goalsAPI.delete(goalId);
      await loadGoals();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete goal');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-6xl">
        <Card className="p-12 text-center">Loading goals...</Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Financial Goals</h1>
          <p className="text-muted-foreground text-lg">
            Track and achieve your money milestones
          </p>
        </div>
        <Button className="gap-2" onClick={() => setShowCreate((v) => !v)}>
          <Plus className="w-5 h-5" />
          {showCreate ? 'Cancel' : 'New Goal'}
        </Button>
      </div>

      {error && (
        <Card className="p-4 mb-6 bg-red-50 border border-red-200 text-red-700">{error}</Card>
      )}

      {showCreate && (
        <Card className="p-6 mb-6 space-y-4">
          <h2 className="text-xl font-bold">Create Goal</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <input
              value={newGoal.name}
              onChange={(e) => setNewGoal((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="Goal name"
              className="w-full rounded border px-3 py-2"
            />
            <input
              type="number"
              value={newGoal.target_amount}
              onChange={(e) => setNewGoal((prev) => ({ ...prev, target_amount: Number(e.target.value) || 0 }))}
              placeholder="Target amount"
              className="w-full rounded border px-3 py-2"
            />
            <input
              type="number"
              value={newGoal.current_amount}
              onChange={(e) => setNewGoal((prev) => ({ ...prev, current_amount: Number(e.target.value) || 0 }))}
              placeholder="Current amount"
              className="w-full rounded border px-3 py-2"
            />
            <input
              type="date"
              value={newGoal.deadline}
              onChange={(e) => setNewGoal((prev) => ({ ...prev, deadline: e.target.value }))}
              className="w-full rounded border px-3 py-2"
            />
          </div>
          <Button onClick={createGoal} disabled={saving} className="gap-2">
            <Plus className="w-4 h-4" />
            {saving ? 'Creating...' : 'Create Goal'}
          </Button>
        </Card>
      )}

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Card className="p-5">
          <p className="text-sm text-muted-foreground">Total Saved</p>
          <p className="text-2xl font-bold">₹{Math.round(summary.totalCurrent).toLocaleString('en-IN')}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-muted-foreground">Target Corpus</p>
          <p className="text-2xl font-bold">₹{Math.round(summary.totalTarget).toLocaleString('en-IN')}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-muted-foreground">Completed Goals</p>
          <p className="text-2xl font-bold">{summary.completed}/{goals.length}</p>
        </Card>
      </div>

      {goals.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Target className="w-10 h-10 text-cyan-600" />
            </div>
            <h2 className="text-2xl font-bold mb-3">Set Your First Goal</h2>
            <p className="text-muted-foreground mb-6">
              Add a goal to start tracking progress with live updates and completion milestones.
            </p>
            <Button size="lg" className="gap-2" onClick={() => setShowCreate(true)}>
              <Plus className="w-5 h-5" />
              Create Your First Goal
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {goals.map((goal) => {
            const percent = goal.target_amount > 0
              ? Math.min(100, (goal.current_amount / goal.target_amount) * 100)
              : 0;

            return (
              <Card key={goal.id} className="p-6 space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-bold">{goal.name}</h3>
                    <p className="text-sm text-muted-foreground">Priority {goal.priority}</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => deleteGoal(goal.id)}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>₹{Math.round(goal.current_amount).toLocaleString('en-IN')}</span>
                    <span>₹{Math.round(goal.target_amount).toLocaleString('en-IN')}</span>
                  </div>
                  <div className="h-2 rounded bg-gray-200 overflow-hidden">
                    <div className="h-full bg-cyan-600" style={{ width: `${percent}%` }} />
                  </div>
                  <p className="text-xs text-muted-foreground">{percent.toFixed(1)}% completed</p>
                </div>

                <div className="flex gap-2">
                  <input
                    type="number"
                    defaultValue={goal.current_amount}
                    onBlur={(e) => updateProgress(goal, Number(e.target.value) || 0)}
                    className="flex-1 rounded border px-3 py-2 text-sm"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => updateProgress(goal, goal.current_amount + Math.max(1000, goal.target_amount * 0.05))}
                  >
                    +Top Up
                  </Button>
                </div>

                {goal.deadline && (
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Deadline: {new Date(goal.deadline).toLocaleDateString()}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* Info Cards */}
      <div className="grid md:grid-cols-2 gap-6 mt-8">
        <Card className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">SMART Goals</h3>
              <p className="text-sm text-muted-foreground">
                Create Specific, Measurable, Achievable, Relevant, and Time-bound financial goals 
                that you can actually accomplish.
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-cyan-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-6 h-6 text-cyan-600" />
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">Track Progress</h3>
              <p className="text-sm text-muted-foreground">
                Monitor your progress with visual trackers, milestone celebrations, and
                personalized recommendations to keep you on track.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

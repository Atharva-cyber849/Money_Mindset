"use client";

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Target, Plus, TrendingUp, AlertCircle } from 'lucide-react';

export default function GoalsPage() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Financial Goals</h1>
          <p className="text-muted-foreground text-lg">
            Track and achieve your money milestones
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="w-5 h-5" />
          New Goal
        </Button>
      </div>

      {/* Empty State */}
      <Card className="p-12 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Target className="w-10 h-10 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold mb-3">Set Your First Goal</h2>
          <p className="text-muted-foreground mb-6">
            Whether it's building an emergency fund, saving for a vacation, or paying off debt, 
            we'll help you create a plan and track your progress.
          </p>
          <Button size="lg" className="gap-2">
            <Plus className="w-5 h-5" />
            Create Your First Goal
          </Button>
        </div>
      </Card>

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
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-6 h-6 text-blue-600" />
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

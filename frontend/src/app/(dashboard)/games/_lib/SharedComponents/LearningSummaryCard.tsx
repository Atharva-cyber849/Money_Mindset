'use client';

import { ArrowRight, Lightbulb } from 'lucide-react';
import { Card } from '@/components/ui/Card';

interface LearningSummaryCardProps {
  title: string;
  summary: string;
  takeaways: string[];
  nextStep: string;
}

export function LearningSummaryCard({ title, summary, takeaways, nextStep }: LearningSummaryCardProps) {
  return (
    <Card className="p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-cyan-950 text-white border-slate-700 shadow-2xl ring-1 ring-cyan-500/20">
      <div className="flex items-start gap-3 mb-4">
        <div className="rounded-full bg-cyan-400/15 p-2 border border-cyan-300/20">
          <Lightbulb className="w-5 h-5 text-cyan-300" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-cyan-100">{title}</h3>
          <p className="text-sm text-slate-300 mt-1">{summary}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {takeaways.map((takeaway) => (
          <div key={takeaway} className="rounded-xl border border-cyan-300/15 bg-slate-900/80 p-4">
            <p className="text-sm text-slate-100 leading-6">{takeaway}</p>
          </div>
        ))}
      </div>

      <div className="mt-5 rounded-xl border border-cyan-300/20 bg-cyan-400/10 p-4">
        <div className="flex items-start gap-3">
          <ArrowRight className="w-4 h-4 text-cyan-300 flex-shrink-0 mt-1" />
          <p className="text-sm text-cyan-50 leading-6">{nextStep}</p>
        </div>
      </div>
    </Card>
  );
}
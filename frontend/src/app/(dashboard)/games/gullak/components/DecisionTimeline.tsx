'use client';

import { motion } from 'framer-motion';
import { TimelineEvent } from '@/app/(dashboard)/games/_lib/SharedComponents';
import { ChartWrapper } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface AllocationRecord {
  month: number;
  emergency: number;
  insurance: number;
  short_term: number;
  long_term: number;
  gold: number;
  totalAllocated: number;
  totalAssets: number;
}

interface DecisionTimelineProps {
  allocationHistory: AllocationRecord[];
  currentMonth: number;
}

export function DecisionTimeline({ allocationHistory, currentMonth }: DecisionTimelineProps) {
  // Get last 10 decisions for timeline view
  const recentDecisions = allocationHistory.slice(-10);

  if (!recentDecisions || recentDecisions.length === 0) {
    return (
      <ChartWrapper
        title="Decision Timeline"
        description="Your allocation history"
        height="h-96"
      >
        <div className="flex items-center justify-center h-full text-gray-500">
          <p>Start making allocation decisions to track your journey</p>
        </div>
      </ChartWrapper>
    );
  }

  const getTotalAllocated = (record: AllocationRecord) => {
    return (
      record.emergency +
      record.insurance +
      record.short_term +
      record.long_term +
      record.gold
    );
  };

  const getTopJar = (record: AllocationRecord) => {
    const jars = {
      emergency: record.emergency,
      insurance: record.insurance,
      short_term: record.short_term,
      long_term: record.long_term,
      gold: record.gold,
    };
    const top = Object.entries(jars).reduce((a, b) => (b[1] > a[1] ? b : a));
    return top[0];
  };

  const jarEmojis: Record<string, string> = {
    emergency: '🚨',
    insurance: '🛡️',
    short_term: '🎯',
    long_term: '🏢',
    gold: '👑',
  };

  const jarLabels: Record<string, string> = {
    emergency: 'Emergency Fund',
    insurance: 'Insurance',
    short_term: 'Short-term Goals',
    long_term: 'Long-term Wealth',
    gold: 'Gold & Hedge',
  };

  return (
    <ChartWrapper
      title="Decision Timeline"
      description={`${recentDecisions.length} recent allocations shown`}
      height="h-auto"
      className="overflow-visible"
    >
      <motion.div
        className="space-y-2 max-h-96 overflow-y-auto pr-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.05, delayChildren: 0.1 }}
      >
        {recentDecisions.map((record, idx) => {
          const topJar = getTopJar(record);
          const totalAllocated = getTotalAllocated(record);
          const year = Math.floor(record.month / 12);
          const monthOfYear = (record.month % 12) || 12;
          const monthNames = [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec',
          ];

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
            >
              <TimelineEvent
                icon={jarEmojis[topJar]}
                title={`Allocated ₹${totalAllocated.toLocaleString()}`}
                description={`Prioritized: ${jarLabels[topJar]}`}
                timestamp={`Month ${record.month} • ${monthNames[monthOfYear - 1]} Year ${year}`}
                variant="default"
                details={[
                  {
                    label: 'Top Allocation',
                    value: `₹${record[topJar as keyof AllocationRecord] || 0} to ${jarLabels[topJar]}`,
                  },
                  {
                    label: 'Total Assets',
                    value: `₹${record.totalAssets.toLocaleString()}`,
                  },
                ]}
                metadata={topJar.toUpperCase()}
              />
            </motion.div>
          );
        })}
      </motion.div>

      {/* Stats Summary at Bottom */}
      <motion.div
        className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-3 gap-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div>
          <p className="text-xs text-gray-600">Total Allocations</p>
          <p className="mt-1 text-lg font-bold text-gray-900">{recentDecisions.length}</p>
        </div>

        <div>
          <p className="text-xs text-gray-600">Avg Monthly Allocated</p>
          <p className="mt-1 text-lg font-bold text-blue-600">
            ₹
            {Math.round(
              recentDecisions.reduce((sum, r) => sum + getTotalAllocated(r), 0) / recentDecisions.length
            ).toLocaleString()}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-600">Latest Total Assets</p>
          <p className="mt-1 text-lg font-bold text-green-600">
            ₹{recentDecisions[recentDecisions.length - 1].totalAssets.toLocaleString()}
          </p>
        </div>
      </motion.div>

      {/* Learning Tip */}
      <motion.div
        className="mt-4 rounded-lg bg-amber-50 border border-amber-200 p-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
      >
        <p className="text-xs font-semibold text-amber-900">💡 Pro Tip</p>
        <p className="mt-1 text-xs text-amber-800">
          Your allocation decisions compound over time. Consistent monthly allocations across all 5 jars create a diversified safety net
          for both present and future.
        </p>
      </motion.div>
    </ChartWrapper>
  );
}

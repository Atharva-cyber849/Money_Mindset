'use client';

import { motion } from 'framer-motion';
import { InfoCard, MetricGauge } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface ConsequencePanelProps {
  emergencyFund: number;
  monthlyExpenses: number;
  insurance: number;
  totalJars: number;
}

export function ConsequencePanel({
  emergencyFund,
  monthlyExpenses,
  insurance,
  totalJars,
}: ConsequencePanelProps) {
  const monthsCovered = monthlyExpenses > 0 ? emergencyFund / monthlyExpenses : 0;
  const recommended = 6; // 6 months recommended
  const isAdequate = monthsCovered >= recommended;
  const insuranceAdequacy = insurance > 0 ? Math.min((insurance / (monthlyExpenses * 12 * 0.3)) * 100, 100) : 0;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <h3 className="mb-6 text-lg font-semibold text-gray-900">🛡️ Financial Safety Check</h3>

      {/* Gauges Row */}
      <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8" variants={containerVariants}>
        <motion.div variants={itemVariants} className="flex flex-col items-center">
          <MetricGauge
            value={monthsCovered}
            max={12}
            title="Emergency Fund"
            unit="Months"
            color="blue"
            size="md"
            description={`${monthsCovered.toFixed(1)} months of expenses covered`}
            thresholds={{ good: 6, warning: 3 }}
          />
        </motion.div>

        <motion.div variants={itemVariants} className="flex flex-col items-center">
          <MetricGauge
            value={insuranceAdequacy}
            max={100}
            title="Insurance Coverage"
            unit="%"
            color="green"
            size="md"
            description={`${insuranceAdequacy.toFixed(0)}% of recommended`}
            thresholds={{ good: 80, warning: 50 }}
          />
        </motion.div>
      </motion.div>

      {/* Information Cards */}
      <motion.div className="space-y-4" variants={containerVariants}>
        {/* Emergency Fund Status */}
        <motion.div variants={itemVariants}>
          <InfoCard
            icon={isAdequate ? '✅' : '⚠️'}
            title="Emergency Fund Status"
            description={
              isAdequate
                ? `Excellent! You have ${monthsCovered.toFixed(1)} months of expenses covered. Financial buffer is secure.`
                : `Needs attention: Only ${monthsCovered.toFixed(1)} months covered. Aim for 6 months (₹${(monthlyExpenses * 6).toLocaleString()}).`
            }
            variant={isAdequate ? 'success' : 'warning'}
          />
        </motion.div>

        {/* Insurance Coverage */}
        <motion.div variants={itemVariants}>
          <InfoCard
            icon={insuranceAdequacy > 50 ? '✓' : '⚠️'}
            title="Insurance Coverage"
            description={
              insuranceAdequacy > 50
                ? `Good health & life insurance. Current allocation: ₹${insurance.toLocaleString()}`
                : `Insufficient insurance. Consider increasing to protect your family during emergencies.`
            }
            variant={insuranceAdequacy > 50 ? 'success' : 'warning'}
          />
        </motion.div>

        {/* Life Event Impact Warning */}
        <motion.div variants={itemVariants}>
          <InfoCard
            icon="🎯"
            title="Life Event Resilience"
            description={
              monthsCovered >= 6
                ? 'Your emergency fund will likely handle most life events. You are financially resilient!'
                : 'Your financial buffer is tight. A job loss or major expense could be challenging. Build your emergency fund.'
            }
            variant="info"
          />
        </motion.div>

        {/* Consequences of Low Safety */}
        {monthsCovered < 3 && (
          <motion.div variants={itemVariants}>
            <div className="rounded-lg bg-red-50 border-2 border-red-200 p-4">
              <p className="font-semibold text-red-900">🚨 High Risk Zone</p>
              <p className="mt-2 text-sm text-red-800">
                With less than 3 months of emergency funds:
              </p>
              <ul className="mt-2 ml-4 text-sm text-red-800 space-y-1">
                <li>• Job loss could force selling investments at loss</li>
                <li>• Medical emergencies may require high-interest debt</li>
                <li>• Limited ability to handle life events without stress</li>
              </ul>
            </div>
          </motion.div>
        )}

        {/* Portfolio Overview */}
        <motion.div variants={itemVariants}>
          <div className="rounded-lg bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200 p-4">
            <p className="font-semibold text-cyan-900">💰 Your Financial Picture</p>
            <div className="mt-3 grid grid-cols-3 gap-3 text-sm">
              <div>
                <p className="text-cyan-700">Emergency</p>
                <p className="font-bold text-cyan-900">₹{emergencyFund.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-cyan-700">Insurance</p>
                <p className="font-bold text-cyan-900">₹{insurance.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-cyan-700">Total Assets</p>
                <p className="font-bold text-cyan-900">₹{totalJars.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Learning Box */}
      <motion.div
        variants={itemVariants}
        className="mt-6 rounded-lg bg-purple-50 border border-purple-200 p-4"
      >
        <p className="font-semibold text-purple-900">💡 Financial Wisdom</p>
        <p className="mt-2 text-sm text-purple-800">
          "Before you invest for the future, secure your present. An adequate emergency fund prevents you from disrupting investments during
          crises — the #1 mistake that derails long-term wealth building."
        </p>
      </motion.div>
    </motion.div>
  );
}

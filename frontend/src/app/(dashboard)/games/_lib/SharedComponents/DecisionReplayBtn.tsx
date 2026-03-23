'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

interface DecisionOutcome {
  scenario: string;
  choice: string;
  impact: string;
  metrics?: { label: string; value: string }[];
}

interface DecisionReplayBtnProps {
  decision: {
    title: string;
    description: string;
    actualOutcome: DecisionOutcome;
    alternativeOutcome?: DecisionOutcome;
    timestamp?: string;
  };
  onReplay?: () => void;
  className?: string;
}

export function DecisionReplayBtn({ decision, onReplay, className = '' }: DecisionReplayBtnProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showAlternative, setShowAlternative] = useState(false);

  const handleReplay = () => {
    onReplay?.();
    setIsOpen(false);
  };

  const currentOutcome = showAlternative ? decision.alternativeOutcome : decision.actualOutcome;

  return (
    <>
      {/* Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(true)}
        className={`inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 px-4 py-2 font-semibold text-white shadow-lg transition-all hover:shadow-xl ${className}`}
      >
        <span>🔄</span>
        <span>Replay Decision</span>
      </motion.button>

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-40 bg-black/50"
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -20 }}
              className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white shadow-2xl"
            >
              {/* Header */}
              <div className="border-b border-gray-200 px-6 py-4">
                <h3 className="text-lg font-semibold text-gray-900">{decision.title}</h3>
                <p className="mt-1 text-sm text-gray-600">{decision.description}</p>
                {decision.timestamp && <p className="mt-2 text-xs text-gray-500">{decision.timestamp}</p>}
              </div>

              {/* Content */}
              <div className="max-h-96 space-y-4 overflow-y-auto p-6">
                {/* Toggle between actual and alternative */}
                {decision.alternativeOutcome && (
                  <div className="flex gap-2 rounded-lg bg-gray-100 p-1">
                    <button
                      onClick={() => setShowAlternative(false)}
                      className={`flex-1 rounded-md px-3 py-2 text-sm font-semibold transition-all ${
                        !showAlternative
                          ? 'bg-white text-gray-900 shadow'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      What Happened
                    </button>
                    <button
                      onClick={() => setShowAlternative(true)}
                      className={`flex-1 rounded-md px-3 py-2 text-sm font-semibold transition-all ${
                        showAlternative ? 'bg-white text-gray-900 shadow' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Alternate Path
                    </button>
                  </div>
                )}

                {/* Outcome Display */}
                <motion.div
                  key={showAlternative ? 'alt' : 'actual'}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="rounded-lg bg-gray-50 p-4"
                >
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-gray-600">Scenario</p>
                      <p className="mt-1 text-sm text-gray-900">{currentOutcome?.scenario}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-gray-600">Choice</p>
                      <p className="mt-1 font-semibold text-cyan-700">{currentOutcome?.choice}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-gray-600">Impact</p>
                      <p className="mt-1 text-sm text-gray-900">{currentOutcome?.impact}</p>
                    </div>

                    {/* Metrics if provided */}
                    {currentOutcome?.metrics && currentOutcome.metrics.length > 0 && (
                      <div className="border-t border-gray-200 pt-3">
                        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-600">
                          Metrics
                        </p>
                        <div className="grid grid-cols-2 gap-2">
                          {currentOutcome.metrics.map((metric, idx) => (
                            <div key={idx} className="rounded bg-white p-2">
                              <p className="text-xs text-gray-600">{metric.label}</p>
                              <p className="mt-0.5 font-semibold text-gray-900">{metric.value}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>

              {/* Footer */}
              <div className="border-t border-gray-200 flex gap-3 bg-gray-50 px-6 py-4">
                <button
                  onClick={() => setIsOpen(false)}
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 transition-colors hover:bg-gray-100"
                >
                  Close
                </button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleReplay}
                  className="flex-1 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 px-4 py-2 font-semibold text-white transition-all hover:shadow-lg"
                >
                  Replay with Data
                </motion.button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

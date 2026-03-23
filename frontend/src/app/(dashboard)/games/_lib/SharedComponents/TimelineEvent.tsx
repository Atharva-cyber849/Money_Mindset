'use client';

import { motion } from 'framer-motion';

interface TimelineEventProps {
  icon: string;
  title: string;
  description?: string;
  timestamp?: string;
  details?: Array<{ label: string; value: string | number }>;
  variant?: 'default' | 'success' | 'warning' | 'critical';
  metadata?: string;
  className?: string;
}

export function TimelineEvent({
  icon,
  title,
  description,
  timestamp,
  details,
  variant = 'default',
  metadata,
  className = '',
}: TimelineEventProps) {
  const variantStyles = {
    default: 'bg-blue-100 text-blue-600',
    success: 'bg-green-100 text-green-600',
    warning: 'bg-amber-100 text-amber-600',
    critical: 'bg-red-100 text-red-600',
  };

  const dotVariantStyles = {
    default: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-amber-500',
    critical: 'bg-red-500',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4 }}
      className={`relative pb-8 ${className}`}
    >
      {/* Timeline line connector */}
      <div className="absolute left-4 top-12 h-8 w-0.5 bg-gray-200" />

      {/* Icon dot */}
      <div className="flex items-start gap-4">
        <motion.div
          whileHover={{ scale: 1.2 }}
          className={`mt-2 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-lg ${variantStyles[variant]} ring-4 ring-white`}
        >
          {icon}
        </motion.div>

        {/* Content */}
        <div className="flex-1 pt-1">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="font-semibold text-gray-900">{title}</h4>
              {description && <p className="mt-0.5 text-sm text-gray-600">{description}</p>}
            </div>
            {metadata && <span className="flex-shrink-0 text-xs font-medium text-gray-500">{metadata}</span>}
          </div>

          {timestamp && <p className="mt-1 text-xs text-gray-500">{timestamp}</p>}

          {details && details.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-3">
              {details.map((detail, idx) => (
                <div key={idx} className="text-sm">
                  <span className="text-gray-600">{detail.label}:</span>
                  <span className="ml-1 font-semibold text-gray-900">{detail.value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface ChartWrapperProps {
  title: string;
  description?: string;
  children: ReactNode;
  loading?: boolean;
  error?: string;
  height?: string;
  className?: string;
}

export function ChartWrapper({
  title,
  description,
  children,
  loading = false,
  error,
  height = 'h-80',
  className = '',
}: ChartWrapperProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`rounded-lg border border-gray-200 bg-white p-6 shadow-sm ${className}`}
    >
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {description && <p className="mt-1 text-sm text-gray-600">{description}</p>}
      </div>

      {/* Content */}
      {loading ? (
        <div className={`${height} flex items-center justify-center`}>
          <div className="flex flex-col items-center gap-3">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-cyan-500" />
            <p className="text-sm text-gray-500">Loading data...</p>
          </div>
        </div>
      ) : error ? (
        <div className={`${height} flex items-center justify-center`}>
          <div className="text-center">
            <p className="text-sm font-semibold text-red-600">Error loading chart</p>
            <p className="mt-1 text-xs text-gray-500">{error}</p>
          </div>
        </div>
      ) : (
        <div className={height}>{children}</div>
      )}
    </motion.div>
  );
}

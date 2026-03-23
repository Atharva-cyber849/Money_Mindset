'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface InfoCardProps {
  icon?: string;
  title: string;
  description: string;
  variant?: 'default' | 'success' | 'warning' | 'info';
  children?: ReactNode;
  className?: string;
}

export function InfoCard({
  icon,
  title,
  description,
  variant = 'default',
  children,
  className = '',
}: InfoCardProps) {
  const variantStyles = {
    default: 'bg-blue-50 border-blue-200 text-blue-900',
    success: 'bg-green-50 border-green-200 text-green-900',
    warning: 'bg-amber-50 border-amber-200 text-amber-900',
    info: 'bg-cyan-50 border-cyan-200 text-cyan-900',
  };

  const iconBgStyles = {
    default: 'bg-blue-100',
    success: 'bg-green-100',
    warning: 'bg-amber-100',
    info: 'bg-cyan-100',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4 }}
      className={`rounded-lg border-2 p-4 ${variantStyles[variant]} ${className}`}
    >
      <div className="flex gap-3">
        {icon && (
          <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg text-lg ${iconBgStyles[variant]}`}>
            {icon}
          </div>
        )}
        <div className="flex-1">
          <h4 className="font-semibold">{title}</h4>
          <p className="mt-1 text-sm opacity-90">{description}</p>
          {children && <div className="mt-3">{children}</div>}
        </div>
      </div>
    </motion.div>
  );
}

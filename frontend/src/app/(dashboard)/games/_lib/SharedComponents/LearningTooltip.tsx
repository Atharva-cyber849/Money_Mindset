'use client';

import { ReactNode, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface LearningTooltipProps {
  content: string;
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export function LearningTooltip({
  content,
  children,
  position = 'top',
  className = '',
}: LearningTooltipProps) {
  const [isHovered, setIsHovered] = useState(false);

  const positionStyles = {
    top: 'bottom-full mb-2',
    bottom: 'top-full mt-2',
    left: 'right-full mr-2',
    right: 'left-full ml-2',
  };

  const arrowStyles = {
    top: 'bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 border-8 border-t-gray-900 border-l-transparent border-r-transparent border-b-transparent',
    bottom:
      'top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 border-8 border-b-gray-900 border-l-transparent border-r-transparent border-t-transparent',
    left: 'right-0 top-1/2 -translate-y-1/2 -translate-x-1/2 border-8 border-l-gray-900 border-t-transparent border-b-transparent border-r-transparent',
    right:
      'left-0 top-1/2 -translate-y-1/2 translate-x-1/2 border-8 border-r-gray-900 border-t-transparent border-b-transparent border-l-transparent',
  };

  return (
    <div
      className={`relative inline-block ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}

      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={`absolute z-50 w-48 rounded-lg bg-gray-900 px-3 py-2 text-sm text-white shadow-lg ${positionStyles[position]}`}
          >
            <div className={arrowStyles[position]} />
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface MilestoneMarkerProps {
  milestone: string;
  icon?: string;
  description?: string;
  onDismiss?: () => void;
  autoClose?: boolean;
  autoCloseDuration?: number;
  className?: string;
}

export function MilestoneMarker({
  milestone,
  icon = '🎉',
  description,
  onDismiss,
  autoClose = true,
  autoCloseDuration = 4000,
  className = '',
}: MilestoneMarkerProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (!autoClose || !isVisible) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      onDismiss?.();
    }, autoCloseDuration);

    return () => clearTimeout(timer);
  }, [autoClose, autoCloseDuration, isVisible, onDismiss]);

  if (!isVisible) return null;

  // Confetti animation
  const confettiPieces = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    delay: Math.random() * 0.3,
    duration: 2 + Math.random() * 1,
    angle: (Math.random() - 0.5) * 2,
    distance: 100 + Math.random() * 100,
  }));

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0, y: -20 }}
      animate={{ scale: 1, opacity: 1, y: 0 }}
      exit={{ scale: 0, opacity: 0, y: -20 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className={`relative mx-auto max-w-sm ${className}`}
    >
      {/* Main card */}
      <div className="rounded-2xl bg-gradient-to-br from-cyan-400 via-blue-400 to-purple-400 p-0.5 shadow-2xl">
        <div className="rounded-2xl bg-white p-8 text-center">
          {/* Confetti animation */}
          {confettiPieces.map((piece) => (
            <motion.div
              key={piece.id}
              className="pointer-events-none absolute text-2xl"
              initial={{ x: 0, y: 0, opacity: 1, rotate: 0 }}
              animate={{
                x: Math.cos(piece.angle) * piece.distance,
                y: Math.sin(piece.angle) * piece.distance,
                opacity: 0,
                rotate: Math.random() * 360,
              }}
              transition={{
                duration: piece.duration,
                delay: piece.delay,
                ease: 'easeOut',
              }}
            >
              {['🎉', '🎊', '⭐', '✨', '🌟'][Math.floor(Math.random() * 5)]}
            </motion.div>
          ))}

          {/* Icon with bounce */}
          <motion.div
            className="mb-4 text-6xl"
            animate={{ y: [0, -20, 0] }}
            transition={{
              duration: 1,
              repeat: Infinity,
              repeatType: 'loop',
            }}
          >
            {icon}
          </motion.div>

          {/* Milestone text */}
          <motion.h3
            className="text-2xl font-bold text-gray-900"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {milestone}
          </motion.h3>

          {/* Description */}
          {description && (
            <motion.p
              className="mt-2 text-sm text-gray-600"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              {description}
            </motion.p>
          )}

          {/* Close button or dismiss hint */}
          <motion.div
            className="mt-6 flex gap-3 justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            {onDismiss && (
              <button
                onClick={() => {
                  setIsVisible(false);
                  onDismiss();
                }}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-200"
              >
                Awesome! 🚀
              </button>
            )}
            {autoClose && (
              <p className="text-xs text-gray-500">Closes in {Math.ceil(autoCloseDuration / 1000)}s</p>
            )}
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

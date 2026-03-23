'use client';

import { useState } from 'react';
import Link from 'next/link';

interface GameCardProps {
  id: string;
  icon: string;
  name: string;
  description?: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  xpReward: number;
  playtime: string;
  locked: boolean;
  unlockAt?: number;
  featured?: boolean;
  href: string;
  accentColor: string;
}

export default function GameCard({
  icon,
  name,
  description,
  difficulty,
  xpReward,
  playtime,
  locked,
  unlockAt,
  featured,
  href,
  accentColor,
}: GameCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const difficultyColors = {
    Beginner: 'bg-green-100 text-green-700',
    Intermediate: 'bg-amber-100 text-amber-700',
    Advanced: 'bg-red-100 text-red-700',
  };

  const colorMap: Record<string, { border: string; bg: string; shadow: string; bar: string }> = {
    teal: {
      border: 'border-cyan-200 hover:border-cyan-400',
      bg: 'bg-cyan-50 hover:bg-cyan-100/50',
      shadow: 'shadow-cyan-100',
      bar: 'bg-cyan-400',
    },
    green: {
      border: 'border-green-200 hover:border-green-400',
      bg: 'bg-green-50 hover:bg-green-100/50',
      shadow: 'shadow-green-100',
      bar: 'bg-green-400',
    },
    purple: {
      border: 'border-purple-200 hover:border-purple-400',
      bg: 'bg-purple-50 hover:bg-purple-100/50',
      shadow: 'shadow-purple-100',
      bar: 'bg-purple-400',
    },
    amber: {
      border: 'border-amber-200 hover:border-amber-400',
      bg: 'bg-amber-50 hover:bg-amber-100/50',
      shadow: 'shadow-amber-100',
      bar: 'bg-amber-400',
    },
    pink: {
      border: 'border-pink-200 hover:border-pink-400',
      bg: 'bg-pink-50 hover:bg-pink-100/50',
      shadow: 'shadow-pink-100',
      bar: 'bg-pink-400',
    },
  };

  const colors = colorMap[accentColor] || colorMap.teal;
  const borderColor = colors.border;
  const bgAccent = colors.bg;
  const bottomBarColor = colors.bar;

  if (locked) {
    return (
      <div
        className={`relative overflow-hidden rounded-xl border-2 border-gray-200 bg-white p-4 transition-all duration-300 opacity-60 cursor-not-allowed`}
      >
        {/* Lock icon */}
        <div className="absolute top-3 right-3 text-lg">🔒</div>

        {/* Content */}
        <div className="flex items-center gap-3 mb-4">
          <div className="text-3xl opacity-50">{icon}</div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-700 text-sm">{name}</h3>
            <p className="text-xs text-gray-500">Unlock at IQ {unlockAt}</p>
          </div>
        </div>

        <div className="h-1 w-full bg-gray-200 rounded-full mt-4" />
      </div>
    );
  }

  return (
    <Link href={href}>
      <div
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`relative overflow-hidden rounded-xl border-2 ${borderColor} ${bgAccent} bg-white p-4 transition-all duration-300 cursor-pointer hover:shadow-lg hover:-translate-y-1 animate-fade-slide-up`}
      >
        {/* Featured Badge */}
        {featured && (
          <div className="absolute top-2 right-2 bg-yellow-300 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">
            ⭐ Featured
          </div>
        )}

        {/* Icon */}
        <div className="text-4xl mb-3">{icon}</div>

        {/* Title */}
        <h3 className="font-bold text-gray-900 text-sm mb-1">{name}</h3>

        {/* Description if provided */}
        {description && (
          <p className="text-xs text-gray-600 mb-3 line-clamp-2">{description}</p>
        )}

        {/* Difficulty Badge */}
        <div className="mb-3">
          <span className={`inline-block text-xs font-semibold px-2 py-1 rounded-full ${difficultyColors[difficulty]}`}>
            {difficulty}
          </span>
        </div>

        {/* Stats Row */}
        <div className="flex items-center justify-between text-xs mb-3 text-gray-600">
          <div className="flex items-center gap-1">
            <span>⏱️</span>
            <span>{playtime}</span>
          </div>
          <div className="flex items-center gap-1 font-semibold text-orange-600">
            <span>⚡</span>
            <span>{xpReward} XP</span>
          </div>
        </div>

        {/* Bottom accent bar */}
        <div className={`absolute bottom-0 left-0 right-0 h-1 ${bottomBarColor} transition-all duration-300 ${isHovered ? 'h-1.5' : 'h-1'}`} />
      </div>
    </Link>
  );
}

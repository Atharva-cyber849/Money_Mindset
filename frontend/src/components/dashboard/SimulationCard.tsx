'use client';

import { useState } from 'react';
import Link from 'next/link';

interface SimulationCardProps {
  id: string;
  icon: string;
  name: string;
  description: string;
  learningValue: string;
  tags?: string[];
  new?: boolean;
  trending?: boolean;
  href: string;
  accentColor: string;
}

export default function SimulationCard({
  icon,
  name,
  description,
  learningValue,
  tags = [],
  new: isNew,
  trending,
  href,
  accentColor,
}: SimulationCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const colorMap = {
    teal: {
      border: 'border-cyan-200 hover:border-cyan-400',
      bg: 'bg-cyan-50 hover:bg-cyan-100/50',
      bar: 'bg-cyan-400',
      tag: 'bg-cyan-100 text-cyan-700',
    },
    green: {
      border: 'border-green-200 hover:border-green-400',
      bg: 'bg-green-50 hover:bg-green-100/50',
      bar: 'bg-green-400',
      tag: 'bg-green-100 text-green-700',
    },
    purple: {
      border: 'border-purple-200 hover:border-purple-400',
      bg: 'bg-purple-50 hover:bg-purple-100/50',
      bar: 'bg-purple-400',
      tag: 'bg-purple-100 text-purple-700',
    },
    amber: {
      border: 'border-amber-200 hover:border-amber-400',
      bg: 'bg-amber-50 hover:bg-amber-100/50',
      bar: 'bg-amber-400',
      tag: 'bg-amber-100 text-amber-700',
    },
    pink: {
      border: 'border-pink-200 hover:border-pink-400',
      bg: 'bg-pink-50 hover:bg-pink-100/50',
      bar: 'bg-pink-400',
      tag: 'bg-pink-100 text-pink-700',
    },
  };

  const colors = colorMap[accentColor as keyof typeof colorMap] || colorMap.teal;
  const borderColor = colors.border;
  const bgAccent = colors.bg;
  const bottomBarColor = colors.bar;
  const tagBgColor = colors.tag;

  return (
    <Link href={href}>
      <div
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`relative overflow-hidden rounded-xl border-2 ${borderColor} ${bgAccent} bg-white p-4 transition-all duration-300 cursor-pointer hover:shadow-lg hover:-translate-y-1 animate-fade-slide-up`}
      >
        {/* New/Trending Badge */}
        <div className="absolute top-2 right-2 flex gap-1">
          {isNew && (
            <div className="bg-green-300 text-green-900 text-xs font-bold px-2 py-1 rounded-full">
              🆕 New
            </div>
          )}
          {trending && (
            <div className="bg-red-300 text-red-900 text-xs font-bold px-2 py-1 rounded-full">
              🔥 Trending
            </div>
          )}
        </div>

        {/* Icon */}
        <div className="text-4xl mb-3">{icon}</div>

        {/* Title */}
        <h3 className="font-bold text-gray-900 text-sm mb-2">{name}</h3>

        {/* Description */}
        <p className="text-xs text-gray-600 mb-3 line-clamp-2">{description}</p>

        {/* Learning Value */}
        <div className="mb-3 text-xs text-gray-700 bg-white rounded px-2 py-1">
          💡 <span className="font-semibold">{learningValue}</span>
        </div>

        {/* Tags */}
        {tags && tags.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {tags.map((tag, idx) => (
              <span
                key={idx}
                className={`text-xs font-semibold px-2 py-1 rounded-full ${tagBgColor}`}
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Bottom accent bar */}
        <div className={`absolute bottom-0 left-0 right-0 h-1 ${bottomBarColor} transition-all duration-300 ${isHovered ? 'h-1.5' : 'h-1'}`} />
      </div>
    </Link>
  );
}

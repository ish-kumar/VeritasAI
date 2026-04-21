/**
 * Glowing Card Component
 * 
 * Inspired by Aceternity UI - Creates an animated glowing border effect
 * on hover using CSS gradients and animations.
 */

'use client';

import { ReactNode } from 'react';

interface GlowingCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: 'blue' | 'purple' | 'emerald' | 'amber' | 'rose';
}

export function GlowingCard({ 
  children, 
  className = '', 
  glowColor = 'blue' 
}: GlowingCardProps) {
  const glowColors = {
    blue: 'before:bg-gradient-to-r before:from-blue-500 before:to-purple-600',
    purple: 'before:bg-gradient-to-r before:from-purple-500 before:to-pink-600',
    emerald: 'before:bg-gradient-to-r before:from-emerald-500 before:to-blue-500',
    amber: 'before:bg-gradient-to-r before:from-amber-500 before:to-orange-500',
    rose: 'before:bg-gradient-to-r before:from-rose-500 before:to-pink-500',
  };

  return (
    <div 
      className={`
        relative group
        rounded-2xl
        transition-all duration-300
        ${className}
      `}
    >
      {/* Animated glowing border */}
      <div 
        className={`
          absolute inset-0 rounded-2xl
          opacity-0 group-hover:opacity-100
          transition-opacity duration-500
          ${glowColors[glowColor]}
          blur-xl
        `}
        style={{
          background: 'linear-gradient(90deg, var(--tw-gradient-stops))',
        }}
      />
      
      {/* Card content */}
      <div className="relative glass rounded-2xl p-6 border border-white/10 group-hover:border-white/20 transition-all duration-300">
        {children}
      </div>
    </div>
  );
}

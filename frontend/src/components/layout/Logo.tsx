// frontend/src/components/layout/Logo.tsx
'use client';

import React from 'react';

interface LogoProps {
  width?: number;
  height?: number;
  className?: string;
}

const Logo: React.FC<LogoProps> = ({ width = 40, height = 40, className = '' }) => {
  return (
    <svg 
      width={width} 
      height={height} 
      viewBox="0 0 300 300" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer circle */}
      <circle 
        cx="150" 
        cy="150" 
        r="120" 
        fill="none" 
        stroke="var(--color-logo)" 
        strokeWidth="3"
      />
      
      {/* Single prominent leaf */}
      <path 
        d="M150 70 C190 110, 210 150, 150 210 C90 150, 110 110, 150 70" 
        fill="var(--color-logo)"
      />
      
      {/* Leaf vein details */}
      <path 
        d="M150 75 C150 120, 150 165, 150 205" 
        fill="none" 
        stroke="var(--color-logo)" 
        strokeWidth="1.5"
      />
      <path 
        d="M150 120 C130 140, 170 140, 150 120" 
        fill="none" 
        stroke="var(--color-logo)" 
        strokeWidth="1"
      />
      <path 
        d="M150 150 C120 160, 180 160, 150 150" 
        fill="none" 
        stroke="var(--color-logo)" 
        strokeWidth="1"
      />
      <path 
        d="M150 180 C130 185, 170 185, 150 180" 
        fill="none" 
        stroke="var(--color-logo)" 
        strokeWidth="1"
      />
      
      {/* Glow effect */}
      <circle 
        cx="150" 
        cy="150" 
        r="90" 
        fill="none" 
        stroke="var(--color-logo)" 
        strokeWidth="1" 
        opacity="0.6"
      />
      
      {/* Vegan symbol */}
      <rect 
        x="125" 
        y="175" 
        width="50" 
        height="18" 
        rx="9" 
        fill="var(--color-background)"
      />
      <text 
        x="150" 
        y="188" 
        fontFamily="Arial, sans-serif" 
        fontSize="12" 
        fontWeight="bold" 
        textAnchor="middle" 
        fill="var(--color-logo)"
      >
        VEGAN
      </text>
    </svg>
  );
};

export default Logo;
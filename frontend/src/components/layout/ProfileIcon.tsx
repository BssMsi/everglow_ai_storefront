'use client';

import React from 'react';

interface ProfileIconProps {
  width?: number;
  height?: number;
  className?: string;
}

const ProfileIcon: React.FC<ProfileIconProps> = ({ 
  width = 32, 
  height = 32, 
  className = '' 
}) => {
  return (
    <svg 
      className={`profile-icon ${className}`}
      width={width}
      height={height}
      viewBox="0 0 24 24" 
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Circular border/outline */}
      <circle 
        cx="12" 
        cy="12" 
        r="11" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="1.5"
      />
      {/* Head */}
      <circle cx="12" cy="9" r="3" fill="currentColor" />
      {/* Body - rounded shoulders */}
      <path d="M6 18c0-3.5 2.5-6 6-6s6 2.5 6 6" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
    </svg>
  );
};

export default ProfileIcon;
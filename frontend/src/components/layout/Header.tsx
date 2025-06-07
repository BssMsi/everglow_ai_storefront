// frontend/src/components/layout/Header.tsx
'use client';

import Link from 'next/link';
import Logo from './Logo';
import ProfileIcon from './ProfileIcon';

const Header = () => {
  return (
    <header className="w-full bg-[var(--color-background)] border-b border-[var(--color-secondary)]/20">
      <nav className="flex items-center justify-between margin-[0_auto] padding-[1rem_1.5rem]">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-[0.5rem] group no-underline">
          <Logo width={40} height={40} className="text-[var(--color-logo)]" />
          <span className="text-lg font-semibold text-[var(--color-foreground)] group-hover:text-[var(--color-primary)] transition-colors duration-200">
            EverGlow
          </span>
        </Link>
        
        {/* Right Navigation */}
        <div className="flex items-center gap-[2rem]">
          <Link 
            href="/" 
            className="no-underline text-[var(--color-foreground)]/70 hover:text-[var(--color-primary)] font-medium transition-colors duration-200"
          >
            Shop
          </Link>
          <Link 
            href="/learn" 
            className="no-underline text-[var(--color-foreground)]/70 hover:text-[var(--color-primary)] font-medium transition-colors duration-200"
          >
            Learn
          </Link>
          <Link 
            href="/about" 
            className="no-underline text-[var(--color-foreground)]/70 hover:text-[var(--color-primary)] font-medium transition-colors duration-200"
          >
            About
          </Link>
          
          {/* Profile Icon */}
          <button className="relative group focus:outline-none transition-all duration-200 border-none bg-transparent">
            <ProfileIcon 
              width={28} 
              height={28} 
              className="text-[var(--color-primary)] group-hover:text-[var(--color-foreground)] transition-colors duration-200" 
            />
          </button>
        </div>
      </nav>
    </header>
  );
};

export default Header;

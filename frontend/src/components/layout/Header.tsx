// frontend/src/components/layout/Header.tsx
'use client';

import Link from 'next/link';
import Logo from './Logo';
import ProfileIcon from './ProfileIcon';

const Header = () => {
  return (
    <header className="w-full bg-[var(--color-background)] border-b border-[var(--color-secondary)]/20">
      <nav className="flex items-center justify-between max-w-7xl mx-auto px-6 py-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <Logo width={24} height={24} className="text-[var(--color-logo)]" />
          <span className="text-lg font-semibold text-[var(--color-foreground)] group-hover:text-[var(--color-primary)] transition-colors duration-200">
            EcoSkin
          </span>
        </Link>
        
        {/* Right Navigation */}
        <div className="flex items-center gap-6">
          <Link 
            href="/shop" 
            className="text-[var(--color-foreground)]/80 hover:text-[var(--color-foreground)] font-medium transition-colors duration-200"
          >
            Shop
          </Link>
          <Link 
            href="/learn" 
            className="text-[var(--color-foreground)]/80 hover:text-[var(--color-foreground)] font-medium transition-colors duration-200"
          >
            Learn
          </Link>
          <Link 
            href="/about" 
            className="text-[var(--color-foreground)]/80 hover:text-[var(--color-foreground)] font-medium transition-colors duration-200"
          >
            About
          </Link>
          
          {/* Profile Icon */}
          <button className="relative group focus:outline-none p-2 rounded-lg hover:bg-[var(--color-secondary)]/20 transition-all duration-200">
            <ProfileIcon 
              width={24} 
              height={24} 
              className="text-[var(--color-profile)] group-hover:text-[var(--color-primary)] transition-colors duration-200" 
            />
          </button>
        </div>
      </nav>
    </header>
  );
};

export default Header;

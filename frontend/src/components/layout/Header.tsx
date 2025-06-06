// frontend/src/components/layout/Header.tsx
'use client';

import Link from 'next/link';
import Image from 'next/image';
import Logo from './Logo';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';

const navLinks = [
  { href: '/shop', label: 'Shop' },
  { href: '/learn', label: 'Learn' },
  { href: '/about', label: 'About' },
];

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 left-0 right-0 z-50 bg-[var(--color-background)]/95 backdrop-blur-md border-b border-[var(--color-secondary)]/30 shadow-lg">
      <nav className="flex items-center justify-between max-w-7xl mx-auto px-6 py-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="transition-transform duration-300 group-hover:scale-110">
            <Logo width={48} height={48} className="drop-shadow-sm" />
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold text-[var(--color-foreground)] tracking-tight group-hover:text-[var(--color-primary)] transition-colors duration-300">
              EverGlow
            </span>
            <span className="text-sm font-medium text-[var(--color-foreground)]/70 -mt-1">
              Labs
            </span>
          </div>
        </Link>
        
        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-2">
          {navLinks.map(link => (
            <Link 
              key={link.href} 
              href={link.href} 
              className="relative px-4 py-2 text-[var(--color-foreground)]/80 hover:text-[var(--color-foreground)] font-medium transition-all duration-300 rounded-lg hover:bg-[var(--color-secondary)]/20 group"
            >
              <span className="relative z-10">{link.label}</span>
              <div className="absolute inset-0 bg-gradient-to-r from-[var(--color-primary)]/10 to-[var(--color-primary)]/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="absolute bottom-0 left-1/2 w-0 h-0.5 bg-[var(--color-primary)] group-hover:w-8 group-hover:left-1/2 group-hover:-translate-x-1/2 transition-all duration-300" />
            </Link>
          ))}
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Profile Avatar */}
          <button className="relative group focus:outline-none">
            <div className="absolute inset-0 bg-[var(--color-primary)]/20 rounded-full scale-0 group-hover:scale-110 group-focus:scale-110 transition-transform duration-300" />
            <Image 
              src="https://i.pravatar.cc/150?img=32"
              alt="Profile"
              width={44}
              height={44} 
              className="relative z-10 rounded-full border-2 border-[var(--color-secondary)]/30 group-hover:border-[var(--color-primary)]/50 transition-all duration-300 shadow-md"
            />
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-[var(--color-background)] rounded-full" />
          </button>

          {/* Mobile Menu Button */}
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg bg-[var(--color-secondary)]/20 hover:bg-[var(--color-secondary)]/30 transition-colors duration-200"
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? (
              <X className="h-5 w-5 text-[var(--color-foreground)]" />
            ) : (
              <Menu className="h-5 w-5 text-[var(--color-foreground)]" />
            )}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-[var(--color-secondary)]/30 bg-[var(--color-background)]/95 backdrop-blur-md">
          <div className="px-6 py-4 space-y-2">
            {navLinks.map(link => (
              <Link 
                key={link.href} 
                href={link.href} 
                onClick={() => setIsMobileMenuOpen(false)}
                className="block px-4 py-3 text-[var(--color-foreground)]/80 hover:text-[var(--color-foreground)] hover:bg-[var(--color-secondary)]/20 rounded-lg transition-all duration-200 font-medium"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;

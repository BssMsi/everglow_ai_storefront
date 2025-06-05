// frontend/src/components/layout/Header.tsx
import Link from 'next/link';
import { ShoppingCart, User } from 'lucide-react';
import Image from 'next/image';

const navLinks = [
  { href: '/shop', label: 'Shop' },
  { href: '/learn', label: 'Learn' },
  { href: '/about', label: 'About' },
];

const Header = () => {
  return (
    <header className="sticky top-0 left-0 right-0 z-50 bg-[var(--color-background)] border-b border-[var(--color-secondary)]">
      <nav className="flex items-center justify-between max-w-7xl mx-auto px-6 py-4">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Image src="/logo-placeholder.png" alt="Logo" width={32} height={32} className="rounded" />
          <span className="text-xl font-bold text-white tracking-tight">EcoSkin</span>
        </div>
        {/* Navigation */}
        <div className="flex gap-8">
          {navLinks.map(link => (
            <a key={link.href} href={link.href} className="text-white text-base font-medium hover:text-blue-300 transition-colors duration-200">
              {link.label}
            </a>
          ))}
        </div>
        {/* Profile Avatar */}
        <div>
          <Image src="/avatar-placeholder.png" alt="Profile" width={36} height={36} className="rounded-full border-2 border-white" />
        </div>
      </nav>
    </header>
  );
};

export default Header;

// frontend/src/components/layout/Header.tsx
import Link from 'next/link';
import Image from 'next/image';

const navLinks = [
  { href: '/shop', label: 'Shop' },
  { href: '/learn', label: 'Learn' },
  { href: '/about', label: 'About' },
];

const Header = () => {
  return (
    <header className="sticky top-0 left-0 right-0 z-50 bg-[var(--color-background)] border-b border-[var(--color-secondary)] shadow-sm">
      <nav className="flex items-center justify-between max-w-7xl mx-auto px-6 py-3">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <Image 
            src="/placeholder-logo.svg" // Using a placeholder SVG
            alt="EcoSkin Logo"
            width={32} // Adjusted size
            height={32}
            className="h-8 w-auto"
          />
          <span className="text-xl font-semibold text-white tracking-tight">EcoSkin</span>
        </Link>
        {/* Navigation */}
        <div className="flex items-center gap-6">
          {navLinks.map(link => (
            <a 
              key={link.href} 
              href={link.href} 
              className="text-sm font-medium text-gray-300 hover:text-white transition-colors duration-200"
            >
              {link.label}
            </a>
          ))}
        </div>
        {/* Profile Avatar */}
        <div className="flex items-center">
          <Image 
            src="https://i.pravatar.cc/150?img=32" 
            alt="Profile" 
            width={32} // Adjusted size
            height={32} 
            className="rounded-full border-2 border-transparent hover:border-[var(--color-primary)] transition-colors duration-200 cursor-pointer"
          />
        </div>
      </nav>
    </header>
  );
};

export default Header;

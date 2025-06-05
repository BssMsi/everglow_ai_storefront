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
    <header className="sticky top-0 left-0 right-0 z-50 bg-[var(--color-background)] border-b border-[var(--color-secondary)]/50 shadow-sm">
      <nav className="flex items-center justify-between max-w-7xl mx-auto px-6 py-4"> {/* Increased py */}
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          {/* Placeholder for a more abstract logo if you have one, or keep text-based */}
          {/* For the image provided, it's a text logo with a small graphic */}
          <div className="w-7 h-7 bg-white flex items-center justify-center rounded-md group-hover:opacity-90 transition-opacity">
            {/* You can replace this with an actual SVG icon if you have one */}
            <span className="text-sm font-bold text-[var(--color-background)]">E</span>
          </div>
          <span className="text-2xl font-bold text-white tracking-tight group-hover:text-gray-300 transition-colors">EcoSkin</span>
        </Link>
        
        {/* Navigation */} 
        <div className="flex items-center gap-8"> {/* Increased gap */}
          {navLinks.map(link => (
            <Link 
              key={link.href} 
              href={link.href} 
              className="text-base font-medium text-gray-300 hover:text-white transition-colors duration-200 pb-1 border-b-2 border-transparent hover:border-white"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Profile Avatar */}
        <div className="flex items-center">
          <button className="focus:outline-none rounded-full focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-background)]">
            <Image 
              src="https://i.pravatar.cc/150?img=32" // Placeholder, replace with actual user avatar if available
              alt="Profile"
              width={40} // Increased size
              height={40} 
              className="rounded-full border-2 border-transparent hover:border-[var(--color-primary)] transition-colors duration-200 cursor-pointer"
            />
          </button>
        </div>
      </nav>
    </header>
  );
};

export default Header;

// frontend/src/components/layout/Header.tsx
import Link from 'next/link';

const Header = () => {
  return (
    // Use a class that will pick up CSS variables, or style directly
    // For PoC, we assume Tailwind classes are set up to use these, or we add custom ones.
    // <header className="fixed top-0 left-0 right-0 bg-gray-800 text-white p-4 shadow-md z-50">
    <header className="fixed top-0 left-0 right-0 p-4 shadow-md z-50" style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-background)'}}>
      <nav className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-xl font-bold" style={{ color: 'var(--color-background)' }}>
          EverGlow
        </Link>
        <div>
          <Link href="/" className="px-3 hover:opacity-80" style={{ color: 'var(--color-background)'}}>
            Home
          </Link>
          <Link href="/about" className="px-3 hover:opacity-80" style={{ color: 'var(--color-background)'}}>
            About
          </Link>
          <Link href="/profile" className="px-3 hover:opacity-80" style={{ color: 'var(--color-background)'}}>
            Profile
          </Link>
        </div>
      </nav>
    </header>
  );
};

export default Header;

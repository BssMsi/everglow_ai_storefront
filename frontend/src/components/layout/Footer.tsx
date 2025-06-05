// frontend/src/components/layout/Footer.tsx
const Footer = () => {
  return (
    <footer className="fixed bottom-0 left-0 right-0 z-50 backdrop-blur-md bg-[var(--color-secondary)]/80 text-[var(--color-text)] shadow-lg transition-all py-3 px-4 text-center flex flex-col md:flex-row md:justify-between md:items-center">
      <p className="mb-2 md:mb-0">&copy; {new Date().getFullYear()} EverGlow. All rights reserved.</p>
      <div className="flex gap-4 justify-center">
        <a href="/about" className="hover:text-pink-400 transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-pink-400">About</a>
        <a href="/profile" className="hover:text-pink-400 transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-pink-400">Profile</a>
      </div>
    </footer>
  );
};

export default Footer;

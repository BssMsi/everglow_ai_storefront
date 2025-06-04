// frontend/src/components/layout/Footer.tsx
const Footer = () => {
  return (
    // <footer className="fixed bottom-0 left-0 right-0 bg-gray-700 text-white p-4 text-center z-50">
    <footer className="fixed bottom-0 left-0 right-0 p-4 text-center z-50" style={{ backgroundColor: 'var(--color-secondary)', color: 'var(--color-text)'}}>
      <p>&copy; {new Date().getFullYear()} EverGlow. All rights reserved.</p>
    </footer>
  );
};

export default Footer;

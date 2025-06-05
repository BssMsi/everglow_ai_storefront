import React from 'react';
import Link from 'next/link';

const Hero = () => (
  <section className="relative w-full flex flex-col items-center justify-center py-20 px-4 bg-gradient-to-br from-[var(--color-primary)]/10 to-[var(--color-secondary)]/40 text-center overflow-hidden">
    <div className="max-w-2xl z-10">
      <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-[var(--color-primary)] drop-shadow-lg">Welcome to EverGlow</h1>
      <p className="text-lg md:text-2xl mb-8 text-[var(--color-text)]">Discover your natural radiance with our vegan skincare.</p>
      <Link href="/#products">
        <button className="button-primary text-lg px-8 py-3 rounded-full shadow-lg hover:scale-105 hover:shadow-xl transition-all duration-300">
          Shop Now
        </button>
      </Link>
    </div>
    {/* Decorative background shapes */}
    <div className="absolute -top-20 -left-20 w-72 h-72 bg-[var(--color-primary)] opacity-20 rounded-full blur-3xl z-0"></div>
    <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-[var(--color-secondary)] opacity-30 rounded-full blur-3xl z-0"></div>
  </section>
);

export default Hero; 
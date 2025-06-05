// frontend/src/app/page.tsx
import { ChatSearchBar } from '@/components/search/ChatSearchBar';
import ProductList from '@/components/products/ProductList';
import { dummyProducts } from '@/data/dummyProducts'; // Make sure this path is correct
import Hero from '@/components/layout/Hero';
import SuggestionRow from '@/components/suggestions/SuggestionRow';

const suggestions = [
  {
    imageUrl: 'https://picsum.photos/seed/vegan1/100/100',
    text: "What's the best vegan moisturizer for dry skin?",
  },
  {
    imageUrl: 'https://picsum.photos/seed/vegan2/100/100',
    text: 'Show me the top-rated vegan sunscreens.',
  },
  {
    imageUrl: 'https://picsum.photos/seed/vegan3/100/100',
    text: 'What are the benefits of using vegan skincare?',
  },
  {
    imageUrl: 'https://picsum.photos/seed/vegan4/100/100',
    text: 'Can you recommend a vegan night cream?',
  },
  {
    imageUrl: 'https://picsum.photos/seed/vegan5/100/100',
    text: 'What\'s the difference between vegan and cruelty-free?',
  },
  {
    imageUrl: 'https://picsum.photos/seed/vegan6/100/100',
    text: 'Find vegan options for sensitive skin.',
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)]">
      <Hero />
      <div className="flex flex-col items-center w-full px-2">
        <ChatSearchBar />
        <SuggestionRow suggestions={suggestions} />
      </div>
      <section id="products">
        <ProductList initialProducts={dummyProducts} />
      </section>
    </div>
  );
}

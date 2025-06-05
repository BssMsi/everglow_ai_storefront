// frontend/src/app/page.tsx
import { ChatSearchBar } from '@/components/search/ChatSearchBar';
import ProductList from '@/components/products/ProductList';
import { dummyProducts } from '@/data/dummyProducts';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)]">
      <div className="flex flex-col items-center w-full px-4 pt-10 pb-6 md:px-6">
        <ChatSearchBar placeholder="What's the best vegan moisturizer for dry skin?" />
      </div>
      <section id="products" className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-semibold text-white mb-6 text-center">Featured Products</h2>
          <ProductList initialProducts={dummyProducts} />
        </div>
      </section>
    </div>
  );
}

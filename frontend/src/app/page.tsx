'use client';

import { ChatSearchBar } from '@/components/search/ChatSearchBar';
import ProductList from '@/components/products/ProductList';
import { dummyProducts } from '@/data/dummyProducts';
import { useState } from 'react';
import { Product } from '@/types/product';

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);

  const handleProductsFound = (newProducts: Product[]) => {
    setProducts(newProducts);
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)]">
      <div className="flex flex-col items-center w-full px-4 pt-10 pb-6 md:px-6">
        <ChatSearchBar 
          placeholder="What's the best vegan moisturizer for dry skin?" 
          onProductsFound={handleProductsFound}
        />
      </div>
      <section id="products" className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ProductList products={products} />
        </div>
      </section>
    </div>
  );
}

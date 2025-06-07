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
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Search Section */}
      <div className="flex flex-col items-center w-full px-6 pt-8 pb-12">
        <div className="w-full max-w-2xl">
          <ChatSearchBar 
            onProductsFound={handleProductsFound}
          />
        </div>
      </div>
      
      {/* Products Section */}
      <section className="pb-12">
        <div className="max-w-7xl mx-auto px-6">
          <ProductList products={products} />
        </div>
      </section>
    </div>
  );
}

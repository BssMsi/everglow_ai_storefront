// frontend/src/components/products/ProductList.tsx
'use client'; // If we plan to update products dynamically based on agent response

import { Product } from '@/types/product'; // Import Product from types
import ProductCard from './ProductCard';
import { useEffect, useState } from 'react';

type ProductListProps = {
  products: Product[]; // Use the imported Product type
};

const ProductList = ({ products }: ProductListProps) => {
  // Sort products by margin (descending)
  const sortedProducts = [...products].sort((a, b) => b.margin - a.margin);
  if (!sortedProducts || sortedProducts.length === 0) {
    return <p className="text-center text-gray-500">Enter your query in the Seach Bar to find products</p>;
  }

  return (
    <section className="w-full max-w-7xl mx-auto px-4 py-12">
      <h2 className="text-3xl font-bold text-[var(--color-primary)] mb-8 text-center">Our Products</h2>
      <div className="flex gap-[32px] overflow-x-auto pb-4 scrollbar-hide">
        {sortedProducts.map((product) => (
          <div key={product.product_id} className="min-w-[260px] max-w-[300px]">
            <ProductCard product={product} />
          </div>
        ))}
      </div>
    </section>
  );
};

export default ProductList;

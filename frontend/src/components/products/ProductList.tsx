// frontend/src/components/products/ProductList.tsx
'use client'; // If we plan to update products dynamically based on agent response

import { Product } from '@/types/product';
import ProductCard from './ProductCard';
import { useEffect, useState } from 'react';

type ProductListProps = {
  initialProducts: Product[];
};

const ProductList = ({ initialProducts }: ProductListProps) => {
  // In a real app, products might come from state management or props updated by AI agent
  const [products, setProducts] = useState<Product[]>(initialProducts);

  // Sort products by margin (descending)
  const sortedProducts = [...products].sort((a, b) => b.margin - a.margin);

  // Example of how products could be updated (e.g., by AI agent response)
  // useEffect(() => {
  //   // Simulate receiving new products from agent after 2 seconds
  //   const timer = setTimeout(() => {
  //     const newProductsFromAgent = [initialProducts[0], initialProducts[2]]; // example
  //     setProducts(newProductsFromAgent);
  //   }, 2000);
  //   return () => clearTimeout(timer);
  // }, []);


  if (!sortedProducts || sortedProducts.length === 0) {
    return <p className="text-center text-gray-500">No products to display currently.</p>;
  }

  return (
    <section className="w-full max-w-7xl mx-auto px-4 py-12">
      <h2 className="text-3xl font-bold text-[var(--color-primary)] mb-8 text-center">Our Products</h2>
      <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide">
        {sortedProducts.map((product) => (
          <div key={product.id} className="min-w-[260px] max-w-[260px]">
            <ProductCard product={product} />
          </div>
        ))}
      </div>
    </section>
  );
};

export default ProductList;

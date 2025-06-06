// frontend/src/components/products/ProductCard.tsx
import { Product } from '@/types/product';
import Image from 'next/image';
import Link from 'next/link';

// Modern, adaptive, interactive product card
const ProductCard = ({ product }: { product: Product }) => {
  return (
    <div className="group border border-[var(--color-secondary)] rounded-xl shadow-lg hover:shadow-[0_10px_30px_-15px_rgba(0,0,0,0.2)] transition-all duration-300 overflow-hidden bg-[var(--color-secondary)] hover:scale-[1.02] transform-gpu cursor-pointer flex flex-col h-full">
      <Link href={`/products/${product.product_id}`} className="block flex flex-col h-full">
        <div className="relative w-full h-48 sm:h-52 cursor-pointer bg-[var(--color-background)] overflow-hidden">
          {product.imageUrl && (
            <Image
              src={product.imageUrl}
              alt={product.name}
              fill
              style={{ objectFit: 'cover' }}
              className="transition-transform duration-300 group-hover:scale-105"
            />
          )}
        </div>
        <div className="p-4 flex flex-col gap-1.5 flex-grow">
          <h3 className="text-md font-semibold text-[var(--color-primary)] mb-0.5 truncate group-hover:text-white transition-colors">
            {product.name}
          </h3>
          <p className="text-xs text-gray-400 mb-1 capitalize">{product.category}</p>
          <p className="text-white font-bold text-lg mb-2.5">${product.priceusd?.toFixed(2)}</p>
          <div className="mt-auto pt-2">
            <button className="w-full px-4 py-2 rounded-lg bg-[var(--color-primary)] text-white text-sm font-medium shadow-md hover:bg-opacity-80 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-secondary)] transition-all duration-200">
              View Details
            </button>
          </div>
        </div>
      </Link>
    </div>
  );
};

export default ProductCard;

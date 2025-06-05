// frontend/src/components/products/ProductCard.tsx
import { Product } from '@/types/product';
import Image from 'next/image';
import Link from 'next/link';

// Modern, adaptive, interactive product card
const ProductCard = ({ product }: { product: Product }) => {
  return (
    <div className="group border border-[var(--color-secondary)] rounded-2xl shadow-lg hover:shadow-2xl transition-shadow duration-300 overflow-hidden bg-[var(--color-secondary)]/80 hover:scale-[1.03] transform-gpu cursor-pointer">
      <Link href={`/products/${product.id}`} className="block">
        <div className="relative w-full h-44 cursor-pointer bg-[var(--color-background)]">
          {product.imageUrl && (
            <Image
              src={product.imageUrl}
              alt={product.name}
              fill
              style={{ objectFit: 'cover' }}
              className="transition-transform duration-300 group-hover:scale-105 rounded-t-2xl"
            />
          )}
        </div>
        <div className="p-4 flex flex-col gap-1">
          <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-1 truncate">{product.name}</h3>
          <p className="text-sm text-[var(--color-text)] opacity-70 mb-1">{product.category}</p>
          <p className="text-pink-400 font-bold text-xl mb-2">${product.price.toFixed(2)}</p>
          <button className="mt-2 px-4 py-1 rounded-full bg-[var(--color-primary)] text-[var(--color-background)] text-sm font-medium shadow hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-pink-400 transition-all">View Details</button>
        </div>
      </Link>
      {/* TODO: Add micro-interactions or quick add-to-cart in future */}
    </div>
  );
};

export default ProductCard;

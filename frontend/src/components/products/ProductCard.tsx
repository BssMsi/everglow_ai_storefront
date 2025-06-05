// frontend/src/components/products/ProductCard.tsx
import { Product } from '@/types/product';
import Image from 'next/image';
import Link from 'next/link';

type ProductCardProps = {
  product: Product;
};

const ProductCard = ({ product }: ProductCardProps) => {
  return (
    <div className="border rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden bg-white">
      <Link href={`/products/${product.id}`}>
        <div className="relative w-full h-48 cursor-pointer">
          {product.imageUrl && (
            <Image
              src={product.imageUrl}
              alt={product.name}
              fill
              style={{ objectFit: 'cover' }}
            />
          )}
          <div className="p-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">{product.name}</h3>
            <p className="text-sm text-gray-500 mb-2">{product.category}</p>
            <p className="text-pink-500 font-bold text-xl mb-3">${product.price.toFixed(2)}</p>
            {/* <p className="text-xs text-gray-400">Margin: {product.margin}</p> */}
          </div>
        </div>
      </Link>
    </div>
  );
};

export default ProductCard;

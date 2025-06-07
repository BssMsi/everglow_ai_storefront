import { Product } from '@/types/product';
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const ProductCard = ({ product }: { product: Product }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  const getProductImages = (productId: string): string[] => {
    const baseImageSets = [
      [
        '1.png',
        '2.png'
      ]
    ];
    
    const setIndex = productId.charCodeAt(productId.length - 1) % baseImageSets.length;
    const imageSet = baseImageSets[setIndex];
    
    return imageSet.map(filename => `/products/${productId}/${filename}`);
  };

  const productImages = getProductImages(product.product_id);

  const nextImage = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex((prev) => 
      prev === productImages.length - 1 ? 0 : prev + 1
    );
  };

  const prevImage = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex((prev) => 
      prev === 0 ? productImages.length - 1 : prev - 1
    );
  };

  const goToImage = (index: number, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex(index);
  };

  return (
    <div className="group bg-[var(--color-secondary)]/30 rounded-[16px] overflow-hidden hover:bg-[var(--color-secondary)]/40 transition-all duration-[300ms] cursor-pointer h-[400px] flex flex-col">
      <Link href={`/products/${product.product_id}`} className="block h-full flex flex-col no-underline cursor-pointer">
        {/* Image Section - Top */}
        <div className="relative w-full h-[280px] bg-gradient-to-br from-[var(--color-background)] to-[var(--color-secondary)]/20 overflow-hidden flex-shrink-0">
          <Image
            src={productImages[currentImageIndex]}
            alt={`${product.name} - Image ${currentImageIndex + 1}`}
            fill
            style={{ objectFit: 'cover' }}
            className="transition-transform duration-[500ms] group-hover:scale-[1.05]"
            onError={(e) => {
              if (product.imageUrl) {
                (e.target as HTMLImageElement).src = product.imageUrl;
              }
            }}
          />
          
          {/* Carousel Controls */}
          {productImages.length > 1 && (
            <>
              <button
                onClick={prevImage}
                className="absolute left-[12px] top-1/2 transform -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white rounded-full p-[8px] opacity-0 group-hover:opacity-100 transition-all duration-[200ms] z-10 cursor-pointer"
                aria-label="Previous image"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-[12px] top-1/2 transform -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white rounded-full p-[8px] opacity-0 group-hover:opacity-100 transition-all duration-[200ms] z-10 cursor-pointer"
                aria-label="Next image"
              >
                <ChevronRight size={16} />
              </button>
              
              <div className="absolute bottom-[12px] left-1/2 transform -translate-x-1/2 flex space-x-[8px] opacity-0 group-hover:opacity-100 transition-opacity duration-[200ms]">
                {productImages.map((_, index) => (
                  <button
                    key={index}
                    onClick={(e) => goToImage(index, e)}
                    className={`w-[8px] h-[8px] rounded-full transition-colors duration-[200ms] cursor-pointer ${
                      index === currentImageIndex 
                        ? 'bg-white' 
                        : 'bg-white/40 hover:bg-white/70'
                    }`}
                    aria-label={`Go to image ${index + 1}`}
                  />
                ))}
              </div>
            </>
          )}
        </div>
        
        {/* Details Section - Bottom */}
        <div className="p-[16px] space-y-[8px] flex-1 flex flex-col justify-between">
          <div className="space-y-[8px]">
            <h3 className="font-medium text-[var(--color-foreground)] hover:text-[var(--color-primary)] text-[14px] leading-tight line-clamp-2">
              {product.name}
            </h3>
            <p className="text-[var(--color-foreground)]/60 text-[12px] capitalize">
              {product.category}
            </p>
          </div>
          <p className="text-[var(--color-foreground)] font-semibold text-[14px] mt-auto">
            ${product.priceusd?.toFixed(2)}
          </p>
        </div>
      </Link>
    </div>
  );
};

export default ProductCard;

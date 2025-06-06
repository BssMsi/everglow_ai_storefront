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
        'Gemini_Generated_Image_q0dstcq0dstcq0ds.png',
        'Gemini_Generated_Image_v9x766v9x766v9x7.png'
      ],
      [
        'Gemini_Generated_Image_kkwy37kkwy37kkwy.png',
        'Gemini_Generated_Image_wb6xamwb6xamwb6x.png'
      ],
      [
        'Gemini_Generated_Image_hd1epuhd1epuhd1e.png',
        'Gemini_Generated_Image_hd1epwhd1epwhd1e.png'
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
    <div className="group bg-[var(--color-secondary)]/30 rounded-2xl overflow-hidden hover:bg-[var(--color-secondary)]/40 transition-all duration-300 cursor-pointer">
      <Link href={`/products/${product.product_id}`} className="block">
        {/* Image Section - Top */}
        <div className="relative w-full aspect-square bg-gradient-to-br from-[var(--color-background)] to-[var(--color-secondary)]/20 overflow-hidden">
          <Image
            src={productImages[currentImageIndex]}
            alt={`${product.name} - Image ${currentImageIndex + 1}`}
            fill
            style={{ objectFit: 'cover' }}
            className="transition-transform duration-500 group-hover:scale-105"
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
                className="absolute left-3 top-1/2 transform -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-all duration-200 z-10"
                aria-label="Previous image"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-all duration-200 z-10"
                aria-label="Next image"
              >
                <ChevronRight size={16} />
              </button>
              
              <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                {productImages.map((_, index) => (
                  <button
                    key={index}
                    onClick={(e) => goToImage(index, e)}
                    className={`w-2 h-2 rounded-full transition-colors duration-200 ${
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
        <div className="p-4 space-y-2">
          <h3 className="font-medium text-[var(--color-foreground)] text-sm leading-tight line-clamp-2">
            {product.name}
          </h3>
          <p className="text-[var(--color-foreground)]/60 text-xs capitalize">
            {product.category}
          </p>
          <p className="text-[var(--color-foreground)] font-semibold text-sm">
            ${product.priceusd?.toFixed(2)}
          </p>
        </div>
      </Link>
    </div>
  );
};

export default ProductCard;

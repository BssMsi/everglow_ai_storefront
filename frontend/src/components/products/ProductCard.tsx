// frontend/src/components/products/ProductCard.tsx
import { Product } from '@/types/product';
import Image from 'next/image';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

// Modern, adaptive, interactive product card with image carousel
const ProductCard = ({ product }: { product: Product }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  // Generate image paths based on the directory structure
  // Each product has 2 images with these common patterns
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
    
    // For demo purposes, we'll cycle through the image sets
    // In a real app, you'd have a mapping or API to determine which images belong to which product
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
    <div className="group border border-[var(--color-secondary)] rounded-xl shadow-lg hover:shadow-[0_10px_30px_-15px_rgba(0,0,0,0.2)] transition-all duration-300 overflow-hidden bg-[var(--color-secondary)] hover:scale-[1.02] transform-gpu cursor-pointer flex flex-col h-full">
      <Link href={`/products/${product.product_id}`} className="block flex flex-col h-full">
        <div className="relative w-full h-48 sm:h-52 cursor-pointer bg-[var(--color-background)] overflow-hidden">
          <Image
            src={productImages[currentImageIndex]}
            alt={`${product.name} - Image ${currentImageIndex + 1}`}
            fill
            style={{ objectFit: 'cover' }}
            className="transition-transform duration-300 group-hover:scale-105"
            onError={(e) => {
              // Fallback to original imageUrl if the generated path fails
              if (product.imageUrl) {
                (e.target as HTMLImageElement).src = product.imageUrl;
              }
            }}
          />
          
          {/* Carousel Controls - Only show if more than 1 image */}
          {productImages.length > 1 && (
            <>
              {/* Navigation Arrows */}
              <button
                onClick={prevImage}
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10"
                aria-label="Previous image"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10"
                aria-label="Next image"
              >
                <ChevronRight size={16} />
              </button>
              
              {/* Dot Indicators */}
              <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                {productImages.map((_, index) => (
                  <button
                    key={index}
                    onClick={(e) => goToImage(index, e)}
                    className={`w-2 h-2 rounded-full transition-colors duration-200 ${
                      index === currentImageIndex 
                        ? 'bg-white' 
                        : 'bg-white/50 hover:bg-white/75'
                    }`}
                    aria-label={`Go to image ${index + 1}`}
                  />
                ))}
              </div>
            </>
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

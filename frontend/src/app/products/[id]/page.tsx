'use client';
import { Product } from '@/types/product';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { ShoppingCart, Tag, Star, Package, Leaf, CheckCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState, useEffect, use } from 'react';

type ProductDetailPageProps = {
  params: Promise<{ id: string }>;
};

const getProductById = async (id: string): Promise<Product | null> => {
  try {
    const params = new URLSearchParams();
    params.append('ids', id);
    const baseUrl = process.env.NODE_ENV === 'production' 
      ? 'https://beingawarematters.com:8000' 
      : 'http://localhost:8000';
    const response = await fetch(`${baseUrl}/api/products?${params.toString()}`);
    if (!response.ok) {
      console.error('Error fetching product:', response);
      return null;
    }
    
    const products: Product[] = await response.json();
    // Return the first element as requested
    return products.length > 0 ? products[0] : null;
  } catch (error) {
    console.error('Error fetching product:', error);
    return null;
  }
};

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const resolvedParams = use(params);
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Get product images from the specified paths
  const getProductImages = (productId: string): string[] => {
    return [
      `/products/${productId}/1.png`,
      `/products/${productId}/2.png`
    ];
  };

  const productImages = product ? getProductImages(product.product_id) : [];

  const nextImage = () => {
    setCurrentImageIndex((prev) => 
      prev === productImages.length - 1 ? 0 : prev + 1
    );
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => 
      prev === 0 ? productImages.length - 1 : prev - 1
    );
  };

  const goToImage = (index: number) => {
    setCurrentImageIndex(index);
  };

  useEffect(() => {
    const fetchProduct = async () => {
      const fetchedProduct = await getProductById(resolvedParams.id);
      setProduct(fetchedProduct);
      setLoading(false);
    };

    fetchProduct();
  }, [resolvedParams.id]);

  if (loading) {
    return (
      <div className="container mx-auto py-12 px-4">
        <div className="bg-white shadow-xl rounded-lg overflow-hidden md:flex animate-pulse">
          <div className="md:w-1/2 h-[384px] bg-gray-200"></div>
          <div className="md:w-1/2 p-8">
            <div className="h-[16px] bg-gray-200 rounded mb-4"></div>
            <div className="h-[32px] bg-gray-200 rounded mb-4"></div>
            <div className="h-[80px] bg-gray-200 rounded mb-6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    console.log('Product not found');
    console.log('Product ID:', resolvedParams.id);
    notFound();
  }

  return (
    <div className="container mx-auto py-12 px-4">
      <div className="bg-white shadow-xl rounded-lg overflow-hidden md:flex">
        {/* Product Image Carousel Section */}
        <div className="md:w-1/2 relative h-[384px] md:h-auto group">
          <div className="relative w-full h-full bg-gradient-to-br  min-h-[300px] from-gray-100 to-gray-200 overflow-hidden">
            <Image
              src={productImages[currentImageIndex]}
              alt={`${product.name} - Image ${currentImageIndex + 1}`}
              fill
              style={{ objectFit: 'cover' }}
              className="transition-transform duration-500 hover:scale-[1.05] min-h-[300px]"
              onError={(e) => {
                // Fallback to product.imageUrl if carousel image fails
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
                  className="absolute left-[10px] top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 z-20 shadow-lg backdrop-blur-sm"
                  aria-label="Previous image"
                >
                  <ChevronLeft size={18} />
                </button>
                <button
                  onClick={nextImage}
                  className="absolute right-[10px] top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 z-20 shadow-lg backdrop-blur-sm"
                  aria-label="Next image"
                >
                  <ChevronRight size={18} />
                </button>
                
                {/* Dot indicators */}
                <div className="absolute bottom-[10px] left-1/2 transform -translate-x-1/2 flex space-x-2 transition-opacity duration-200">
                  {productImages.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => goToImage(index)}
                      className={`w-2.5 h-2.5 rounded-full transition-all duration-200 shadow-sm ${
                        index === currentImageIndex 
                          ? 'bg-white scale-110' 
                          : 'bg-white/60 hover:bg-white/80 hover:scale-105'
                      }`}
                      aria-label={`Go to image ${index + 1}`}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Product Details Section */}
        <div className="md:w-1/2 p-8">
          <p className="text-sm text-pink-500 uppercase tracking-wider mb-1 flex items-center">
            <Tag size={16} className="mr-2" /> {product.category}
          </p>
          <h1 className="text-4xl font-bold text-gray-800 mb-4">{product.name}</h1>

          <p className="text-gray-600 leading-relaxed mb-6">{product.description}</p>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2 flex items-center">
              <Leaf size={20} className="mr-2 text-green-500" /> Top Ingredients
            </h3>
            <ul className="list-disc list-inside text-gray-600 space-y-1">
              {product.top_ingredients.split('; ').map((ingredient, index) => (
                <li key={index}>{ingredient}</li>
              ))}
            </ul>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2 flex items-center">
              <Star size={20} className="mr-2 text-yellow-500" /> Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {product.tags.split('|').map((tag, index) => (
                <span key={index} className="bg-pink-100 text-pink-700 px-[10px] py-[5px] rounded-full text-sm">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between mb-8">
            <p className="text-3xl font-extrabold text-pink-600">${product.priceusd.toFixed(2)}</p>
          </div>

          <button className="w-full bg-pink-500 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:bg-pink-600 transition duration-300 flex items-center justify-center text-lg">
            <ShoppingCart size={22} className="mr-2" /> Add to Cart (Dummy)
          </button>

          <div className="mt-6 text-sm text-gray-500">
            <p className="flex items-center"><CheckCircle size={16} className="mr-2 text-green-500" /> Product ID: {product.product_id}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Optional: Create a not-found.tsx file in the app directory or products/[id] directory
// for a custom "not found" UI.
// Example: frontend/src/app/products/[id]/not-found.tsx
/*
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="text-center py-10">
      <h2 className="text-2xl font-bold">Product Not Found</h2>
      <p>Sorry, we couldn't find the product you were looking for.</p>
      <Link href="/" className="text-blue-500 hover:underline mt-4 inline-block">
        Go back to Home
      </Link>
    </div>
  )
}
*/

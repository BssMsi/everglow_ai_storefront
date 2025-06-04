// frontend/src/app/products/[id]/page.tsx
import { dummyProducts } from '@/data/dummyProducts'; // Adjust path as necessary
import { Product } from '@/types/product';         // Adjust path as necessary
import Image from 'next/image';
import { notFound } from 'next/navigation'; // For handling product not found
import { ShoppingCart, Tag, Star, Package, Leaf, CheckCircle } from 'lucide-react'; // Icons

// This function can be used if you want to generate static paths at build time
// For now, we'll rely on dynamic rendering.
// export async function generateStaticParams() {
//   return dummyProducts.map((product) => ({
//     id: product.id,
//   }));
// }

type ProductDetailPageProps = {
  params: { id: string };
};

const getProductById = (id: string): Product | undefined => {
  return dummyProducts.find((product) => product.id === id);
};

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const product = getProductById(params.id);

  if (!product) {
    notFound(); // Triggers the not-found page or component
  }

  return (
    <div className="container mx-auto py-12 px-4">
      <div className="bg-white shadow-xl rounded-lg overflow-hidden md:flex">
        {/* Product Image Section */}
        <div className="md:w-1/2 relative min-h-[300px] md:min-h-full">
          {product.imageUrl && (
            <Image
              src={product.imageUrl}
              alt={product.name}
              layout="fill"
              objectFit="cover"
              className="transition-transform duration-500 hover:scale-105"
            />
          )}
          {!product.imageUrl && (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
              <Package size={64} className="text-gray-400" />
            </div>
          )}
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
              {product.top_ingredients.map((ingredient, index) => (
                <li key={index}>{ingredient}</li>
              ))}
            </ul>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2 flex items-center">
              <Star size={20} className="mr-2 text-yellow-500" /> Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {product.tags.map((tag, index) => (
                <span key={index} className="bg-pink-100 text-pink-700 px-3 py-1 rounded-full text-sm">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between mb-8">
            <p className="text-3xl font-extrabold text-pink-600">${product.price.toFixed(2)}</p>
            {/* Margin is usually not displayed to customers
            <p className="text-sm text-gray-500">Margin: {product.margin}</p>
            */}
          </div>

          <button className="w-full bg-pink-500 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:bg-pink-600 transition duration-300 flex items-center justify-center text-lg">
            <ShoppingCart size={22} className="mr-2" /> Add to Cart (Dummy)
          </button>

          <div className="mt-6 text-sm text-gray-500">
            <p className="flex items-center"><CheckCircle size={16} className="mr-2 text-green-500" /> Product ID: {product.id}</p>
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

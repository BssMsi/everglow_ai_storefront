// frontend/src/app/page.tsx
import SearchBar from '@/components/search/SearchBar';
import ProductList from '@/components/products/ProductList';
import { dummyProducts } from '@/data/dummyProducts'; // Make sure this path is correct

export default function HomePage() {
  return (
    <div>
      {/* Welcome message or hero section can be added here */}
      <div className="text-center my-8">
        <h1 className="text-4xl font-bold text-pink-600 mb-2">Welcome to EverGlow</h1>
        <p className="text-lg text-gray-600">Discover your natural radiance with our vegan skincare.</p>
      </div>

      <SearchBar />
      <ProductList initialProducts={dummyProducts} />
    </div>
  );
}

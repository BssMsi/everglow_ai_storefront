// frontend/src/types/product.ts
export interface Product {
  product_id: string;
  name: string;
  category: string;
  description: string;
  top_ingredients: string[];
  tags: string[];
  priceusd: number;
  margin: number; // For sorting
  imageUrl?: string; // Optional image
}

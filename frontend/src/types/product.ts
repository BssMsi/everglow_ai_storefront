// frontend/src/types/product.ts
export interface Product {
  id: string;
  name: string;
  category: string;
  description: string;
  top_ingredients: string[];
  tags: string[];
  price: number;
  margin: number; // For sorting
  imageUrl?: string; // Optional image
}

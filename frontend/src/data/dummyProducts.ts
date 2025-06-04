// frontend/src/data/dummyProducts.ts
import { Product } from '@/types/product';

export const dummyProducts: Product[] = [
  {
    id: '1',
    name: 'Radiant Glow Serum',
    category: 'Serums',
    description: 'A powerful vegan serum to boost your skin\'s natural radiance.',
    top_ingredients: ['Vitamin C', 'Hyaluronic Acid', 'Rosehip Oil'],
    tags: ['vegan', 'glow', 'brightening', 'serum'],
    price: 45.00,
    margin: 0.6, // Higher margin
    imageUrl: 'https://via.placeholder.com/300x300.png?text=Radiant+Glow+Serum',
  },
  {
    id: '2',
    name: 'Pure Hydration Moisturizer',
    category: 'Moisturizers',
    description: 'Deeply hydrating moisturizer for all skin types, 100% vegan.',
    top_ingredients: ['Aloe Vera', 'Shea Butter', 'Jojoba Oil'],
    tags: ['vegan', 'hydration', 'moisturizer', 'daily'],
    price: 35.00,
    margin: 0.5,
    imageUrl: 'https://via.placeholder.com/300x300.png?text=Pure+Hydration',
  },
  {
    id: '3',
    name: 'Gentle Cleansing Foam',
    category: 'Cleansers',
    description: 'A soft, gentle foam that cleanses without stripping moisture.',
    top_ingredients: ['Chamomile Extract', 'Green Tea', 'Cucumber Extract'],
    tags: ['vegan', 'gentle', 'cleanser', 'foam'],
    price: 25.00,
    margin: 0.55,
    imageUrl: 'https://via.placeholder.com/300x300.png?text=Gentle+Cleanser',
  },
   {
    id: '4',
    name: 'Overnight Renewal Cream',
    category: 'Creams',
    description: 'Works overnight to repair and renew your skin.',
    top_ingredients: ['Retinol (plant-derived)', 'Peptides', 'Avocado Oil'],
    tags: ['vegan', 'renewal', 'night cream', 'anti-aging'],
    price: 55.00,
    margin: 0.65, // Highest margin
    imageUrl: 'https://via.placeholder.com/300x300.png?text=Renewal+Cream',
  },
];

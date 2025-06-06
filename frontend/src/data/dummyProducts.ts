// frontend/src/data/dummyProducts.ts
import { Product } from '@/types/product';

export const dummyProducts: Product[] = [
  {
    product_id: '1',
    name: 'Radiant Glow Serum',
    category: 'Serums',
    description: 'A powerful vegan serum to boost your skin\'s natural radiance.',
    top_ingredients: ['Vitamin C', 'Hyaluronic Acid', 'Rosehip Oil'],
    tags: ['vegan', 'glow', 'brightening', 'serum'],
    priceusd: 45.00,
    margin: 0.6, // Higher margin
    imageUrl: 'https://picsum.photos/seed/picsum/200/350',
  },
  {
    product_id: '2',
    name: 'Pure Hydration Moisturizer',
    category: 'Moisturizers',
    description: 'Deeply hydrating moisturizer for all skin types, 100% vegan.',
    top_ingredients: ['Aloe Vera', 'Shea Butter', 'Jojoba Oil'],
    tags: ['vegan', 'hydration', 'moisturizer', 'daily'],
    priceusd: 35.00,
    margin: 0.5,
    imageUrl: 'https://picsum.photos/seed/picsum/200/360',
  },
  {
    product_id: '3',
    name: 'Gentle Cleansing Foam',
    category: 'Cleansers',
    description: 'A soft, gentle foam that cleanses without stripping moisture.',
    top_ingredients: ['Chamomile Extract', 'Green Tea', 'Cucumber Extract'],
    tags: ['vegan', 'gentle', 'cleanser', 'foam'],
    priceusd: 25.00,
    margin: 0.55,
    imageUrl: 'https://picsum.photos/seed/picsum/200/370',
  },
   {
    product_id: '4',
    name: 'Overnight Renewal Cream',
    category: 'Creams',
    description: 'Works overnight to repair and renew your skin.',
    top_ingredients: ['Retinol (plant-derived)', 'Peptides', 'Avocado Oil'],
    tags: ['vegan', 'renewal', 'night cream', 'anti-aging'],
    priceusd: 55.00,
    margin: 0.65, // Highest margin
    imageUrl: 'https://picsum.photos/seed/picsum/200/380',
  },
];

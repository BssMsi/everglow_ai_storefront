# EverGlow AI Storefront (Frontend)

## Project Overview
EverGlow is a 100% vegan skincare brand. This Proof of Concept (PoC) demonstrates an AI-driven storefront with an Adaptive UI: every page and component can be personalized to each customer. The font, color scheme, and other UI variables are stored centrally and can be changed dynamically based on customer profile or behavior.

## Motivation: Adaptive UI by Modularization & Context
- **Adaptive UI**: The app uses a global Theme Context to manage color schemes and fonts as CSS variables. When a customer updates their profile (e.g., preferred color or font), the entire UI adapts instantly.
- **Modularization**: All UI elements (header, footer, search, products, etc.) are built as independent, reusable components. Theme logic is centralized in `src/context/ThemeContext.tsx`.
- **Context-Driven**: The customer profile (editable on the Profile page) drives the UI's look and feel. All theme changes are propagated via React context and CSS variables for maximum flexibility.

## Folder Structure
```
frontend/
  ├── src/
  │   ├── app/         # Next.js app directory (pages: main, about, profile, product detail)
  │   ├── components/  # Modular UI components (layout, products, search, etc.)
  │   ├── context/     # ThemeContext for adaptive UI
  │   └── types/       # TypeScript types for products, profile, theme
  ├── public/          # Static assets
  ├── package.json     # Project dependencies
  └── ...
```

## Key Features
- **Fixed Header & Footer**: Always visible, styled using theme variables.
- **Main Page**: Expandable search bar (with voice/AI agent placeholder), dynamic product list sorted by margin.
- **About Page**: Brand philosophy and team (static content).
- **Product Detail Page**: Shows all product attributes, dummy add-to-cart button.

## Adaptive UI Implementation
- **ThemeContext** (`src/context/ThemeContext.tsx`):
  - Stores and updates color scheme & font as CSS variables.
  - Exposes available themes and fonts for easy extension.
  - All components use these variables for consistent, adaptive styling.
- **Profile-Driven Adaptation**: Changing profile preferences updates the UI in real time.
- **Modular Components**: Each UI piece is a separate component, making it easy to extend or replace.

## Getting Started
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```
3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## How to Extend
- **Add a new color scheme or font**: Update `ThemeContext.tsx` and `profile.ts` types.
- **Add new adaptive attributes**: Extend the `CustomerProfile` type and update the context logic.
- **Add new UI components**: Place them in `src/components/` and use theme variables for styling.

## Next Steps / TODO
- Add customer interaction analytics to further personalize the UI.
- Revolutionize UI: Modern, animated, adaptive components

---

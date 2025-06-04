// frontend/src/context/ThemeContext.tsx
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { CustomerProfile, ThemeSettings } from '@/types/profile';

const defaultThemeSettings: ThemeSettings = {
  colorScheme: 'default',
  fontFamily: "'Inter', sans-serif", // Default font from layout
};

// Define CSS variables for themes
const themes: Record<CustomerProfile['preferredColorScheme'], Record<string, string>> = {
  default: {
    '--color-primary': '#EC4899', // Pink-500 (example)
    '--color-secondary': '#D1D5DB', // Gray-300
    '--color-text': '#1F2937', // Gray-800
    '--color-background': '#FFFFFF', // White
    '--font-family': "'Inter', sans-serif",
  },
  rose: {
    '--color-primary': '#F43F5E', // Rose-500
    '--color-secondary': '#FECDD3', // Rose-200
    '--color-text': '#881337', // Rose-900
    '--color-background': '#FFF1F2', // Rose-50
    '--font-family': "'Inter', sans-serif", // Default font, can be overridden by font preference
  },
  teal: {
    '--color-primary': '#14B8A6', // Teal-500
    '--color-secondary': '#99F6E4', // Teal-200
    '--color-text': '#0F766E', // Teal-700
    '--color-background': '#F0FDFA', // Teal-50
    '--font-family': "'Inter', sans-serif",
  },
  lavender: {
    '--color-primary': '#8B5CF6', // Violet-500
    '--color-secondary': '#DDD6FE', // Violet-200
    '--color-text': '#5B21B6', // Violet-700
    '--color-background': '#F5F3FF', // Violet-50
    '--font-family': "'Inter', sans-serif",
  }
};

const fonts: Record<CustomerProfile['preferredFont'], string> = {
  inter: "'Inter', sans-serif",
  roboto: "'Roboto', sans-serif",
  lato: "'Lato', sans-serif",
};

interface ThemeContextType {
  themeSettings: ThemeSettings;
  setThemeSettings: (settings: Partial<CustomerProfile>) => void;
  availableColorSchemes: CustomerProfile['preferredColorScheme'][];
  availableFonts: CustomerProfile['preferredFont'][];
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [themeSettings, setThemeState] = useState<ThemeSettings>(defaultThemeSettings);

  useEffect(() => {
    const root = document.documentElement;
    const selectedScheme = themes[themeSettings.colorScheme] || themes.default;

    // Apply color scheme variables
    Object.entries(selectedScheme).forEach(([key, value]) => {
      if (key !== '--font-family') { // Font family is handled separately
         root.style.setProperty(key, value);
      }
    });

    // Apply font family
    root.style.setProperty('--font-family', themeSettings.fontFamily);
    document.body.style.fontFamily = themeSettings.fontFamily;

  }, [themeSettings]);

  const handleSetThemeSettings = (newProfileSettings: Partial<CustomerProfile>) => {
    setThemeState(prev => {
      const newColorScheme = newProfileSettings.preferredColorScheme || prev.colorScheme;
      const newFontKey = newProfileSettings.preferredFont ||
                         (Object.keys(fonts) as CustomerProfile['preferredFont'][])
                           .find(key => fonts[key] === prev.fontFamily) ||
                         'inter';

      return {
        colorScheme: newColorScheme,
        fontFamily: fonts[newFontKey],
      };
    });
  };

  const availableColorSchemes = Object.keys(themes) as CustomerProfile['preferredColorScheme'][];
  const availableFonts = Object.keys(fonts) as CustomerProfile['preferredFont'][];

  return (
    <ThemeContext.Provider value={{ themeSettings, setThemeSettings: handleSetThemeSettings, availableColorSchemes, availableFonts }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// frontend/src/context/ThemeContext.tsx
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { CustomerProfile, ThemeSettings } from '@/types/profile';

const defaultThemeSettings: ThemeSettings = {
  colorScheme: 'dark',
  fontFamily: "'Inter', sans-serif",
};

// Define CSS variables for themes with all needed variables including logo color
const themes: Record<CustomerProfile['preferredColorScheme'], Record<string, string>> = {
  default: {
    '--color-primary': '#EC4899',
    '--color-secondary': '#D1D5DB',
    '--color-text': '#1F2937',
    '--color-background': '#FFFFFF',
    '--color-accent-dark': '#9CA3AF',
    '--color-foreground': '#1F2937',
    '--color-muted': '#F3F4F6',
    '--color-logo': '#EC4899', // Logo color matches primary
    '--font-family': "'Inter', sans-serif",
  },
  dark: {
    '--color-primary': '#3B82F6',
    '--color-secondary': '#1E293B',
    '--color-text': '#FFFFFF',
    '--color-background': '#0F172A',
    '--color-accent-dark': '#334155',
    '--color-foreground': '#F8FAFC',
    '--color-muted': '#475569',
    '--color-logo': '#3B82F6', // Blue logo for dark theme
    '--font-family': "'Inter', sans-serif",
  },
  rose: {
    '--color-primary': '#F43F5E',
    '--color-secondary': '#FECDD3',
    '--color-text': '#881337',
    '--color-background': '#FFF1F2',
    '--color-accent-dark': '#FB7185',
    '--color-foreground': '#881337',
    '--color-muted': '#FDF2F8',
    '--color-logo': '#F43F5E', // Rose logo
    '--font-family': "'Inter', sans-serif",
  },
  teal: {
    '--color-primary': '#14B8A6',
    '--color-secondary': '#99F6E4',
    '--color-text': '#0F766E',
    '--color-background': '#F0FDFA',
    '--color-accent-dark': '#5EEAD4',
    '--color-foreground': '#0F766E',
    '--color-muted': '#CCFBF1',
    '--color-logo': '#14B8A6', // Teal logo
    '--font-family': "'Inter', sans-serif",
  },
  lavender: {
    '--color-primary': '#8B5CF6',
    '--color-secondary': '#DDD6FE',
    '--color-text': '#5B21B6',
    '--color-background': '#F5F3FF',
    '--color-accent-dark': '#C4B5FD',
    '--color-foreground': '#5B21B6',
    '--color-muted': '#EDE9FE',
    '--color-logo': '#8B5CF6', // Lavender logo
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

// Update the type definition in profile.ts to include 'dark'

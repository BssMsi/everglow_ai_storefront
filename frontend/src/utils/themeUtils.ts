import { CustomerProfile } from '@/types/profile';

// Available themes from your ThemeContext
const AVAILABLE_THEMES: CustomerProfile['preferredColorScheme'][] = [
  'default',
  'dark', 
  'rose',
  'teal',
  'lavender'
];

/**
 * Utility function to change the theme from anywhere in the application
 * @param theme - The theme to apply, or null to randomly select one
 * @param setThemeSettings - The setThemeSettings function from useTheme hook
 */
export const changeTheme = (
  theme: CustomerProfile['preferredColorScheme'] | null,
  setThemeSettings: (settings: Partial<CustomerProfile>) => void
) => {
  let selectedTheme: CustomerProfile['preferredColorScheme'];
  
  if (theme === null) {
    // Randomly select a theme
    const randomIndex = Math.floor(Math.random() * AVAILABLE_THEMES.length);
    selectedTheme = AVAILABLE_THEMES[randomIndex];
  } else {
    // Validate the provided theme
    if (!AVAILABLE_THEMES.includes(theme)) {
      console.warn(`Invalid theme '${theme}'. Available themes:`, AVAILABLE_THEMES);
      return;
    }
    selectedTheme = theme;
  }
  
  // Apply the theme
  setThemeSettings({ preferredColorScheme: selectedTheme });
  
  console.log(`Theme changed to: ${selectedTheme}`);
};

/**
 * Get all available themes
 * @returns Array of available theme names
 */
export const getAvailableThemes = (): CustomerProfile['preferredColorScheme'][] => {
  return [...AVAILABLE_THEMES];
};

/**
 * Get a random theme
 * @returns A randomly selected theme name
 */
export const getRandomTheme = (): CustomerProfile['preferredColorScheme'] => {
  const randomIndex = Math.floor(Math.random() * AVAILABLE_THEMES.length);
  return AVAILABLE_THEMES[randomIndex];
};
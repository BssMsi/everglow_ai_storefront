// frontend/src/types/profile.ts
export interface CustomerProfile {
  name: string;
  email: string;
  preferredColorScheme: 'default' | 'rose' | 'teal' | 'lavender';
  preferredFont: 'inter' | 'roboto' | 'lato';
  // Add other preference-related attributes here
}

export interface ThemeSettings {
  colorScheme: CustomerProfile['preferredColorScheme'];
  fontFamily: string; // Will store the CSS font-family string
}

// frontend/src/app/profile/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { CustomerProfile } from '@/types/profile';
import { Palette, Type, UserCircle, Mail } from 'lucide-react';

// This fonts object should ideally be imported from ThemeContext or a shared constants file
const pageFonts: Record<CustomerProfile['preferredFont'], string> = {
  inter: "'Inter', sans-serif",
  roboto: "'Roboto', sans-serif",
  lato: "'Lato', sans-serif",
};

export default function ProfilePage() {
  const { themeSettings, setThemeSettings, availableColorSchemes, availableFonts } = useTheme();

  const [formState, setFormState] = useState<Partial<CustomerProfile>>({
    name: 'Jane Doe', // Dummy data
    email: 'jane.doe@example.com', // Dummy data
    preferredColorScheme: themeSettings.colorScheme,
    preferredFont: (Object.keys(pageFonts) as CustomerProfile['preferredFont'][])
                      .find(key => pageFonts[key] === themeSettings.fontFamily) || 'inter',
  });

  useEffect(() => {
    setFormState(prev => ({
      ...prev,
      preferredColorScheme: themeSettings.colorScheme,
      preferredFont: (Object.keys(pageFonts) as CustomerProfile['preferredFont'][])
                        .find(key => pageFonts[key] === themeSettings.fontFamily) || 'inter',
    }));
  }, [themeSettings]);


  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prevState => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Profile settings submitted:', formState);
    setThemeSettings(formState);
    alert('Profile and theme settings updated!');
  };

  return (
    <div className="py-8 px-4 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-center text-primary">Customer Profile & Preferences</h1>

      <form onSubmit={handleSubmit} className="bg-white shadow-xl rounded-lg p-8 space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            <UserCircle size={16} className="inline mr-1" /> Name
          </label>
          <input
            type="text"
            name="name"
            id="name"
            value={formState.name || ''}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            <Mail size={16} className="inline mr-1" /> Email
          </label>
          <input
            type="email"
            name="email"
            id="email"
            value={formState.email || ''}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
          />
        </div>

        <hr className="my-6 border-primary"/>

        <div>
          <label htmlFor="preferredColorScheme" className="block text-sm font-medium text-gray-700 mb-1">
            <Palette size={16} className="inline mr-1" /> Preferred Color Scheme
          </label>
          <select
            name="preferredColorScheme"
            id="preferredColorScheme"
            value={formState.preferredColorScheme}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
          >
            {availableColorSchemes.map(scheme => (
              <option key={scheme} value={scheme} className="capitalize">
                {scheme.charAt(0).toUpperCase() + scheme.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="preferredFont" className="block text-sm font-medium text-gray-700 mb-1">
            <Type size={16} className="inline mr-1" /> Preferred Font
          </label>
          <select
            name="preferredFont"
            id="preferredFont"
            value={formState.preferredFont}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
          >
            {availableFonts.map(font => (
              <option key={font} value={font} className="capitalize">
                {font.charAt(0).toUpperCase() + font.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="w-full button-primary text-white font-semibold py-2 px-4 rounded-md hover:opacity-90 transition duration-150"
        >
          Save Profile & Apply Theme
        </button>
      </form>
    </div>
  );
}

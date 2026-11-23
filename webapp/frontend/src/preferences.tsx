import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { ar } from './data/ar';

export type Language = 'en' | 'ar';
export type Theme = 'light' | 'dark';

interface Preferences {
  language: Language;
  setLanguage: (language: Language) => void;
  theme: Theme;
  toggleTheme: () => void;
  t: (text: string) => string;
  locale: string;
}

const Context = createContext<Preferences | null>(null);

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Graceful fallback
  }
}

export interface PreferencesProviderProps {
  readonly children: ReactNode;
}

export function PreferencesProvider({ children }: Readonly<PreferencesProviderProps>) {
  const [language, setLanguage] = useState<Language>(() => {
    const saved = read('honest_lang') || read('honest:language');
    return saved === 'ar' ? 'ar' : 'en';
  });

  const [theme, setTheme] = useState<Theme>(() => {
    const saved = read('honest_theme') || read('honest:theme');
    return saved === 'dark' || saved === 'light' ? (saved as Theme) : 'light';
  });

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    write('honest_lang', language);
    write('honest:language', language);
  }, [language]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.dataset.theme = theme;
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);
    document.documentElement.style.colorScheme = theme;
    const themeMeta = document.querySelector('meta[name="theme-color"]');
    if (themeMeta) {
      themeMeta.setAttribute('content', theme === 'dark' ? '#0a0e17' : '#f8faf9');
    }
    write('honest_theme', theme);
    write('honest:theme', theme);
  }, [theme]);

  const value = useMemo<Preferences>(
    () => ({
      language,
      setLanguage,
      theme,
      toggleTheme: () => setTheme((old) => (old === 'dark' ? 'light' : 'dark')),
      t: (text: string) => (language === 'ar' ? ar[text] || text : text),
      locale: language === 'ar' ? 'ar-EG' : 'en-US'
    }),
    [language, theme]
  );

  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function usePreferences(): Preferences {
  const context = useContext(Context);
  if (!context) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return context;
}

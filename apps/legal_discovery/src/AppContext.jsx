import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [settings, setSettings] = useState({});
  const [session, setSession] = useState(null);
  const [featureFlags, setFeatureFlags] = useState({});
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => (t === 'dark' ? 'light' : 'dark'));

  const value = useMemo(
    () => ({ settings, setSettings, session, setSession, featureFlags, setFeatureFlags, theme, toggleTheme }),
    [settings, session, featureFlags, theme]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export const useAppContext = () => useContext(AppContext);


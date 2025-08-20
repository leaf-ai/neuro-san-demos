import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [settings, setSettings] = useState({});
  const [session, setSession] = useState(null);
  const [featureFlags, setFeatureFlags] = useState({});
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.body.classList.remove('light', 'dark');
    document.body.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    fetch('/api/settings')
      .then(r => r.json())
      .then(data => {
        setSettings(data);
        if (data.theme) setTheme(data.theme);
      })
      .catch(() => {});
    fetch('/api/feature-flags')
      .then(r => r.json())
      .then(setFeatureFlags)
      .catch(() => {});
  }, []);

  const toggleTheme = () => setTheme(t => (t === 'dark' ? 'light' : 'dark'));

  const value = useMemo(
    () => ({
      settings,
      setSettings,
      session,
      setSession,
      featureFlags,
      setFeatureFlags,
      theme,
      setTheme,
      toggleTheme,
    }),
    [settings, session, featureFlags, theme]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export const useAppContext = () => useContext(AppContext);


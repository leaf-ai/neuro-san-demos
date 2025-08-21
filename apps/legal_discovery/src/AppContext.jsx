import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';

const AppContext = createContext();

export function AppProvider({ children }) {
  const themes = ['dark', 'light', 'ocean', 'forest', 'rose'];
  const [settings, setSettings] = useState({});
  const [session, setSession] = useState(null);
  const [featureFlags, setFeatureFlags] = useState({});
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.body.classList.remove(...themes);
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

  const toggleTheme = () =>
    setTheme(t => {
      const idx = themes.indexOf(t);
      return themes[(idx + 1) % themes.length];
    });

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
      themes,
    }),
    [settings, session, featureFlags, theme]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export const useAppContext = () => useContext(AppContext);


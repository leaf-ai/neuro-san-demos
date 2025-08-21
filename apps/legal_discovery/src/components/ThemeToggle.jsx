import React from 'react';
import { useAppContext } from '../AppContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useAppContext();
  const icons = { dark: 'moon', light: 'sun', ocean: 'water', forest: 'leaf', rose: 'heart' };
  return (
    <button onClick={toggleTheme} className="tab-button" aria-label="Toggle theme">
      <i className={`fa fa-${icons[theme] || 'palette'}`}></i>
    </button>
  );
}

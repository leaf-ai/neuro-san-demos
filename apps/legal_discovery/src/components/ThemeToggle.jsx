import React from 'react';
import { useAppContext } from '../AppContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useAppContext();
  return (
    <button onClick={toggleTheme} className="tab-button" aria-label="Toggle theme">
      <i className={`fa fa-${theme === 'dark' ? 'sun' : 'moon'}`}></i>
    </button>
  );
}

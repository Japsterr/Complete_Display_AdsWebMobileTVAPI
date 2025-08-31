import { useEffect, useState } from 'react';

// Feature flag via Vite env: VITE_ENABLE_THEME_TOGGLE=true
const ENABLED = import.meta.env.VITE_ENABLE_THEME_TOGGLE !== 'false';
const STORAGE_KEY = 'ui_theme';
type Theme = 'dark' | 'light';

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.dataset.theme = theme; // allows CSS [data-theme="dark"] selectors
  if (theme === 'dark') {
    root.classList.add('theme-dark');
    root.classList.remove('theme-light');
  } else {
    root.classList.add('theme-light');
    root.classList.remove('theme-dark');
  }
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem(STORAGE_KEY) as Theme) || 'dark');

  useEffect(() => {
    if (!ENABLED) return; // rollback path: do nothing if disabled
    applyTheme(theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  if (!ENABLED) return null; // feature disabled -> hides toggle entirely

  const next = theme === 'dark' ? 'light' : 'dark';

  return (
    <button
      aria-label="Toggle theme"
      type="button"
      onClick={() => setTheme(next)}
      style={{
        background: 'linear-gradient(135deg,#ff6b35,#ff925f)',
        color: '#1a1b1e',
        border: 'none',
        padding: '6px 12px',
        borderRadius: 6,
        fontSize: 12,
        cursor: 'pointer'
      }}
    >
      {theme === 'dark' ? 'Light' : 'Dark'} Mode
    </button>
  );
}

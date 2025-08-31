import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, beforeEach } from 'vitest';
import { renderApp } from '../../test/renderWithRouter';

describe('ThemeToggle', () => {
  beforeEach(() => {
    // ensure feature enabled for test environment
    (import.meta as any).env = { ...(import.meta as any).env, VITE_ENABLE_THEME_TOGGLE: 'true' };
    document.documentElement.className = '';
    delete document.documentElement.dataset.theme;
    localStorage.removeItem('ui_theme');
  });

  it('toggles between dark and light modes', async () => {
    const user = userEvent.setup();
    renderApp({ route: '/dashboard', withAuth: true });
    const btn = await screen.findByRole('button', { name: /light mode|dark mode/i });
    const firstLabel = btn.textContent;
    await user.click(btn);
    // after click dataset theme should change
    const dataTheme = document.documentElement.dataset.theme;
    expect(dataTheme === 'dark' || dataTheme === 'light').toBe(true);
    expect(btn.textContent).not.toEqual(firstLabel);
  });
});

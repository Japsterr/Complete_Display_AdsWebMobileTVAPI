import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { renderApp } from '../../test/renderWithRouter';

describe('Auth pages', () => {
  it('renders login form', () => {
    renderApp({ route: '/login' });
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('renders register form', () => {
    renderApp({ route: '/register' });
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  it('redirects protected page to login when no token', () => {
    renderApp({ route: '/dashboard' });
    // After redirect, login button visible
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });
});

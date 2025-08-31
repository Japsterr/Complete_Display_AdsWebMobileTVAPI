import { screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { renderApp } from '../../test/renderWithRouter';

// Dashboard routes to verify. Expect a keyword to appear. Adjust selectors as pages evolve.
const protectedCases: Array<[path: string, regex: RegExp]> = [
  ['/dashboard', /dashboard/i],
  ['/profile', /profile/i],
  ['/media', /media/i],
  ['/campaigns', /campaign/i],
  ['/displays', /display/i],
  ['/menus', /menu/i],
  ['/analytics', /analytics/i],
  ['/settings', /settings/i],
];

describe('Protected routes (authenticated)', () => {
  for (const [path, rx] of protectedCases) {
    it(`renders ${path}`, () => {
      renderApp({ route: path, withAuth: true });
      expect(screen.getByText(rx)).toBeInTheDocument();
    });
  }
});

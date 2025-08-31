import { screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { renderApp } from '../../test/renderWithRouter';

// NOTE: These are smoke tests verifying that each public route renders without auth.
// They assume the page components contain some identifying text.

const cases: Array<[path: string, expectedRegex: RegExp]> = [
  ['/', /mobile-first digital signage/i],
  ['/features', /features/i],
  ['/pricing', /pricing/i],
  ['/contact', /contact/i],
  ['/documentation', /documentation/i],
];

describe('Public routes', () => {
  for (const [path, expected] of cases) {
    it(`renders ${path}`, () => {
      renderApp({ route: path });
      // We only assert presence of a keyword; pages can later refine data-testid usage.
      const el = screen.getByText(expected);
      expect(el).toBeInTheDocument();
    });
  }
});

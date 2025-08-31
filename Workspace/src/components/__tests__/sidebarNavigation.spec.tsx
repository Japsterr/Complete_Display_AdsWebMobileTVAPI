import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { renderApp } from '../../test/renderWithRouter';

describe('Sidebar navigation', () => {
  it('navigates between main sections', async () => {
    const user = userEvent.setup();
    renderApp({ route: '/dashboard', withAuth: true });

    const targets = [
      { link: /profile/i, expect: /profile/i },
      { link: /media/i, expect: /media/i },
      { link: /campaigns/i, expect: /campaign/i },
      { link: /menus/i, expect: /menu/i },
      { link: /displays/i, expect: /display/i },
      { link: /analytics/i, expect: /analytics/i },
      { link: /settings/i, expect: /settings/i },
    ];

    for (const t of targets) {
      const navLink = screen.getByRole('link', { name: t.link });
      await user.click(navLink);
      expect(screen.getByText(t.expect)).toBeInTheDocument();
    }
  });
});

import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { renderApp } from '../../test/renderWithRouter';

describe('CampaignEditor interactions', () => {
  it('opens and closes media modal', async () => {
    renderApp({ route: '/campaigns/new', withAuth: true });
    const openBtn = screen.getByRole('button', { name: /open add media modal/i });
    await userEvent.click(openBtn);
    const modal = await screen.findByTestId('media-library-placeholder');
    expect(modal).toBeInTheDocument();
    const closeBtn = screen.getByRole('button', { name: /close media modal/i });
    await userEvent.click(closeBtn);
    // After close, placeholder should no longer be present (queryBy returns null)
    expect(screen.queryByTestId('media-library-placeholder')).toBeNull();
  });
});

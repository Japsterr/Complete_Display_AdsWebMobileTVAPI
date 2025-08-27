import { describe, it, expect, vi } from 'vitest';
import * as api from '../../services/api';

describe('reorderMenu helper', () => {
  it('calls API with correct payload', async () => {
    const postMock = vi.spyOn(api.default, 'post').mockResolvedValue({ data: { status: 'ok' } } as any);

    const categories = [{ category_id: 1, order: 0 }, { category_id: 2, order: 1 }];
    const items = [{ item_id: 10, category_id: 1, order: 0 }, { item_id: 11, category_id: 2, order: 1 }];

    const res = await api.reorderMenu(5, { categories, items } as any);

    expect(postMock).toHaveBeenCalledWith('/menus/5/reorder/', { categories, items });
    expect(res).toEqual({ status: 'ok' });

    postMock.mockRestore();
  });
});

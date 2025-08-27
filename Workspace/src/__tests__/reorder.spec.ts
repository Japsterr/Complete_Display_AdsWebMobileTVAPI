import { describe, it, expect, vi } from 'vitest';
import * as api from '../services/api';

describe('reorderMenu helper', () => {
  it('posts the correct payload to the reorder endpoint', async () => {
    const postSpy = vi.spyOn(api.default, 'post').mockResolvedValue({ data: { status: 'ok' } });

    const menuId = 42;
    const payload = {
      categories: [ { category_id: 1, order: 0 }, { category_id: 2, order: 1 } ],
      items: [ { item_id: 101, category_id: 1, order: 0 }, { item_id: 102, category_id: 2, order: 0 } ]
    };

    const res = await api.reorderMenu(menuId, payload);

    expect(postSpy).toHaveBeenCalledWith(`/menus/${menuId}/reorder/`, payload);
    expect(res).toEqual({ status: 'ok' });

    postSpy.mockRestore();
  });
});

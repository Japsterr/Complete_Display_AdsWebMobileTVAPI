import { http, HttpResponse } from 'msw';

// Simple in-memory stores for tests
let mediaAutoId = 1;
const media: any[] = [];
let campaigns: any[] = [
  { campaign_id: 1, name: 'Sample Campaign', description: 'Test', created_at: new Date().toISOString() }
];

export const handlers = [
  http.get('*/api/v1/media/', () => {
    return HttpResponse.json(media);
  }),
  http.post('*/api/v1/media/', async ({ request }) => {
    // For simplicity we don't parse multipart; just return stub
    const newObj = { id: mediaAutoId++, file_name: 'mock-file.png', duration: 10, media_type: 'image', thumbnail_url: '', url: '' };
    media.push(newObj);
    return HttpResponse.json(newObj, { status: 201 });
  }),
  http.get('*/api/v1/campaigns/', () => {
    return HttpResponse.json(campaigns);
  }),
  http.post('*/api/v1/campaigns/', async ({ request }) => {
    const body = await request.json();
    const newCampaign = { campaign_id: campaigns.length + 1, name: body.name, description: body.description || '', created_at: new Date().toISOString() };
    campaigns.push(newCampaign);
    return HttpResponse.json(newCampaign, { status: 201 });
  }),
  http.patch('*/api/v1/campaigns/:id/', async ({ params, request }) => {
    const id = Number(params.id);
    const body = await request.json();
    campaigns = campaigns.map(c => c.campaign_id === id ? { ...c, ...body } : c);
    const updated = campaigns.find(c => c.campaign_id === id);
    if (!updated) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
    return HttpResponse.json(updated);
  })
];

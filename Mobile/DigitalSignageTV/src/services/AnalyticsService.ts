import { API_BASE } from '../config';
import DeviceActivationService from './DeviceActivationService';

export interface HeartbeatPayload {
  device_id: string;
  status?: 'online' | 'offline';
  device_info?: Record<string, any>;
}

export interface ImpressionPayload {
  device_id: string;
  media_id: number;
  campaign_id: number;
  duration_shown: number;
  scheduled_duration: number;
  completed: boolean;
  sequence_number: number;
  total_media_in_campaign: number;
}

type QueueItem = { url: string; body: any };
const QUEUE_STORAGE_KEY = 'analytics_queue_v1';

async function loadQueue(): Promise<QueueItem[]> {
  try {
    const raw = await Promise.resolve(globalThis?.localStorage?.getItem?.(QUEUE_STORAGE_KEY));
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

async function saveQueue(q: QueueItem[]): Promise<void> {
  try {
    await Promise.resolve(globalThis?.localStorage?.setItem?.(QUEUE_STORAGE_KEY, JSON.stringify(q)));
  } catch {}
}

async function enqueue(item: QueueItem) {
  const q = await loadQueue();
  q.push(item);
  await saveQueue(q);
}

async function flushQueue() {
  const q = await loadQueue();
  if (q.length === 0) return;
  const remaining: QueueItem[] = [];
  for (const item of q) {
    try {
      await fetch(item.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.body),
      });
    } catch {
      remaining.push(item);
    }
  }
  await saveQueue(remaining);
}

class AnalyticsService {
  async sendHeartbeat(extra?: Partial<HeartbeatPayload>): Promise<void> {
    const device_id = DeviceActivationService.getDeviceId();
    try {
      await fetch(`${API_BASE}/analytics/heartbeat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id, status: 'online', ...extra }),
      });
      // best-effort flush queued events if any
      flushQueue();
    } catch (e) {
      await enqueue({ url: `${API_BASE}/analytics/heartbeat/`, body: { device_id, status: 'online', ...extra } });
    }
  }

  async recordImpression(payload: ImpressionPayload): Promise<void> {
    try {
      await fetch(`${API_BASE}/analytics/impression/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      flushQueue();
    } catch (e) {
      await enqueue({ url: `${API_BASE}/analytics/impression/`, body: payload });
    }
  }
}

export default new AnalyticsService();

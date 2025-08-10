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

class AnalyticsService {
  async sendHeartbeat(extra?: Partial<HeartbeatPayload>): Promise<void> {
    const device_id = DeviceActivationService.getDeviceId();
    try {
      await fetch(`${API_BASE}/analytics/heartbeat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id, status: 'online', ...extra }),
      });
    } catch (e) {
      // ignore network errors; will retry on next tick
    }
  }

  async recordImpression(payload: ImpressionPayload): Promise<void> {
    try {
      await fetch(`${API_BASE}/analytics/impression/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (e) {
      // ignore
    }
  }
}

export default new AnalyticsService();

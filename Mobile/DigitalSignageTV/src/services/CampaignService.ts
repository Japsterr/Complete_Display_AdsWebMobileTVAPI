import DeviceActivationService from './DeviceActivationService';
import ConfigService from './ConfigService';

interface MediaItem {
  media_id: number;
  file_path: string;
  media_type: 'image' | 'video';
  duration: number;
  name: string;
}

interface Campaign {
  campaign_id: number;
  name: string;
  media_items: MediaItem[];
  is_active: boolean;
  normalize_to_orientation?: 'none' | 'portrait' | 'landscape';
}

interface CampaignResponse {
  campaign: number;
  campaign_name?: string;
  normalize_to_orientation?: 'none' | 'portrait' | 'landscape';
  schedule?: any;
  media_items?: MediaItem[];
}

class CampaignService {
  /**
   * Get the current campaign for this device
   */
  async getCurrentCampaign(): Promise<Campaign | null> {
    const deviceId = DeviceActivationService.getDeviceId();
    const base = await ConfigService.getApiBase();
  const response = await fetch(`${base}/devices/current-campaign/?device_id=${deviceId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        // No campaign assigned
        return null;
      }
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get campaign');
    }

    const data: CampaignResponse = await response.json();
    
    // Transform the response to our Campaign interface
    return {
      campaign_id: data.campaign,
      name: data.campaign_name || `Campaign ${data.campaign}`,
      media_items: data.media_items || [],
      is_active: true,
      normalize_to_orientation: data.normalize_to_orientation || 'none',
    };
  }

  /**
   * Get media URL for a media item
   */
  async getMediaUrlAsync(mediaItem: MediaItem): Promise<string> {
    // If server already returned a full URL, use it as-is
    if (mediaItem.file_path.startsWith('http://') || mediaItem.file_path.startsWith('https://')) {
      return mediaItem.file_path;
    }
    // Otherwise, construct from API_BASE root
    const base = await ConfigService.getApiBase();
    const root = base.replace('/api/v1', '');
    return `${root}${mediaItem.file_path.startsWith('/') ? '' : '/'}${mediaItem.file_path}`;
  }

  /**
   * Poll for campaign updates
   */
  startPollingCampaign(
    onCampaignUpdate: (campaign: Campaign | null) => void,
    onError: (error: Error) => void,
    intervalMs: number = 30000 // Check every 30 seconds
  ): () => void {
    const interval = setInterval(async () => {
      try {
        const campaign = await this.getCurrentCampaign();
        onCampaignUpdate(campaign);
      } catch (error) {
        onError(error instanceof Error ? error : new Error('Unknown error'));
      }
    }, intervalMs);

    // Return stop function
    return () => clearInterval(interval);
  }
}

export default new CampaignService();
export type { Campaign, MediaItem };

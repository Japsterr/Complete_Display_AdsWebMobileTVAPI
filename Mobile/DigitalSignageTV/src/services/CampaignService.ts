import DeviceActivationService from './DeviceActivationService';

// Configuration
const BASE_URL = 'http://127.0.0.1:8000/api/v1';

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
}

interface CampaignResponse {
  campaign: number;
  schedule?: any;
  media_items?: MediaItem[];
}

class CampaignService {
  /**
   * Get the current campaign for this device
   */
  async getCurrentCampaign(): Promise<Campaign | null> {
    const deviceId = DeviceActivationService.getDeviceId();
    
    const response = await fetch(`${BASE_URL}/devices/current-campaign/?device_id=${deviceId}`, {
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
      name: `Campaign ${data.campaign}`,
      media_items: data.media_items || [],
      is_active: true,
    };
  }

  /**
   * Get media URL for a media item
   */
  getMediaUrl(mediaItem: MediaItem): string {
    // Construct full URL for media file
    return `${BASE_URL.replace('/api/v1', '')}${mediaItem.file_path}`;
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

import DeviceInfo from 'react-native-device-info';
import ConfigService from './ConfigService';

interface ActivationResponse {
  activation_code: string;
  status: string;
  message: string;
}

interface ActivationStatusResponse {
  status: string;
  activated: boolean;
  display_name?: string;
  location?: string;
  activation_code?: string;
  message: string;
}

interface DeviceInfo {
  brand: string;
  model: string;
  systemVersion: string;
  appVersion: string;
  buildNumber: string;
}

class DeviceActivationService {
  private deviceId: string | null = null;
  private deviceInfo: DeviceInfo | null = null;

  /**
   * Initialize device information
   */
  async initialize(): Promise<void> {
    try {
      this.deviceId = await DeviceInfo.getUniqueId();
      
      this.deviceInfo = {
        brand: await DeviceInfo.getBrand(),
        model: await DeviceInfo.getModel(),
        systemVersion: await DeviceInfo.getSystemVersion(),
        appVersion: await DeviceInfo.getVersion(),
        buildNumber: await DeviceInfo.getBuildNumber(),
      };
      
      console.log('Device initialized:', {
        deviceId: this.deviceId,
        deviceInfo: this.deviceInfo
      });
    } catch (error) {
      console.error('Failed to initialize device info:', error);
      // Fallback device ID
      this.deviceId = `TV-${Date.now()}`;
      this.deviceInfo = {
        brand: 'Unknown',
        model: 'Unknown',
        systemVersion: 'Unknown',
        appVersion: '1.0.0',
        buildNumber: '1',
      };
    }
  }

  /**
   * Get device ID
   */
  getDeviceId(): string {
    if (!this.deviceId) {
      throw new Error('Device not initialized. Call initialize() first.');
    }
    return this.deviceId;
  }

  /**
   * Request activation code from backend
   */
  async requestActivationCode(): Promise<ActivationResponse> {
    if (!this.deviceId || !this.deviceInfo) {
      throw new Error('Device not initialized. Call initialize() first.');
    }

  const base = await ConfigService.getApiBase();
  const response = await fetch(`${base}/devices/request-activation/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        device_id: this.deviceId,
        device_info: this.deviceInfo,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to request activation code');
    }

    return await response.json();
  }

  /**
   * Check activation status
   */
  async checkActivationStatus(): Promise<ActivationStatusResponse> {
    if (!this.deviceId) {
      throw new Error('Device not initialized. Call initialize() first.');
    }

  const base = await ConfigService.getApiBase();
  const response = await fetch(`${base}/devices/check-activation/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        device_id: this.deviceId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to check activation status');
    }

    return await response.json();
  }

  /**
   * Poll for activation status every few seconds
   */
  startPollingActivation(
    onActivated: (data: ActivationStatusResponse) => void,
    onError: (error: Error) => void,
    intervalMs: number = 5000
  ): () => void {
    const interval = setInterval(async () => {
      try {
        const status = await this.checkActivationStatus();
        if (status.activated) {
          clearInterval(interval);
          onActivated(status);
        }
      } catch (error) {
        onError(error instanceof Error ? error : new Error('Unknown error'));
      }
    }, intervalMs);

    // Return stop function
    return () => clearInterval(interval);
  }
}

export default new DeviceActivationService();

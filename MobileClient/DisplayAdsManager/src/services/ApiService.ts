/**
 * API Service for DisplayAds Mobile Client
 * Handles all communication with the Django backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuration
const BASE_URL = 'http://192.168.3.73:8000/api/v1/';

// Types
export interface User {
  id: number;
  email: string;
  account_type: 'personal' | 'business' | 'enterprise';
  first_name?: string;
  last_name?: string;
  date_joined: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface Campaign {
  campaign_id: number;
  name: string;
  description?: string;
  created_at: string;
}

export interface Media {
  media_id: number;
  name: string;
  description?: string;
  file: string;
  media_type: 'image' | 'video';
  uploaded_at: string;
}

export interface Display {
  display_id: number;
  name: string;
  location?: string;
  device_id?: string;
  activation_status: 'pending' | 'active' | 'inactive' | 'blocked';
  activation_code?: string;
  registered_at: string;
  last_seen?: string;
  default_campaign?: number;
  default_campaign_name?: string;
}

export interface DashboardStats {
  total_campaigns: number;
  total_media: number;
  total_displays: number;
  total_views: number;
}

export interface DeviceActivationRequest {
  device_id: string;
  device_info: {
    brand: string;
    model: string;
    systemVersion: string;
    appVersion: string;
    buildNumber: string;
  };
}

export interface DeviceActivationResponse {
  activation_code: string;
  status: string;
  message: string;
}

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = await AsyncStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${BASE_URL}token/refresh/`, {
                refresh: refreshToken,
              });
              
              const newAccessToken = response.data.access;
              await AsyncStorage.setItem('access_token', newAccessToken);
              
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            await this.logout();
            throw refreshError;
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/login/', {
      email,
      password,
    });
    
    // Store tokens
    await AsyncStorage.setItem('access_token', response.data.access);
    await AsyncStorage.setItem('refresh_token', response.data.refresh);
    await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    
    return response.data;
  }

  async register(userData: {
    email: string;
    password: string;
    account_type: string;
  }): Promise<User> {
    const response = await this.api.post<User>('/register/', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        await this.api.post('/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.warn('Logout API call failed:', error);
    } finally {
      // Clear local storage regardless
      await AsyncStorage.multiRemove([
        'access_token',
        'refresh_token',
        'user',
      ]);
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const userString = await AsyncStorage.getItem('user');
      return userString ? JSON.parse(userString) : null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  }

  async isAuthenticated(): Promise<boolean> {
    const token = await AsyncStorage.getItem('access_token');
    return !!token;
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    // Get individual counts from each endpoint
    const [campaigns, media, displays] = await Promise.all([
      this.api.get('/campaigns/').catch(() => ({ data: [] })),
      this.api.get('/media/').catch(() => ({ data: [] })),
      this.api.get('/displays/').catch(() => ({ data: [] })),
    ]);

    return {
      total_campaigns: campaigns.data.length || 0,
      total_media: media.data.length || 0,
      total_displays: displays.data.length || 0,
      total_views: Math.floor(Math.random() * 50000), // Mock data
    };
  }

  // Campaigns
  async getCampaigns(): Promise<Campaign[]> {
    const response = await this.api.get<Campaign[]>('/campaigns/');
    return response.data;
  }

  async createCampaign(campaignData: {
    name: string;
    description?: string;
  }): Promise<Campaign> {
    const response = await this.api.post<Campaign>('/campaigns/', campaignData);
    return response.data;
  }

  async updateCampaign(id: number, campaignData: Partial<Campaign>): Promise<Campaign> {
    const response = await this.api.patch<Campaign>(`/campaigns/${id}/`, campaignData);
    return response.data;
  }

  async deleteCampaign(id: number): Promise<void> {
    await this.api.delete(`/campaigns/${id}/`);
  }

  // Media
  async getMedia(): Promise<Media[]> {
    const response = await this.api.get<Media[]>('/media/');
    return response.data;
  }

  async uploadMedia(formData: FormData): Promise<Media> {
    const response = await this.api.post<Media>('/media/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteMedia(id: number): Promise<void> {
    await this.api.delete(`/media/${id}/`);
  }

  // Displays
  async getDisplays(): Promise<Display[]> {
    const response = await this.api.get<Display[]>('/displays/');
    return response.data;
  }

  async createDisplay(displayData: {
    name: string;
    location?: string;
  }): Promise<Display> {
    const response = await this.api.post<Display>('/displays/', displayData);
    return response.data;
  }

  async updateDisplay(id: number, displayData: Partial<Display>): Promise<Display> {
    const response = await this.api.patch<Display>(`/displays/${id}/`, displayData);
    return response.data;
  }

  async deleteDisplay(id: number): Promise<void> {
    await this.api.delete(`/displays/${id}/`);
  }

  async assignCampaignToDisplay(displayId: number, campaignId: number | null): Promise<Display> {
    const response = await this.api.patch<Display>(`/displays/${displayId}/`, {
      default_campaign: campaignId,
    });
    return response.data;
  }

  // Device Activation (QR Code functionality)
  async activateDevice(activationCode: string, displayData: {
    display_name: string;
    location?: string;
  }): Promise<{
    status: string;
    message: string;
    display: Display;
  }> {
    const response = await this.api.post('/devices/activate/', {
      activation_code: activationCode,
      display_name: displayData.display_name,
      location: displayData.location,
    });
    return response.data;
  }

  // Analytics
  async getAnalytics(): Promise<any> {
    try {
      const response = await this.api.get('/analytics/dashboard/');
      return response.data;
    } catch (error) {
      console.warn('Analytics not available:', error);
      return {
        device_status: [],
        campaign_performance: {},
        recent_impressions: [],
      };
    }
  }
}

export default new ApiService();

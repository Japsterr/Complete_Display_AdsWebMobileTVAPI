import axios from "axios";
import type { AxiosInstance } from "axios";

const api: AxiosInstance = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1/",
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  res => res,
  async error => {
    // For now, don't auto-refresh tokens to avoid login loops
    if (error.response && error.response.status === 401) {
      // Only redirect if we're not already on the login page
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface Campaign {
  campaign_id: number;  // Changed from id to campaign_id to match the model
  name: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface Display {
  display_id: number;  // This is the primary key
  name: string;
  location?: string;
  device_id: string;
  activation_status: string;
  registered_at: string;
  activated_at?: string;
  last_seen?: string;
  default_campaign?: number;
  default_campaign_name?: string;
}

// Campaign API functions
export const fetchCampaigns = async (): Promise<Campaign[]> => {
  const response = await api.get('/campaigns/');
  return response.data.results || response.data;
};

export const assignCampaignToDisplay = async (displayId: number, campaignId: number): Promise<Display> => {
  console.log('Assigning campaign', campaignId, 'to display', displayId);
  const response = await api.patch(`/displays/${displayId}/`, {
    default_campaign: campaignId === 0 ? null : campaignId
  });
  console.log('Assignment response:', response.data);
  return response.data;
};

export const fetchDisplays = async (): Promise<Display[]> => {
  const response = await api.get('/displays/');
  console.log('Displays API response:', response.data);
  return response.data.results || response.data;
};

export const registerDisplay = async (displayData: {
  name: string;
  location: string;
  device_id: string;
}): Promise<Display> => {
  const response = await api.post('/displays/', displayData);
  return response.data;
};

export default api;

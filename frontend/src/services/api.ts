import axios from 'axios';
import { 
  MarketsResponse, 
  TicksResponse, 
  Stats, 
  SubscribeResponse, 
  UnsubscribeResponse 
} from '../types/api';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// API service class
export class ApiService {
  // Get account balance and statistics
  static async getStats(): Promise<Stats> {
    const response = await api.get<Stats>('/stats');
    return response.data;
  }

  // Get available markets
  static async getMarkets(): Promise<MarketsResponse> {
    const response = await api.get<MarketsResponse>('/markets');
    return response.data;
  }

  // Subscribe to tick updates
  static async subscribeToTicks(symbol: string): Promise<SubscribeResponse> {
    const response = await api.post<SubscribeResponse>('/subscribe', { symbol });
    return response.data;
  }

  // Unsubscribe from tick updates
  static async unsubscribeFromTicks(): Promise<UnsubscribeResponse> {
    const response = await api.post<UnsubscribeResponse>('/unsubscribe', {});
    return response.data;
  }

  // Get latest ticks
  static async getTicks(): Promise<TicksResponse> {
    const response = await api.get<TicksResponse>('/ticks');
    return response.data;
  }

  // Health check
  static async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await api.get('/health');
    return response.data;
  }

  // Debug ticks
  static async getDebugTicks(): Promise<any> {
    const response = await api.get('/debug/ticks');
    return response.data;
  }

  // Settings methods
  static async getSettings(): Promise<{ settings: Record<string, any> }> {
    const response = await api.get('/settings');
    return response.data;
  }

  static async getSetting(key: string): Promise<{ key: string; value: any }> {
    const response = await api.get(`/settings/${key}`);
    return response.data;
  }

  static async updateSetting(key: string, value: any): Promise<{ key: string; value: any; message: string }> {
    const response = await api.put(`/settings/${key}`, { value });
    return response.data;
  }

  static async createSetting(key: string, value: any, description?: string): Promise<{ key: string; value: any; message: string }> {
    const response = await api.post('/settings', { key, value, description });
    return response.data;
  }

  static async deleteSetting(key: string): Promise<{ message: string }> {
    const response = await api.delete(`/settings/${key}`);
    return response.data;
  }

  // Subscription management methods
  static async getSubscriptionStatus(): Promise<any> {
    const response = await api.get('/subscription/status');
    return response.data;
  }

  static async cleanupSubscription(): Promise<any> {
    const response = await api.post('/subscription/cleanup');
    return response.data;
  }

  // Debug methods
  static async testTelegramNotification(): Promise<{ message: string; test_data: any }> {
    const response = await api.post('/debug/test-telegram');
    return response.data;
  }

  static async testSSE(): Promise<{ message: string; test_data: any }> {
    const response = await api.post('/debug/test-sse');
    return response.data;
  }
}

export default api;

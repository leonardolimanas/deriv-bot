import { 
  Market, 
  Strategy, 
  StrategyInfo, 
  TradeHistory, 
  OverallStats,
  CreateStrategyRequest,
  CreateTradeRequest,
  ProcessTickRequest,
  TickResult
} from '../types/trading';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

class TradingApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/api/trading`;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Markets
  async getMarkets(): Promise<Market[]> {
    return this.request<Market[]>('/markets');
  }

  // Strategies
  async createStrategy(data: CreateStrategyRequest): Promise<Strategy> {
    return this.request<Strategy>('/strategies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getStrategies(): Promise<Strategy[]> {
    return this.request<Strategy[]>('/strategies');
  }

  async getActiveStrategies(): Promise<Record<string, StrategyInfo>> {
    return this.request<Record<string, StrategyInfo>>('/strategies/active');
  }

  async getStrategy(strategyId: string): Promise<StrategyInfo> {
    return this.request<StrategyInfo>(`/strategies/${strategyId}`);
  }

  async resetStrategy(strategyId: string): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>(`/strategies/${strategyId}/reset`, {
      method: 'POST',
    });
  }

  async cancelTrades(strategyId: string): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>(`/strategies/${strategyId}/cancel`, {
      method: 'POST',
    });
  }

  async updateStrategy(strategyId: string, data: CreateStrategyRequest): Promise<Strategy> {
    return this.request<Strategy>(`/strategies/${strategyId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteStrategy(strategyId: string): Promise<void> {
    return this.request<void>(`/strategies/${strategyId}`, {
      method: 'DELETE',
    });
  }

  // Trades
  async createTrade(strategyId: string, data: CreateTradeRequest): Promise<any> {
    return this.request(`/strategies/${strategyId}/trades`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async processTick(strategyId: string, data: ProcessTickRequest): Promise<TickResult> {
    return this.request<TickResult>(`/strategies/${strategyId}/ticks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // History and Stats
  async getTradeHistory(strategyId?: string, limit: number = 100): Promise<TradeHistory[]> {
    const params = new URLSearchParams();
    if (strategyId) params.append('strategy_id', strategyId);
    if (limit) params.append('limit', limit.toString());
    
    return this.request<TradeHistory[]>(`/history?${params.toString()}`);
  }

  async getOverallStats(): Promise<OverallStats> {
    return this.request<OverallStats>('/stats');
  }
}

export const tradingApi = new TradingApiService();

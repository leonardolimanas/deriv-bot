export interface Market {
  symbol: string;
  display_name: string;
  market: string;
  has_tick_stream: boolean;
  // Additional market information
  submarket?: string;
  exchange?: string;
  market_display_name?: string;
  submarket_display_name?: string;
  // Trading information
  pip?: number;
  pip_size?: number;
  min_contract_size?: number;
  max_contract_size?: number;
  min_stake?: number;
  max_stake?: number;
  // Price information
  spot?: number;
  spot_time?: number;
  // Product information
  product_type?: string;
  product_id?: number;
  contract_type?: string;
}

export interface Tick {
  timestamp: number;
  quote: number;
  bid: number;
  ask: number;
  status?: string;
  message?: string;
}

export interface Stats {
  balance: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface MarketsResponse {
  markets: Market[];
}

export interface TicksResponse {
  ticks: Tick[];
  available: boolean;
}

export interface SubscribeResponse {
  status: 'subscribed' | 'error';
  message?: string;
}

export interface UnsubscribeResponse {
  status: 'unsubscribed' | 'error';
  message?: string;
}

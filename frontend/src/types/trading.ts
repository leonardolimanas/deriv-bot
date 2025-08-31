// Trading Types

export interface Market {
  id: string;
  name: string;
  description: string;
  type: 'forex' | 'synthetic';
}

export interface Strategy {
  id?: number;
  strategy_id: string;
  name?: string;
  description?: string;
  trigger_count: number;
  max_entries: number;
  base_amount: number;
  martingale_multiplier: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface StrategyInfo {
  strategy_id: string;
  stats: StrategyStats;
  active_trades: ActiveTrade[];
  current_sequence: number[];
}

export interface StrategyStats {
  total_profit: number;
  total_trades: number;
  winning_trades: number;
  win_rate: number;
  active_trades: number;
  current_sequence: number[];
  max_entries: number;
  base_amount: number;
  martingale_multiplier: number;
}

export interface ActiveTrade {
  id: string;
  bet_type: 'even' | 'odd';
  amount: number;
  entry_time: string;
  status: 'pending' | 'win' | 'loss' | 'cancelled';
}

export interface TradeResult {
  trade_id: string;
  status: 'win' | 'loss' | 'new_entry';
  result?: number;
  profit?: number;
  bet_type?: 'even' | 'odd';
  amount?: number;
  entry_number?: number;
}

export interface TickResult {
  strategy_id: string;
  tick_value: number;
  trigger_info?: TriggerInfo;
  trade_results: TradeResult[];
  active_trades: number;
  stats: StrategyStats;
}

export interface TriggerInfo {
  trigger_type: 'even_sequence' | 'odd_sequence';
  suggested_bet: 'even' | 'odd';
  sequence: number[];
  reason: string;
}

export interface TradeHistory {
  strategy_id: string;
  timestamp: string;
  trade_id: string;
  status: 'win' | 'loss';
  result: number;
  profit: number;
  bet_type: 'even' | 'odd';
  amount: number;
}

export interface OverallStats {
  total_profit: number;
  total_trades: number;
  total_wins: number;
  total_active_trades: number;
  overall_win_rate: number;
  total_strategies: number;
}

export interface CreateStrategyRequest {
  name?: string;
  description?: string;
  trigger_count: number;
  max_entries: number;
  base_amount: number;
  martingale_multiplier: number;
  is_active?: boolean;
}

export interface CreateTradeRequest {
  bet_type: 'even' | 'odd';
  amount?: number;
}

export interface ProcessTickRequest {
  tick_value: number;
}

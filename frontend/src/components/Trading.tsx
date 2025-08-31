import React, { useState, useEffect } from 'react';
import { tradingApi } from '../services/tradingApi';
import { Market, StrategyInfo, TradeHistory, OverallStats } from '../types/trading';

const Trading: React.FC = () => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [strategies, setStrategies] = useState<Record<string, StrategyInfo>>({});
  const [selectedMarket, setSelectedMarket] = useState<string>('');
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [overallStats, setOverallStats] = useState<OverallStats | null>(null);
  const [tradeHistory, setTradeHistory] = useState<TradeHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const [tradeForm, setTradeForm] = useState({
    bet_type: 'even' as 'even' | 'odd',
    amount: 1.0
  });

  const [tickValue, setTickValue] = useState<number>(0);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError('');

      const [marketsData, strategiesData, statsData] = await Promise.all([
        tradingApi.getMarkets(),
        tradingApi.getActiveStrategies(),
        tradingApi.getOverallStats()
      ]);

      setMarkets(marketsData);
      setStrategies(strategiesData);
      setOverallStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados iniciais');
    } finally {
      setLoading(false);
    }
  };



  const createTrade = async () => {
    if (!selectedStrategy) {
      setError('Selecione uma estratégia primeiro');
      return;
    }

    try {
      setLoading(true);
      setError('');

      await tradingApi.createTrade(selectedStrategy, tradeForm);
      
      // Reload strategy info
      const strategyInfo = await tradingApi.getStrategy(selectedStrategy);
      setStrategies(prev => ({ 
        ...prev, 
        [selectedStrategy]: strategyInfo
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar trade');
    } finally {
      setLoading(false);
    }
  };

  const processTick = async () => {
    if (!selectedStrategy) {
      setError('Selecione uma estratégia primeiro');
      return;
    }

    try {
      setLoading(true);
      setError('');

      await tradingApi.processTick(selectedStrategy, { tick_value: tickValue });
      
      // Reload strategy info
      const strategyInfo = await tradingApi.getStrategy(selectedStrategy);
      setStrategies(prev => ({ 
        ...prev, 
        [selectedStrategy]: strategyInfo
      }));

      // Reload overall stats
      const stats = await tradingApi.getOverallStats();
      setOverallStats(stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar tick');
    } finally {
      setLoading(false);
    }
  };

  const resetStrategy = async () => {
    if (!selectedStrategy) {
      setError('Selecione uma estratégia primeiro');
      return;
    }

    try {
      setLoading(true);
      setError('');

      await tradingApi.resetStrategy(selectedStrategy);
      
      // Reload strategy info
      const strategyInfo = await tradingApi.getStrategy(selectedStrategy);
      setStrategies(prev => ({ 
        ...prev, 
        [selectedStrategy]: strategyInfo
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao resetar estratégia');
    } finally {
      setLoading(false);
    }
  };

  const cancelTrades = async () => {
    if (!selectedStrategy) {
      setError('Selecione uma estratégia primeiro');
      return;
    }

    try {
      setLoading(true);
      setError('');

      await tradingApi.cancelTrades(selectedStrategy);
      
      // Reload strategy info
      const strategyInfo = await tradingApi.getStrategy(selectedStrategy);
      setStrategies(prev => ({ 
        ...prev, 
        [selectedStrategy]: strategyInfo
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao cancelar trades');
    } finally {
      setLoading(false);
    }
  };

  const loadTradeHistory = async () => {
    try {
      setLoading(true);
      const history = await tradingApi.getTradeHistory(selectedStrategy || undefined);
      setTradeHistory(history);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar histórico');
    } finally {
      setLoading(false);
    }
  };

  const selectedStrategyInfo = selectedStrategy ? strategies[selectedStrategy] : null;

  return (
    <div className="min-vh-100 bg-dark">
      <div className="container-fluid py-4">
        <div className="row">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h2 className="text-white mb-0">
                <i className="fas fa-chart-line me-2"></i>
                Sistema de Trading
              </h2>
              <div className="d-flex gap-2">
                <button 
                  className="btn btn-outline-light btn-sm"
                  onClick={loadInitialData}
                  disabled={loading}
                >
                  <i className="fas fa-sync-alt me-1"></i>
                  {loading ? 'Atualizando...' : 'Atualizar'}
                </button>
              </div>
            </div>

            {error && (
              <div className="alert alert-danger alert-dismissible fade show" role="alert">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {error}
                <button type="button" className="btn-close" onClick={() => setError('')}></button>
              </div>
            )}

            <div className="row">
              {/* Left Column - Configuration */}
              <div className="col-lg-6">
                <div className="row g-3">
                  {/* Market Selection */}
                  <div className="col-12">
                    <div className="card bg-dark-light border-0">
                      <div className="card-header bg-transparent border-0">
                        <h5 className="text-white mb-0">
                          <i className="fas fa-globe me-2"></i>
                          Seleção de Mercado
                        </h5>
                      </div>
                      <div className="card-body">
                        <select
                          value={selectedMarket}
                          onChange={(e) => setSelectedMarket(e.target.value)}
                          className="form-select bg-dark text-white border-secondary"
                        >
                          <option value="">Selecione um mercado</option>
                          {markets.map((market) => (
                            <option key={market.id} value={market.id}>
                              {market.name} - {market.description}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>



                  {/* Strategy Selection */}
                  <div className="col-12">
                    <div className="card bg-dark-light border-0">
                      <div className="card-header bg-transparent border-0">
                        <h5 className="text-white mb-0">
                          <i className="fas fa-list me-2"></i>
                          Selecionar Estratégia
                        </h5>
                      </div>
                      <div className="card-body">
                        <select
                          value={selectedStrategy}
                          onChange={(e) => setSelectedStrategy(e.target.value)}
                          className="form-select bg-dark text-white border-secondary"
                        >
                          <option value="">Selecione uma estratégia</option>
                          {Object.keys(strategies).map((strategyId) => (
                            <option key={strategyId} value={strategyId}>
                              {strategyId}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Trade Creation */}
                  <div className="col-12">
                    <div className="card bg-dark-light border-0">
                      <div className="card-header bg-transparent border-0">
                        <h5 className="text-white mb-0">
                          <i className="fas fa-handshake me-2"></i>
                          Criar Trade
                        </h5>
                      </div>
                      <div className="card-body">
                        <div className="row g-3">
                          <div className="col-md-6">
                            <label className="form-label text-white">Tipo de Aposta</label>
                            <select
                              value={tradeForm.bet_type}
                              onChange={(e) => setTradeForm(prev => ({ ...prev, bet_type: e.target.value as 'even' | 'odd' }))}
                              className="form-select bg-dark text-white border-secondary"
                            >
                              <option value="even">Even (Par)</option>
                              <option value="odd">Odd (Ímpar)</option>
                            </select>
                          </div>
                          <div className="col-md-6">
                            <label className="form-label text-white">Valor ($)</label>
                            <input
                              type="number"
                              step="0.01"
                              value={tradeForm.amount}
                              onChange={(e) => setTradeForm(prev => ({ ...prev, amount: parseFloat(e.target.value) }))}
                              className="form-control bg-dark text-white border-secondary"
                              min="0.01"
                            />
                          </div>
                          <div className="col-12">
                            <button
                              onClick={createTrade}
                              disabled={loading || !selectedStrategy}
                              className="btn btn-success w-100"
                            >
                              <i className="fas fa-plus me-2"></i>
                              {loading ? 'Criando...' : 'Criar Trade'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Tick Simulation */}
                  <div className="col-12">
                    <div className="card bg-dark-light border-0">
                      <div className="card-header bg-transparent border-0">
                        <h5 className="text-white mb-0">
                          <i className="fas fa-play me-2"></i>
                          Simular Tick
                        </h5>
                      </div>
                      <div className="card-body">
                        <div className="row g-3">
                          <div className="col-md-8">
                            <label className="form-label text-white">Valor do Tick (0-9)</label>
                            <input
                              type="number"
                              value={tickValue}
                              onChange={(e) => setTickValue(parseInt(e.target.value))}
                              className="form-control bg-dark text-white border-secondary"
                              min="0"
                              max="9"
                            />
                          </div>
                          <div className="col-md-4">
                            <label className="form-label">&nbsp;</label>
                            <button
                              onClick={processTick}
                              disabled={loading || !selectedStrategy}
                              className="btn btn-warning w-100"
                            >
                              <i className="fas fa-play me-2"></i>
                              {loading ? 'Processando...' : 'Processar Tick'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Strategy Actions */}
                  <div className="col-12">
                    <div className="card bg-dark-light border-0">
                      <div className="card-header bg-transparent border-0">
                        <h5 className="text-white mb-0">
                          <i className="fas fa-tools me-2"></i>
                          Ações da Estratégia
                        </h5>
                      </div>
                      <div className="card-body">
                        <div className="row g-2">
                          <div className="col-md-4">
                            <button
                              onClick={resetStrategy}
                              disabled={loading || !selectedStrategy}
                              className="btn btn-warning w-100"
                            >
                              <i className="fas fa-undo me-2"></i>
                              Resetar
                            </button>
                          </div>
                          <div className="col-md-4">
                            <button
                              onClick={cancelTrades}
                              disabled={loading || !selectedStrategy}
                              className="btn btn-danger w-100"
                            >
                              <i className="fas fa-times me-2"></i>
                              Cancelar
                            </button>
                          </div>
                          <div className="col-md-4">
                            <button
                              onClick={loadTradeHistory}
                              disabled={loading || !selectedStrategy}
                              className="btn btn-secondary w-100"
                            >
                              <i className="fas fa-history me-2"></i>
                              Histórico
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column - Information */}
              <div className="col-lg-6">
                <div className="row g-3">
                  {/* Overall Stats */}
                  {overallStats && (
                    <div className="col-12">
                      <div className="card bg-dark-light border-0">
                        <div className="card-header bg-transparent border-0">
                          <h5 className="text-white mb-0">
                            <i className="fas fa-chart-bar me-2"></i>
                            Estatísticas Gerais
                          </h5>
                        </div>
                        <div className="card-body">
                          <div className="row text-center">
                            <div className="col-6 mb-3">
                              <div className="h3 text-success mb-1">
                                ${overallStats.total_profit.toFixed(2)}
                              </div>
                              <small className="text-muted">Lucro Total</small>
                            </div>
                            <div className="col-6 mb-3">
                              <div className="h3 text-info mb-1">
                                {overallStats.total_trades}
                              </div>
                              <small className="text-muted">Total de Trades</small>
                            </div>
                            <div className="col-6">
                              <div className="h3 text-success mb-1">
                                {overallStats.overall_win_rate.toFixed(1)}%
                              </div>
                              <small className="text-muted">Taxa de Sucesso</small>
                            </div>
                            <div className="col-6">
                              <div className="h3 text-warning mb-1">
                                {overallStats.total_strategies}
                              </div>
                              <small className="text-muted">Estratégias Ativas</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Selected Strategy Info */}
                  {selectedStrategyInfo && (
                    <div className="col-12">
                      <div className="card bg-dark-light border-0">
                        <div className="card-header bg-transparent border-0">
                          <h5 className="text-white mb-0">
                            <i className="fas fa-info-circle me-2"></i>
                            Estratégia: {selectedStrategy}
                          </h5>
                        </div>
                        <div className="card-body">
                          <div className="row text-center mb-3">
                            <div className="col-6">
                              <div className="h4 text-success mb-1">
                                ${selectedStrategyInfo.stats.total_profit.toFixed(2)}
                              </div>
                              <small className="text-muted">Lucro</small>
                            </div>
                            <div className="col-6">
                              <div className="h4 text-info mb-1">
                                {selectedStrategyInfo.stats.win_rate.toFixed(1)}%
                              </div>
                              <small className="text-muted">Taxa de Sucesso</small>
                            </div>
                          </div>
                          <div className="row text-center mb-3">
                            <div className="col-4">
                              <div className="h5 text-white mb-1">{selectedStrategyInfo.stats.total_trades}</div>
                              <small className="text-muted">Total</small>
                            </div>
                            <div className="col-4">
                              <div className="h5 text-success mb-1">{selectedStrategyInfo.stats.winning_trades}</div>
                              <small className="text-muted">Vitórias</small>
                            </div>
                            <div className="col-4">
                              <div className="h5 text-danger mb-1">{selectedStrategyInfo.stats.total_trades - selectedStrategyInfo.stats.winning_trades}</div>
                              <small className="text-muted">Derrotas</small>
                            </div>
                          </div>
                          <div>
                            <small className="text-muted">Sequência Atual:</small>
                            <div className="d-flex gap-1 mt-2">
                              {selectedStrategyInfo.current_sequence.map((tick, index) => (
                                <div
                                  key={index}
                                  className={`rounded-circle d-flex align-items-center justify-content-center text-sm fw-bold ${
                                    tick % 2 === 0 ? 'bg-primary text-white' : 'bg-danger text-white'
                                  }`}
                                  style={{ width: '32px', height: '32px' }}
                                >
                                  {tick}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Active Trades */}
                  {selectedStrategyInfo && selectedStrategyInfo.active_trades.length > 0 && (
                    <div className="col-12">
                      <div className="card bg-dark-light border-0">
                        <div className="card-header bg-transparent border-0">
                          <h5 className="text-white mb-0">
                            <i className="fas fa-clock me-2"></i>
                            Trades Ativos
                          </h5>
                        </div>
                        <div className="card-body">
                          <div className="list-group list-group-flush bg-transparent">
                            {selectedStrategyInfo.active_trades.map((trade) => (
                              <div key={trade.id} className="list-group-item bg-transparent border-secondary d-flex justify-content-between align-items-center">
                                <div>
                                  <div className="text-white fw-bold">{trade.bet_type.toUpperCase()}</div>
                                  <div className="text-muted">${trade.amount.toFixed(2)}</div>
                                </div>
                                <div className="text-muted small">
                                  {new Date(trade.entry_time).toLocaleTimeString()}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Trade History */}
                  {tradeHistory.length > 0 && (
                    <div className="col-12">
                      <div className="card bg-dark-light border-0">
                        <div className="card-header bg-transparent border-0">
                          <h5 className="text-white mb-0">
                            <i className="fas fa-history me-2"></i>
                            Histórico de Trades
                          </h5>
                        </div>
                        <div className="card-body">
                          <div className="list-group list-group-flush bg-transparent" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                            {tradeHistory.map((trade) => (
                              <div key={trade.trade_id} className="list-group-item bg-transparent border-secondary d-flex justify-content-between align-items-center">
                                <div className="d-flex align-items-center gap-2">
                                  <div className={`rounded-circle ${
                                    trade.status === 'win' ? 'bg-success' : 'bg-danger'
                                  }`} style={{ width: '12px', height: '12px' }}></div>
                                  <span className="text-white fw-bold">{trade.bet_type.toUpperCase()}</span>
                                </div>
                                <div className="text-end">
                                  <div className={`fw-bold ${
                                    trade.profit > 0 ? 'text-success' : 'text-danger'
                                  }`}>
                                    ${trade.profit.toFixed(2)}
                                  </div>
                                  <div className="text-muted small">Resultado: {trade.result}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Trading;

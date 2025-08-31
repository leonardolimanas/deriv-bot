import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Toast, ToastContainer, Badge } from 'react-bootstrap';
import { MarketSelector } from './MarketSelector';
import { StreamControls } from './StreamControls';
import { TicksTable } from './TicksTable';
import { DebugPanel } from './DebugPanel';
import { Alert } from './Alert';
import { Footer } from './Footer';
import { ApiService } from '../services/api';
import { sseService } from '../services/sse';
import { Market, Tick } from '../types/api';
import { TrendingUp, TrendingDown, BarChart3, Activity, DollarSign } from 'lucide-react';

// Get decimal places for symbol
const getDecimalPlaces = (symbol: string) => {
  const symbolUpper = symbol?.toUpperCase();
  
  // Assets that need 4 decimal places
  const fourDecimalAssets = [
    'RDBEAR', 'RDBULL', 'R_25', 'R_50', 'R_75', 'R_10', 'R_20', 'R_30', 'R_40', 'R_60', 'R_70', 'R_80', 'R_90'
  ];
  
  // Assets that need 5 decimal places (some forex pairs)
  const fiveDecimalAssets = [
    'FRXEURUSD', 'FRXGBPUSD', 'FRXUSDJPY', 'FRXUSDCHF', 'FRXAUDUSD', 'FRXUSDCAD', 'FRXNZDUSD'
  ];
  
  // Assets that need 1 decimal place
  const oneDecimalAssets = [
    'WLDAUD', 'WLDEUR', 'WLDGBP', 'WLDUSD', 'WLDJPY', 'WLDCHF', 'WLDCAD', 'WLDAUD', 'WLDNZD'
  ];
  
  if (fourDecimalAssets.includes(symbolUpper)) {
    return 4;
  }
  
  if (fiveDecimalAssets.includes(symbolUpper)) {
    return 5;
  }
  
  if (oneDecimalAssets.includes(symbolUpper)) {
    return 1;
  }
  
  // Most assets use 2 decimal places
  return 2;
};

// Format price with correct decimal places
const formatPrice = (price: number, symbol?: string) => {
  const decimals = getDecimalPlaces(symbol || '');
  return price.toFixed(decimals);
};

// Current Tick Display Component
interface CurrentTickDisplayProps {
  currentTick: Tick;
  previousTick: Tick | null;
  selectedSymbol: string;
}

const CurrentTickDisplay: React.FC<CurrentTickDisplayProps> = ({ currentTick, previousTick, selectedSymbol }) => {
  const getTickBackgroundColor = () => {
    if (!previousTick) {
      return 'bg-white text-dark'; // First tick - white background with black text
    }
    
    if (currentTick.quote > previousTick.quote) {
      return 'bg-success text-white'; // Higher - green background
    } else if (currentTick.quote < previousTick.quote) {
      return 'bg-danger text-white'; // Lower - red background
    } else {
      return 'bg-white text-dark'; // Equal - white background with black text
    }
  };

  const getVariationIcon = () => {
    if (!previousTick) {
      return null; // No icon for first tick
    }
    
    if (currentTick.quote > previousTick.quote) {
      return <TrendingUp size={12} />; // Up arrow
    } else if (currentTick.quote < previousTick.quote) {
      return <TrendingDown size={12} />; // Down arrow
    } else {
      return null; // No icon for equal
    }
  };

  return (
    <div className={`p-2 rounded ${getTickBackgroundColor()}`}>
      <div className="d-flex align-items-center justify-content-center">
        <div className="d-flex align-items-center gap-1">
          {getVariationIcon()}
          <small className="fw-bold">
            {formatPrice(currentTick.quote, selectedSymbol)}
          </small>
        </div>
      </div>
    </div>
  );
};

interface DashboardProps {
  onStreamingChange: (isStreaming: boolean) => void;
  onBalanceChange: (balance: number | null) => void;
  onTicksCountChange: (count: number) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onStreamingChange, onBalanceChange, onTicksCountChange }) => {
  // State
  const [balance, setBalance] = useState<number | null>(null);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [selectedMarket, setSelectedMarket] = useState('');
  const [ticks, setTicks] = useState<Tick[]>([]);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isSubscribing, setIsSubscribing] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [alert, setAlert] = useState<{ message: string; type: 'success' | 'error' | 'warning' | 'info' } | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'warning' | 'info'; show: boolean } | null>(null);
  
  // Loading states
  const [isLoadingBalance, setIsLoadingBalance] = useState(true);
  const [isLoadingMarkets, setIsLoadingMarkets] = useState(true);

  // Settings state
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [showDebugPanel, setShowDebugPanel] = useState(true);

  // Polling intervals

  // Polling intervals
  const [ticksInterval] = useState<NodeJS.Timeout | null>(null);

  // SSE connection state
  const [isSSEConnected, setIsSSEConnected] = useState(false);

  // Load account balance
  const loadBalance = useCallback(async () => {
    try {
      const stats = await ApiService.getStats();
      setBalance(stats.balance);
      onBalanceChange(stats.balance);
    } catch (error) {
      console.error('Error loading balance:', error);
      showToast('Erro ao carregar saldo da conta', 'error');
    } finally {
      setIsLoadingBalance(false);
    }
  }, [onBalanceChange]);

  // Load markets
  const loadMarkets = useCallback(async () => {
    try {
      const response = await ApiService.getMarkets();
      setMarkets(response.markets);
    } catch (error) {
      console.error('Error loading markets:', error);
      showToast('Erro ao carregar mercados', 'error');
    } finally {
      setIsLoadingMarkets(false);
    }
  }, []);

  // Load settings
  const loadSettings = useCallback(async () => {
    try {
      const response = await ApiService.getSettings();
      setSettings(response.settings);
      setShowDebugPanel(response.settings.show_debug_panel || false);
      
      // Set default market if no market is selected
      if (!selectedMarket && response.settings.default_market) {
        setSelectedMarket(response.settings.default_market);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  }, [selectedMarket]);

  // Show toast notification
  const showToast = useCallback((message: string, type: 'success' | 'error' | 'warning' | 'info') => {
    setToast({ message, type, show: true });
  }, []);

  // Hide toast notification
  const hideToast = useCallback(() => {
    setToast(prev => prev ? { ...prev, show: false } : null);
  }, []);



  // Subscribe to ticks
  const handleSubscribe = useCallback(async () => {
    if (!selectedMarket) return;

    setIsSubscribing(true);
    try {
      const response = await ApiService.subscribeToTicks(selectedMarket);
      
      if (response.status === 'subscribed') {
        setIsSubscribed(true);
        setIsStreaming(true);
        showToast(`Inscrito com sucesso em ${selectedMarket}`, 'success');
        
        // Connect to SSE stream for real-time updates
        sseService.connect();
        setIsSSEConnected(true);
        
        // Set up SSE event listeners
        sseService.on('connected', (data) => {
          // SSE connected
        });
        
        sseService.on('tick_update', (data) => {
          if (data.ticks && data.ticks.length > 0) {
            setTicks(data.ticks);
            setIsStreaming(data.available);
            onStreamingChange(data.available);
            onTicksCountChange(data.ticks.length);
          }
        });
        
      } else {
        showToast(response.message || 'Erro ao inscrever', 'error');
      }
    } catch (error) {
      console.error('Error subscribing:', error);
      showToast('Erro ao inscrever. Tente novamente.', 'error');
    } finally {
      setIsSubscribing(false);
    }
  }, [selectedMarket, showToast, onStreamingChange, onTicksCountChange]);

  // Unsubscribe from ticks
  const handleUnsubscribe = useCallback(async () => {
    try {
      const response = await ApiService.unsubscribeFromTicks();
      
      if (response.status === 'unsubscribed') {
        setIsSubscribed(false);
        setIsStreaming(false);
        setTicks([]);
        showToast('Inscrição cancelada com sucesso', 'success');
        
        // Disconnect from SSE stream
        sseService.disconnect();
        setIsSSEConnected(false);
        
        // Clear SSE event listeners
        sseService.off('connected');
        sseService.off('tick_update');
      } else {
        showToast(response.message || 'Erro ao cancelar inscrição', 'error');
      }
    } catch (error) {
      console.error('Error unsubscribing:', error);
      showToast('Erro ao cancelar inscrição. Tente novamente.', 'error');
    }
  }, [showToast]);

  // Initialize dashboard
  useEffect(() => {
    loadBalance();
    loadMarkets();
    loadSettings();
    checkActiveSubscription();
    
    // Set up balance polling
    const interval = setInterval(() => {
      loadBalance();
    }, 5000);
    
    return () => {
      if (interval) clearInterval(interval);
      if (ticksInterval) clearInterval(ticksInterval);
      sseService.disconnect();
      cleanupOnUnload();
    };
  }, [loadBalance, loadMarkets, loadSettings]);

  // Check for active subscription on mount
  const checkActiveSubscription = useCallback(async () => {
    try {
      const status = await ApiService.getSubscriptionStatus();
      
      if (status.is_subscribed && status.current_symbol) {
        showToast(`Subscrição ativa encontrada: ${status.current_symbol}`, 'warning');
        
        // Set the current market
        setSelectedMarket(status.current_symbol);
        setIsSubscribed(true);
        setIsStreaming(status.tick_stream_available);
        
        // Connect to SSE
        sseService.connect();
        setIsSSEConnected(true);
        
        // Set up SSE event listeners
        sseService.on('connected', (data) => {
          // SSE connected
        });
        
        sseService.on('tick_update', (data) => {
          if (data.ticks && data.ticks.length > 0) {
            setTicks(data.ticks);
            setIsStreaming(data.available);
            onStreamingChange(data.available);
            onTicksCountChange(data.ticks.length);
          }
        });
      }
    } catch (error) {
      console.error('Error checking subscription status:', error);
    }
  }, [showToast, onStreamingChange, onTicksCountChange]);

  // Cleanup function for page unload
  const cleanupOnUnload = useCallback(async () => {
    try {
      await ApiService.cleanupSubscription();
    } catch (error) {
      console.error('Error cleaning up subscription:', error);
    }
  }, []);

  // Auto-hide toast after 5 seconds
  useEffect(() => {
    if (toast?.show) {
      const timer = setTimeout(() => {
        hideToast();
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [toast, hideToast]);

  // Handle page unload/refresh
  useEffect(() => {
    const handleBeforeUnload = async () => {
      await cleanupOnUnload();
    };

    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'hidden') {
        await cleanupOnUnload();
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [cleanupOnUnload]);

  // Monitor settings changes
  useEffect(() => {
    setShowDebugPanel(settings.show_debug_panel || false);
  }, [settings.show_debug_panel]);

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%)' }}>
      {/* Main Content */}
      <main className="py-4">
        <Container fluid>
          {/* Page Header */}
          <Row className="mb-4">
            <Col>
              <h2 className="text-white mb-2">Trading Dashboard</h2>
              <p className="text-muted">Monitoramento em tempo real de trading e dados de mercado</p>
              {isSSEConnected && (
                <div className="d-flex align-items-center gap-2 mt-2">
                  <div className="badge bg-success">
                    <i className="fas fa-wifi me-1"></i>
                    SSE Conectado
                  </div>
                  {isSubscribed && selectedMarket && (
                    <div className="badge bg-info">
                      <i className="fas fa-chart-line me-1"></i>
                      {selectedMarket}
                    </div>
                  )}
                </div>
              )}
            </Col>
          </Row>

          {/* Alert (for non-streaming notifications) */}
          {alert && (
            <Row className="mb-4">
              <Col>
                <Alert
                  message={alert.message}
                  type={alert.type}
                  onClose={() => setAlert(null)}
                />
              </Col>
            </Row>
          )}

          {/* Stats Cards and Stream Controls */}
          <Row className="mb-4">
            <Col md={3} className="mb-3">
              <Card className="stats-card h-100">
                <Card.Body className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <h6 className="text-muted mb-1">Saldo Total</h6>
                    <h4 className="text-white mb-0">
                      {isLoadingBalance ? (
                        <span className="text-muted">Carregando...</span>
                      ) : balance !== null ? (
                        `$${balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                      ) : (
                        '--'
                      )}
                    </h4>
                    <small className="text-muted">USD</small>
                  </div>
                  <div className="bg-primary rounded-circle p-2">
                    <DollarSign className="text-white" size={24} />
                  </div>
                </Card.Body>
              </Card>
            </Col>



            <Col md={9} className="mb-3">
              <Card className="stats-card h-100">
                <Card.Body>
                  <div className="d-flex align-items-center justify-content-between mb-3">
                    <div className="flex-grow-1">
                      <h6 className="text-muted mb-1">Status e Controles de Streaming</h6>
                      <div className="d-flex align-items-center gap-3">
                        <div className="d-flex align-items-center">
                          <div className={`rounded-circle p-2 me-2 ${isStreaming ? 'bg-success' : 'bg-secondary'}`}>
                            <Activity className="text-white" size={20} />
                          </div>
                          <div>
                            <h5 className="text-white mb-0">
                              {isStreaming ? 'Ativo' : 'Inativo'}
                            </h5>
                            <small className="text-muted">{ticks.length} ticks recebidos</small>
                          </div>
                        </div>
                        
                        {ticks.length > 0 && (
                          <div className="ms-3">
                            <CurrentTickDisplay 
                              currentTick={ticks[ticks.length - 1]} 
                              previousTick={ticks.length > 1 ? ticks[ticks.length - 2] : null}
                              selectedSymbol={selectedMarket}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="border-top pt-3">
                    <StreamControls
                      isSubscribed={isSubscribed}
                      isSubscribing={isSubscribing}
                      onSubscribe={handleSubscribe}
                      onUnsubscribe={handleUnsubscribe}
                      selectedMarket={selectedMarket}
                    />
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>





          {/* Debug Panel */}
          {showDebugPanel && (
            <Row className="mb-4">
              <Col lg={12}>
                <DebugPanel 
                  selectedMarket={selectedMarket}
                  isStreaming={isStreaming}
                  refreshInterval={settings.auto_refresh_interval || 5000}
                />
              </Col>
            </Row>
          )}



          {/* Main Content Grid */}
          <Row>
            {/* Left Side - Market Selection Only */}
            <Col lg={5} className="mb-4">
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Seleção de Mercado</h5>
                </Card.Header>
                <Card.Body>
                  <MarketSelector
                    markets={markets}
                    selectedMarket={selectedMarket}
                    onMarketChange={setSelectedMarket}
                    isLoading={isLoadingMarkets}
                    defaultMarket={settings.default_market}
                  />
                </Card.Body>
              </Card>
            </Col>

            {/* Right Side - Ticks Table */}
            <Col lg={7} className="mb-4">
              {/* Ticks Table */}
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Dados de Ticks em Tempo Real</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  <div className="table-container">
                    <TicksTable 
                      ticks={ticks} 
                      isStreaming={isStreaming} 
                      selectedSymbol={selectedMarket}
                    />
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </main>

      {/* Footer */}
      <Footer />

      {/* Toast Notifications */}
      <ToastContainer position="top-end" className="p-3">
        {toast && (
          <Toast 
            show={toast.show} 
            onClose={hideToast}
            bg={toast.type}
            className="toast-custom"
          >
            <Toast.Header closeButton>
              <strong className="me-auto">
                {toast.type === 'success' && 'Sucesso'}
                {toast.type === 'error' && 'Erro'}
                {toast.type === 'warning' && 'Aviso'}
                {toast.type === 'info' && 'Informação'}
              </strong>
            </Toast.Header>
            <Toast.Body className="text-white">
              {toast.message}
            </Toast.Body>
          </Toast>
        )}
      </ToastContainer>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, Table } from 'react-bootstrap';
import { RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { ApiService } from '../services/api';

interface DebugPanelProps {
  selectedMarket: string;
  isStreaming: boolean;
  refreshInterval?: number;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({ selectedMarket, isStreaming, refreshInterval = 5000 }) => {
  const [debugData, setDebugData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchDebugData = async () => {
    if (!selectedMarket) return;
    
    setIsLoading(true);
    try {
      const response = await ApiService.getDebugTicks();
      setDebugData(response);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching debug data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedMarket && isStreaming) {
      fetchDebugData();
      // Auto-refresh based on configured interval
      const interval = setInterval(fetchDebugData, refreshInterval);
      return () => clearInterval(interval);
    } else {
      // Clear debug data when not streaming
      setDebugData(null);
    }
  }, [selectedMarket, isStreaming, refreshInterval]);

  if (!selectedMarket) {
    return (
      <Card className="mb-3">
        <Card.Header>
          <h6 className="mb-0">🔍 Painel de Debug</h6>
        </Card.Header>
        <Card.Body>
          <div className="text-center text-muted">
            <AlertTriangle size={24} className="mb-2" />
            <p>Selecione um mercado para iniciar o debug</p>
          </div>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="mb-3">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h6 className="mb-0">🔍 Painel de Debug - {selectedMarket}</h6>
        <div className="d-flex align-items-center gap-2">
          <small className="text-muted">
            Atual: {debugData?.debug_info?.deriv_current_symbol || 'N/A'}
          </small>
          <Button
            variant="outline-primary"
            size="sm"
            onClick={fetchDebugData}
            disabled={isLoading}
          >
            <RefreshCw className={`me-1 ${isLoading ? 'spinning' : ''}`} size={14} />
            Atualizar
          </Button>
          <small className="text-muted">
            Auto-refresh: {refreshInterval / 1000}s
          </small>
          {lastUpdate && (
            <small className="text-muted">
              Última atualização: {lastUpdate.toLocaleTimeString()}
            </small>
          )}
        </div>
      </Card.Header>
      <Card.Body>
        {isLoading ? (
          <div className="text-center">
            <div className="spinner-border spinner-border-sm" role="status">
              <span className="visually-hidden">Carregando...</span>
            </div>
            <p className="mt-2 text-muted">Carregando dados de debug...</p>
          </div>
        ) : debugData ? (
          <div>
            {/* Status Summary */}
            <div className="row mb-3">
              <div className="col-md-3">
                <div className="text-center p-2 border rounded">
                  <h6 className="text-muted mb-1">Status Stream</h6>
                  <Badge bg={debugData.debug_info?.stream_available ? 'success' : 'danger'}>
                    {debugData.debug_info?.stream_available ? 'Ativo' : 'Inativo'}
                  </Badge>
                </div>
              </div>
              <div className="col-md-3">
                <div className="text-center p-2 border rounded">
                  <h6 className="text-muted mb-1">Total Ticks</h6>
                  <h5 className="mb-0">{debugData.debug_info?.total_ticks || 0}</h5>
                </div>
              </div>
              <div className="col-md-3">
                <div className="text-center p-2 border rounded">
                  <h6 className="text-muted mb-1">Último Tick</h6>
                  <small className="text-muted">
                    {debugData.debug_info?.time_diff || 0}s atrás
                  </small>
                </div>
              </div>
              <div className="col-md-3">
                <div className="text-center p-2 border rounded">
                  <h6 className="text-muted mb-1">Símbolo Ativo</h6>
                  <small className="text-info">
                    {debugData.debug_info?.current_symbol || 'N/A'}
                  </small>
                </div>
              </div>
            </div>

            {/* Debug Info */}
            <div className="row mb-3">
              <div className="col-12">
                <div className="p-2 border rounded bg-light">
                  <h6 className="text-muted mb-2">Informações de Debug:</h6>
                  <div className="row">
                    <div className="col-md-4">
                      <small className="text-muted">Selecionado:</small>
                      <br />
                      <Badge bg="primary">{selectedMarket}</Badge>
                    </div>
                    <div className="col-md-4">
                      <small className="text-muted">Atual no Backend:</small>
                      <br />
                      <Badge bg={debugData.debug_info?.deriv_current_symbol === selectedMarket ? 'success' : 'warning'}>
                        {debugData.debug_info?.deriv_current_symbol || 'N/A'}
                      </Badge>
                    </div>
                    <div className="col-md-4">
                      <small className="text-muted">Status:</small>
                      <br />
                      <Badge bg={debugData.debug_info?.deriv_current_symbol === selectedMarket ? 'success' : 'danger'}>
                        {debugData.debug_info?.deriv_current_symbol === selectedMarket ? 'Sincronizado' : 'Dessincronizado'}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Ticks Table */}
            {debugData.debug_info?.recent_ticks && debugData.debug_info.recent_ticks.length > 0 && (
              <div>
                <h6 className="mb-2">Últimos 5 Ticks Recebidos:</h6>
                <div className="table-responsive">
                  <Table size="sm" className="table-dark">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Símbolo</th>
                        <th>Status</th>
                        <th>Horário Local</th>
                        <th>Quote</th>
                        <th>Bid</th>
                        <th>Ask</th>
                        <th>Epoch</th>
                        <th>Pip Size</th>
                      </tr>
                    </thead>
                    <tbody>
                      {debugData.debug_info.recent_ticks.map((tick: any, index: number) => (
                        <tr key={index}>
                          <td>{tick.index}</td>
                          <td>
                            <Badge bg="info" className="small">
                              {tick.symbol || 'N/A'}
                            </Badge>
                          </td>
                          <td>
                            <Badge bg={tick.is_subscribed_symbol ? 'success' : 'warning'} className="small">
                              {tick.is_subscribed_symbol ? 'Inscrito' : 'Outro'}
                            </Badge>
                          </td>
                          <td>
                            <small>{tick.local_time}</small>
                          </td>
                          <td>
                            <strong className="text-success">
                              {tick.quote ? tick.quote.toFixed(5) : 'N/A'}
                            </strong>
                          </td>
                          <td>
                            <small>{tick.bid ? tick.bid.toFixed(5) : 'N/A'}</small>
                          </td>
                          <td>
                            <small>{tick.ask ? tick.ask.toFixed(5) : 'N/A'}</small>
                          </td>
                          <td>
                            <small>{tick.epoch || 'N/A'}</small>
                          </td>
                          <td>
                            <small>{tick.pip_size || 'N/A'}</small>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </div>
            )}

            {/* Raw Data */}
            <div className="mt-3">
              <h6 className="mb-2">Dados Brutos (Último Tick):</h6>
              <pre className="bg-dark text-light p-2 rounded" style={{ fontSize: '0.75rem', maxHeight: '200px', overflow: 'auto' }}>
                {JSON.stringify(debugData.debug_info?.recent_ticks?.[0]?.raw_tick || {}, null, 2)}
              </pre>
            </div>
          </div>
        ) : (
          <div className="text-center text-muted">
            <AlertTriangle size={24} className="mb-2" />
            <p>Nenhum dado de debug disponível</p>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

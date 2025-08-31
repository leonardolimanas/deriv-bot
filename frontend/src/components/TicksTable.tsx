import React, { useState, useEffect } from 'react';
import { Table, Badge, Spinner, Alert, Pagination } from 'react-bootstrap';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Tick } from '../types/api';

interface TicksTableProps {
  ticks: Tick[];
  isStreaming: boolean;
  selectedSymbol?: string;
}

export const TicksTable: React.FC<TicksTableProps> = ({ ticks, isStreaming, selectedSymbol }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const ticksPerPage = 20;

  // Reset to first page when ticks array changes significantly
  useEffect(() => {
    const totalPages = Math.ceil(ticks.length / ticksPerPage);
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [ticks.length, currentPage, ticksPerPage]);

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

  // Calculate price change
  const getPriceChange = (currentPrice: number, previousPrice: number) => {
    const change = currentPrice - previousPrice;
    const changePercent = (change / previousPrice) * 100;
    return {
      value: change,
      percent: changePercent,
      isPositive: change >= 0
    };
  };

  // Format timestamp
  const formatTime = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // Pagination logic - show most recent ticks first
  const totalPages = Math.ceil(ticks.length / ticksPerPage);
  const startIndex = (currentPage - 1) * ticksPerPage;
  const endIndex = startIndex + ticksPerPage;
  // Get ticks for current page, with most recent first (reverse the array to show newest first)
  const currentTicks = ticks.slice().reverse().slice(startIndex, endIndex);
  


  // Pagination component
  const PaginationComponent = () => (
    <div className="d-flex justify-content-between align-items-center p-3 border-bottom border-secondary">
      <div className="d-flex align-items-center">
        <small className="text-muted me-3">
          Página {currentPage} de {totalPages}
        </small>
        <small className="text-muted">
          Mostrando {startIndex + 1}-{Math.min(endIndex, ticks.length)} de {ticks.length} ticks
        </small>
      </div>
      
      <Pagination size="sm" className="mb-0">
        <Pagination.First 
          onClick={() => setCurrentPage(1)}
          disabled={currentPage === 1}
        />
        <Pagination.Prev 
          onClick={() => setCurrentPage(currentPage - 1)}
          disabled={currentPage === 1}
        />
        
        {/* Page numbers */}
        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
          let pageNum;
          if (totalPages <= 5) {
            pageNum = i + 1;
          } else if (currentPage <= 3) {
            pageNum = i + 1;
          } else if (currentPage >= totalPages - 2) {
            pageNum = totalPages - 4 + i;
          } else {
            pageNum = currentPage - 2 + i;
          }
          
          return (
            <Pagination.Item
              key={pageNum}
              active={pageNum === currentPage}
              onClick={() => setCurrentPage(pageNum)}
            >
              {pageNum}
            </Pagination.Item>
          );
        })}
        
        <Pagination.Next 
          onClick={() => setCurrentPage(currentPage + 1)}
          disabled={currentPage === totalPages}
        />
        <Pagination.Last 
          onClick={() => setCurrentPage(totalPages)}
          disabled={currentPage === totalPages}
        />
      </Pagination>
    </div>
  );

  if (ticks.length === 0) {
    return (
      <div className="text-center py-5">
        <div className="mb-3">
          {/* Removed Activity import, so this will cause an error */}
        </div>
        <h6 className="text-muted mb-2">Aguardando dados...</h6>
        <p className="text-muted small">
          {isStreaming ? 'Streaming ativo - dados chegarão em breve' : 'Inicie o streaming para receber dados'}
        </p>
        {isStreaming && (
          <div className="mt-3">
            <Spinner animation="border" size="sm" variant="primary" />
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      {/* Live Status Indicator */}
      {isStreaming && (
        <Alert variant="success" className="mb-3">
          <div className="d-flex align-items-center">
            {/* Removed Activity import, so this will cause an error */}
            <strong>Streaming Ativo</strong>
            <Badge bg="success" className="ms-2">
              {ticks.length} ticks recebidos
            </Badge>
          </div>
        </Alert>
      )}

      {/* Top Pagination */}
      {totalPages > 1 && <PaginationComponent />}

      {/* Ticks Table */}
      <div className="table-responsive">
        <Table className="table table-striped table-hover mb-0">
          <thead>
            <tr>
              <th className="text-white">
                <div className="d-flex align-items-center">
                  Horário
                </div>
              </th>
              <th className="text-white">Preço</th>
              <th className="text-white">
                <div className="d-flex align-items-center">
                  <TrendingUp className="me-1" size={14} />
                  Variação
                </div>
              </th>
              <th className="text-white">%</th>
            </tr>
          </thead>
          <tbody>
            {currentTicks.map((tick, index) => {
              const isLatest = currentPage === 1 && index === 0;
              // Since we're showing ticks in reverse order, we need to calculate the correct indices
              const reversedIndex = startIndex + index;
              const originalIndex = ticks.length - 1 - reversedIndex;
              // For variation, we need the tick that came BEFORE this one in time
              // Since we're showing newest first, the "previous" tick in time is the next one in the reversed array
              const nextTickInReversed = index < currentTicks.length - 1 ? currentTicks[index + 1] : null;
              const priceChange = nextTickInReversed 
                ? getPriceChange(tick.quote, nextTickInReversed.quote)
                : { value: 0, percent: 0, isPositive: true };

                              return (
                  <tr 
                    key={`${tick.timestamp}-${originalIndex}`}
                  className={isLatest ? 'table-active' : ''}
                  style={{
                    backgroundColor: isLatest ? 'rgba(102, 126, 234, 0.1)' : 'transparent'
                  }}
                >
                  <td className="text-white">
                    <small>{formatTime(tick.timestamp)}</small>
                  </td>
                  <td className="text-white">
                    <span className="fw-bold">
                      {formatPrice(tick.quote, selectedSymbol)}
                    </span>
                  </td>
                  <td className="text-white">
                    {priceChange.value !== 0 ? (
                      <div className="d-flex align-items-center">
                        {priceChange.isPositive ? (
                          <TrendingUp className="text-success me-1" size={12} />
                        ) : (
                          <TrendingDown className="text-danger me-1" size={12} />
                        )}
                        <Badge 
                          bg={priceChange.isPositive ? 'success' : 'danger'}
                          className="small"
                        >
                          {priceChange.isPositive ? '+' : ''}{formatPrice(priceChange.value, selectedSymbol)}
                        </Badge>
                      </div>
                    ) : (
                      <span className="text-muted">-</span>
                    )}
                  </td>
                  <td className="text-white">
                    {priceChange.percent !== 0 ? (
                      <Badge 
                        bg={priceChange.isPositive ? 'success' : 'danger'}
                        className="small"
                      >
                        {priceChange.isPositive ? '+' : ''}{priceChange.percent.toFixed(2)}%
                      </Badge>
                    ) : (
                      <span className="text-muted">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      </div>

      {/* Bottom Pagination */}
      {totalPages > 1 && <PaginationComponent />}

      {/* Table Footer */}
      <div className="p-3 border-top border-secondary">
        <div className="d-flex justify-content-between align-items-center">
          <small className="text-muted">
            {totalPages > 1 ? (
              `Página ${currentPage} de ${totalPages} - ${ticksPerPage} ticks por página`
            ) : (
              `Mostrando todos os ${ticks.length} ticks`
            )}
          </small>
          <small className="text-muted">
            Total: {ticks.length} ticks recebidos
          </small>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { Button, Badge } from 'react-bootstrap';
import { Play, Square, Activity } from 'lucide-react';

interface StreamControlsProps {
  isSubscribed: boolean;
  isSubscribing: boolean;
  onSubscribe: () => void;
  onUnsubscribe: () => void;
  selectedMarket: string;
}

export const StreamControls: React.FC<StreamControlsProps> = ({
  isSubscribed,
  isSubscribing,
  onSubscribe,
  onUnsubscribe,
  selectedMarket
}) => {
  return (
    <div className="stream-controls-compact">
      <div className="d-flex align-items-center justify-content-between">
        {/* Market Info */}
        <div className="d-flex align-items-center">
          {selectedMarket && (
            <div className="me-3">
              <Badge bg="info" className="small">
                <strong>Mercado:</strong> {selectedMarket}
              </Badge>
            </div>
          )}
        </div>

        {/* Control Buttons */}
        <div className="d-flex gap-2">
          <Button
            variant="success"
            size="sm"
            onClick={onSubscribe}
            disabled={isSubscribing || !selectedMarket}
            style={{ minWidth: '80px' }}
          >
            {isSubscribing ? (
              <>
                <div className="spinner-border spinner-border-sm me-1" role="status">
                  <span className="visually-hidden">Carregando...</span>
                </div>
                Conectando
              </>
            ) : (
              <>
                <Play className="me-1" size={14} />
                Iniciar
              </>
            )}
          </Button>

          <Button
            variant="danger"
            size="sm"
            onClick={onUnsubscribe}
            disabled={!isSubscribed}
            style={{ minWidth: '80px' }}
          >
            <Square className="me-1" size={14} />
            Parar
          </Button>
        </div>
      </div>
    </div>
  );
};

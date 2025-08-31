import React from 'react';
import { Navbar, Nav, Container, Badge, Button } from 'react-bootstrap';
import { 
  TrendingUp, 
  BarChart3, 
  Settings, 
  Bell, 
  User, 
  Activity,
  Wifi,
  WifiOff
} from 'lucide-react';

interface HeaderProps {
  isStreaming: boolean;
  balance: number | null;
  ticksCount: number;
  currentPage: 'dashboard' | 'settings';
  onPageChange: (page: 'dashboard' | 'settings') => void;
}

export const Header: React.FC<HeaderProps> = ({ isStreaming, balance, ticksCount, currentPage, onPageChange }) => {
  return (
    <Navbar bg="transparent" expand="lg" className="py-3">
      <Container fluid>
        {/* Brand */}
        <Navbar.Brand href="#" className="d-flex align-items-center">
          <div className="me-3">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-2">
              <TrendingUp className="text-white" size={24} />
            </div>
          </div>
          <div>
            <h4 className="mb-0 text-white fw-bold">Deriv Bot</h4>
            <small className="text-muted">Trading Dashboard</small>
          </div>
        </Navbar.Brand>

        {/* Navigation */}
        <Navbar.Toggle aria-controls="basic-navbar-nav" className="border-0 text-white" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link 
              href="#" 
              className={`d-flex align-items-center ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => onPageChange('dashboard')}
            >
              <Activity className="me-2" size={16} />
              Dashboard
            </Nav.Link>
            <Nav.Link 
              href="#" 
              className={`d-flex align-items-center ${currentPage === 'settings' ? 'active' : ''}`}
              onClick={() => onPageChange('settings')}
            >
              <Settings className="me-2" size={16} />
              Configurações
            </Nav.Link>
          </Nav>

          {/* Status Indicators */}
          <div className="d-flex align-items-center me-3">
            {/* Streaming Status */}
            <div className="d-flex align-items-center me-3">
              <Badge 
                bg={isStreaming ? "success" : "secondary"} 
                className="d-flex align-items-center"
              >
                {isStreaming ? <Wifi className="me-1" size={12} /> : <WifiOff className="me-1" size={12} />}
                {isStreaming ? 'Live' : 'Offline'}
              </Badge>
            </div>

            {/* Balance */}
            {balance !== null && (
              <div className="d-flex align-items-center me-3">
                <Badge bg="info" className="d-flex align-items-center">
                  <span className="me-1">💰</span>
                  ${balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </Badge>
              </div>
            )}

            {/* Ticks Counter */}
            <div className="d-flex align-items-center me-3">
              <Badge bg="warning" text="dark" className="d-flex align-items-center">
                <Activity className="me-1" size={12} />
                {ticksCount} ticks
              </Badge>
            </div>
          </div>

          {/* User Actions */}
          <div className="d-flex align-items-center">
            <Button variant="outline-light" size="sm" className="me-2">
              <Bell size={16} />
            </Button>
            <Button variant="outline-light" size="sm" className="d-flex align-items-center">
              <User size={16} className="me-1" />
              Profile
            </Button>
          </div>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

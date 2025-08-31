import React from 'react';
import { Container, Row, Col, Badge } from 'react-bootstrap';
import { 
  Heart, 
  Github, 
  Twitter, 
  Linkedin, 
  Mail,
  Shield,
  Zap,
  Clock
} from 'lucide-react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer py-4 mt-5">
      <Container>
        <Row className="align-items-center">
          {/* Brand and Description */}
          <Col lg={4} className="mb-3 mb-lg-0">
            <div className="d-flex align-items-center mb-2">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-1 me-2">
                <Zap className="text-white" size={16} />
              </div>
              <h6 className="mb-0 text-white fw-bold">Deriv Bot</h6>
            </div>
            <p className="text-muted mb-0 small">
              Plataforma moderna de trading automatizado com análise em tempo real 
              e estratégias avançadas para maximizar seus resultados.
            </p>
          </Col>

          {/* Quick Stats */}
          <Col lg={4} className="mb-3 mb-lg-0">
            <div className="d-flex justify-content-center">
              <div className="text-center me-4">
                <div className="d-flex align-items-center justify-content-center mb-1">
                  <Shield className="text-success me-1" size={14} />
                  <small className="text-muted">Seguro</small>
                </div>
                <Badge bg="success" className="small">99.9%</Badge>
              </div>
              <div className="text-center me-4">
                <div className="d-flex align-items-center justify-content-center mb-1">
                  <Zap className="text-warning me-1" size={14} />
                  <small className="text-muted">Performance</small>
                </div>
                <Badge bg="warning" text="dark" className="small">Rápido</Badge>
              </div>
              <div className="text-center">
                <div className="d-flex align-items-center justify-content-center mb-1">
                  <Clock className="text-info me-1" size={14} />
                  <small className="text-muted">Tempo Real</small>
                </div>
                <Badge bg="info" className="small">Live</Badge>
              </div>
            </div>
          </Col>

          {/* Social Links */}
          <Col lg={4} className="text-lg-end">
            <div className="d-flex justify-content-center justify-content-lg-end align-items-center">
              <a href="#" className="text-muted me-3 hover:text-white transition-colors">
                <Github size={18} />
              </a>
              <a href="#" className="text-muted me-3 hover:text-white transition-colors">
                <Twitter size={18} />
              </a>
              <a href="#" className="text-muted me-3 hover:text-white transition-colors">
                <Linkedin size={18} />
              </a>
              <a href="#" className="text-muted hover:text-white transition-colors">
                <Mail size={18} />
              </a>
            </div>
          </Col>
        </Row>

        {/* Bottom Bar */}
        <Row className="mt-3 pt-3 border-top border-secondary">
          <Col className="text-center">
            <p className="text-muted mb-0 small">
              © {currentYear} Deriv Bot. Made with{' '}
              <Heart className="text-danger" size={12} />{' '}
              by Leonardo Nascimento
            </p>
            <p className="text-muted mb-0 small mt-1">
              <strong>Disclaimer:</strong> Trading envolve risco. Este software é apenas para fins educacionais.
            </p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

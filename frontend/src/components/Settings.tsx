import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Spinner, Row, Col, Badge } from 'react-bootstrap';
import { Settings as SettingsIcon, Save, RefreshCw, Database, Eye, EyeOff, Bell, MessageSquare, Key } from 'lucide-react';
import { ApiService } from '../services/api';

interface Setting {
  key: string;
  value: string | boolean | number;
  description?: string;
}

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [localSettings, setLocalSettings] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [alert, setAlert] = useState<{ message: string; type: 'success' | 'error' | 'warning' | 'info' } | null>(null);

  // Load settings on component mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      // Loading settings...
      const response = await ApiService.getSettings();
              // Settings response received
      setSettings(response.settings);
      setLocalSettings(response.settings);
              // Settings loaded successfully
    } catch (error) {
      console.error('Error loading settings:', error);
      showAlert('Erro ao carregar configurações', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showAlert = (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
    setAlert({ message, type });
    setTimeout(() => setAlert(null), 5000);
  };

  const saveAllSettings = async () => {
    try {
      setSaving(true);
      // Saving all settings
      
      // Save each setting individually
      for (const [key, value] of Object.entries(localSettings)) {
        await ApiService.updateSetting(key, value);
      }
      
      setSettings(localSettings);
      setHasChanges(false);
      showAlert('Configurações salvas com sucesso!', 'success');
    } catch (error) {
      console.error('Error saving settings:', error);
      showAlert('Erro ao salvar configurações', 'error');
    } finally {
      setSaving(false);
    }
  };

  const updateLocalSetting = (key: string, value: any) => {
    setLocalSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleToggleSetting = (key: string, currentValue: boolean) => {
    updateLocalSetting(key, !currentValue);
  };

  const handleNumberSetting = (key: string, value: string) => {
    const numValue = parseInt(value);
    if (!isNaN(numValue)) {
      updateLocalSetting(key, numValue);
    }
  };

  const handleStringSetting = (key: string, value: string) => {
    updateLocalSetting(key, value);
  };

  const testTelegramNotification = async () => {
    try {
      setSaving(true);
      await ApiService.testTelegramNotification();
      showAlert('Notificação de teste enviada com sucesso!', 'success');
    } catch (error) {
      console.error('Error testing Telegram notification:', error);
      showAlert('Erro ao enviar notificação de teste', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <Spinner animation="border" variant="primary" />
        <p className="text-muted mt-3">Carregando configurações...</p>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <div className="d-flex align-items-center mb-4">
            <div className="bg-primary rounded-circle p-2 me-3">
              <SettingsIcon className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-white mb-0">Configurações</h2>
              <small className="text-muted">Gerencie as configurações do sistema</small>
            </div>
          </div>

          {/* Alert */}
          {alert && (
            <Alert variant={alert.type} dismissible onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          )}

          <Row>
            <Col lg={8}>
              {/* Interface Settings */}
              <Card className="stats-card mb-4">
                <Card.Header className="d-flex align-items-center">
                  <Eye className="me-2" size={20} />
                  <h5 className="mb-0 text-white">Configurações da Interface</h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <Eye className="me-2" size={16} />
                            Painel de Debug
                          </div>
                        </Form.Label>
                        <div className="d-flex align-items-center">
                          <Form.Check
                            type="switch"
                            id="show-debug-panel"
                            checked={localSettings.show_debug_panel || false}
                            onChange={() => handleToggleSetting('show_debug_panel', localSettings.show_debug_panel || false)}
                            className="me-2"
                          />
                          <span className="text-muted small">
                            {localSettings.show_debug_panel ? 'Visível' : 'Oculto'}
                          </span>
                        </div>
                        <Form.Text className="text-muted">
                          Exibir painel de debug no dashboard
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <RefreshCw className="me-2" size={16} />
                            Intervalo de Atualização
                          </div>
                        </Form.Label>
                        <Form.Control
                          type="number"
                          value={localSettings.auto_refresh_interval || 5000}
                          onChange={(e) => handleNumberSetting('auto_refresh_interval', e.target.value)}
                          min="1000"
                          max="30000"
                          step="1000"
                        />
                        <Form.Text className="text-muted">
                          Intervalo de atualização automática (ms)
                        </Form.Text>
                      </Form.Group>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>

              {/* Telegram Settings */}
              <Card className="stats-card mb-4">
                <Card.Header className="d-flex align-items-center">
                  <Bell className="me-2" size={20} />
                  <h5 className="mb-0 text-white">Configurações do Telegram</h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <Bell className="me-2" size={16} />
                            Notificações do Telegram
                          </div>
                        </Form.Label>
                        <div className="d-flex align-items-center">
                          <Form.Check
                            type="switch"
                            id="telegram-enabled"
                            checked={localSettings.telegram_enabled || false}
                            onChange={() => handleToggleSetting('telegram_enabled', localSettings.telegram_enabled || false)}
                            className="me-2"
                          />
                          <span className="text-muted small">
                            {localSettings.telegram_enabled ? 'Habilitadas' : 'Desabilitadas'}
                          </span>
                        </div>
                        <Form.Text className="text-muted">
                          Habilitar notificações do Telegram
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <RefreshCw className="me-2" size={16} />
                            Intervalo de Notificação
                          </div>
                        </Form.Label>
                        <Form.Control
                          type="number"
                          value={localSettings.telegram_notification_interval || 30}
                          onChange={(e) => handleNumberSetting('telegram_notification_interval', e.target.value)}
                          min="5"
                          max="300"
                          step="5"
                        />
                        <Form.Text className="text-muted">
                          Intervalo entre notificações (segundos)
                        </Form.Text>
                      </Form.Group>
                    </Col>
                  </Row>
                  
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <Key className="me-2" size={16} />
                            Token do Bot
                          </div>
                        </Form.Label>
                        <Form.Control
                          type="password"
                          value={localSettings.telegram_bot_token || ''}
                          onChange={(e) => handleStringSetting('telegram_bot_token', e.target.value)}
                          placeholder="Digite o token do bot"
                        />
                        <Form.Text className="text-muted">
                          Token do bot do Telegram
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <MessageSquare className="me-2" size={16} />
                            ID do Chat
                          </div>
                        </Form.Label>
                        <Form.Control
                          type="text"
                          value={localSettings.telegram_chat_id || ''}
                          onChange={(e) => handleStringSetting('telegram_chat_id', e.target.value)}
                          placeholder="Digite o ID do chat"
                        />
                        <Form.Text className="text-muted">
                          ID do chat do Telegram
                        </Form.Text>
                      </Form.Group>
                    </Col>
                  </Row>

                  <div className="d-flex justify-content-end">
                    <Button 
                      variant="outline-primary" 
                      size="sm"
                      onClick={testTelegramNotification}
                      disabled={saving}
                    >
                      {saving ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          Testando...
                        </>
                      ) : (
                        <>
                          <Bell size={16} className="me-2" />
                          Testar Notificação
                        </>
                      )}
                    </Button>
                  </div>
                </Card.Body>
              </Card>

              {/* API Settings */}
              <Card className="stats-card mb-4">
                <Card.Header className="d-flex align-items-center">
                  <Key className="me-2" size={20} />
                  <h5 className="mb-0 text-white">Configurações da API Deriv</h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={4}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <Key className="me-2" size={16} />
                            App ID
                          </div>
                        </Form.Label>
                        <Form.Control
                          type="text"
                          value={localSettings.deriv_app_id || ''}
                          onChange={(e) => handleStringSetting('deriv_app_id', e.target.value)}
                          placeholder="Digite o App ID"
                        />
                        <Form.Text className="text-muted">
                          ID da aplicação Deriv
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <Key className="me-2" size={16} />
                            API Token (Demo)
                          </div>
                        </Form.Label>
                        <Form.Control
                          type="password"
                          value={localSettings.deriv_api_token || ''}
                          onChange={(e) => handleStringSetting('deriv_api_token', e.target.value)}
                          placeholder="Digite o token da API"
                        />
                        <Form.Text className="text-muted">
                          Token da API Deriv (Demo)
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          <div className="d-flex align-items-center">
                            <Key className="me-2" size={16} />
                            API Token (Real)
                          </div>
                        </Form.Label>
                        <Form.Control
                          type="password"
                          value={localSettings.deriv_api_token_real || ''}
                          onChange={(e) => handleStringSetting('deriv_api_token_real', e.target.value)}
                          placeholder="Digite o token real da API"
                        />
                        <Form.Text className="text-muted">
                          Token da API Deriv (Real)
                        </Form.Text>
                      </Form.Group>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>

              {/* Data Settings */}
              <Card className="stats-card mb-4">
                <Card.Header className="d-flex align-items-center">
                  <Database className="me-2" size={20} />
                  <h5 className="mb-0 text-white">Configurações de Dados</h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={4}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          Máximo de Ticks
                        </Form.Label>
                        <Form.Control
                          type="number"
                          value={localSettings.max_ticks_display || 20}
                          onChange={(e) => handleNumberSetting('max_ticks_display', e.target.value)}
                          min="10"
                          max="100"
                          step="5"
                        />
                        <Form.Text className="text-muted">
                          Número máximo de ticks exibidos na tabela
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          Ativo Padrão
                        </Form.Label>
                        <Form.Control
                          type="text"
                          value={localSettings.default_market || 'R_100'}
                          onChange={(e) => handleStringSetting('default_market', e.target.value)}
                          placeholder="Ex: R_100, RDBEAR, FRXEURUSD"
                        />
                        <Form.Text className="text-muted">
                          Ativo selecionado automaticamente ao carregar o dashboard
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group className="mb-3">
                        <Form.Label className="text-white">
                          Notificações
                        </Form.Label>
                        <div className="d-flex align-items-center">
                          <Form.Check
                            type="switch"
                            id="enable-notifications"
                            checked={localSettings.enable_notifications || false}
                            onChange={() => handleToggleSetting('enable_notifications', localSettings.enable_notifications || false)}
                            className="me-2"
                          />
                          <span className="text-muted small">
                            {localSettings.enable_notifications ? 'Habilitadas' : 'Desabilitadas'}
                          </span>
                        </div>
                        <Form.Text className="text-muted">
                          Habilitar notificações do sistema
                        </Form.Text>
                      </Form.Group>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>

            <Col lg={4}>
              {/* Settings Info */}
              <Card className="stats-card">
                <Card.Header>
                  <h5 className="mb-0 text-white">Informações</h5>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <small className="text-muted">Configurações Ativas</small>
                    <div className="mt-2">
                      <Badge bg="success" className="me-1 mb-1">
                        {Object.keys(settings).length} configurações
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <small className="text-muted">Banco de Dados</small>
                    <div className="mt-2">
                      <Badge bg="info" className="me-1 mb-1">
                        SQLite Local
                      </Badge>
                    </div>
                  </div>

                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    onClick={loadSettings}
                    disabled={loading}
                    className="w-100"
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Carregando...
                      </>
                    ) : (
                      <>
                        <RefreshCw size={16} className="me-2" />
                        Recarregar
                      </>
                    )}
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Action Buttons */}
          <Row className="mt-4">
            <Col lg={8}>
              <Card className="stats-card">
                <Card.Body className="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 className="text-white mb-1">Ações</h6>
                    <small className="text-muted">
                      {hasChanges ? 'Você tem alterações não salvas' : 'Todas as configurações estão salvas'}
                    </small>
                  </div>
                  <div className="d-flex gap-2">
                    <Button 
                      variant="outline-secondary" 
                      size="sm"
                      onClick={loadSettings}
                      disabled={loading}
                    >
                      <RefreshCw size={16} className="me-2" />
                      Recarregar
                    </Button>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={saveAllSettings}
                      disabled={saving || !hasChanges}
                    >
                      {saving ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          Salvando...
                        </>
                      ) : (
                        <>
                          <Save size={16} className="me-2" />
                          Salvar Configurações
                        </>
                      )}
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </div>
      </div>
    </div>
  );
};

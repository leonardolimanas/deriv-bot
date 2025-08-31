import React, { useState, useEffect } from 'react';
import { tradingApi } from '../services/tradingApi';
import { Strategy } from '../types/trading';

interface StrategyForm {
  name: string;
  description: string;
  trigger_count: number;
  max_entries: number;
  base_amount: number;
  martingale_multiplier: number;
  is_active: boolean;
}

export const Strategies: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);

  const [form, setForm] = useState<StrategyForm>({
    name: '',
    description: '',
    trigger_count: 3,
    max_entries: 5,
    base_amount: 1.0,
    martingale_multiplier: 2.0,
    is_active: true
  });

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await tradingApi.getStrategies();
      setStrategies(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar estratégias');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');

      if (editingStrategy) {
        await tradingApi.updateStrategy(editingStrategy.strategy_id, form);
      } else {
        await tradingApi.createStrategy(form);
      }

      setShowForm(false);
      setEditingStrategy(null);
      resetForm();
      loadStrategies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar estratégia');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (strategy: Strategy) => {
    setEditingStrategy(strategy);
    setForm({
      name: strategy.name || '',
      description: strategy.description || '',
      trigger_count: strategy.trigger_count,
      max_entries: strategy.max_entries,
      base_amount: strategy.base_amount,
      martingale_multiplier: strategy.martingale_multiplier,
      is_active: strategy.is_active
    });
    setShowForm(true);
  };

  const handleDelete = async (strategyId: string) => {
    if (!window.confirm('Tem certeza que deseja excluir esta estratégia?')) {
      return;
    }

    try {
      setLoading(true);
      await tradingApi.deleteStrategy(strategyId);
      loadStrategies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir estratégia');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setForm({
      name: '',
      description: '',
      trigger_count: 3,
      max_entries: 5,
      base_amount: 1.0,
      martingale_multiplier: 2.0,
      is_active: true
    });
  };

  return (
    <div className="min-vh-100 bg-dark">
      <div className="container-fluid py-4">
        <div className="row">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h2 className="text-white mb-0">
                <i className="fas fa-cogs me-2"></i>
                Gerenciar Estratégias
              </h2>
              <div className="d-flex gap-2">
                <button 
                  className="btn btn-outline-light btn-sm"
                  onClick={loadStrategies}
                  disabled={loading}
                >
                  <i className="fas fa-sync-alt me-1"></i>
                  {loading ? 'Atualizando...' : 'Atualizar'}
                </button>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={() => {
                    setShowForm(true);
                    setEditingStrategy(null);
                    resetForm();
                  }}
                >
                  <i className="fas fa-plus me-1"></i>
                  Nova Estratégia
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

            {/* Strategy Form */}
            {showForm && (
              <div className="card bg-dark-light border-0 mb-4">
                <div className="card-header bg-transparent border-0">
                  <h5 className="text-white mb-0">
                    <i className="fas fa-edit me-2"></i>
                    {editingStrategy ? 'Editar Estratégia' : 'Nova Estratégia'}
                  </h5>
                </div>
                <div className="card-body">
                  <form onSubmit={handleSubmit}>
                    <div className="row g-3">
                      <div className="col-md-6">
                        <label className="form-label text-white">Nome</label>
                        <input
                          type="text"
                          value={form.name}
                          onChange={(e) => setForm(prev => ({ ...prev, name: e.target.value }))}
                          className="form-control bg-dark text-white border-secondary"
                          placeholder="Nome da estratégia"
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label text-white">Descrição</label>
                        <input
                          type="text"
                          value={form.description}
                          onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                          className="form-control bg-dark text-white border-secondary"
                          placeholder="Descrição da estratégia"
                        />
                      </div>
                      <div className="col-12">
                        <label className="form-label text-white">Descrição Detalhada</label>
                        <textarea
                          value={form.description}
                          onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                          className="form-control bg-dark text-white border-secondary"
                          placeholder="Descrição detalhada da estratégia"
                          rows={3}
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label text-white">Gatilho (repetições)</label>
                        <input
                          type="number"
                          value={form.trigger_count}
                          onChange={(e) => setForm(prev => ({ ...prev, trigger_count: parseInt(e.target.value) }))}
                          className="form-control bg-dark text-white border-secondary"
                          min="2"
                          max="10"
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label text-white">Máximo de Entradas</label>
                        <input
                          type="number"
                          value={form.max_entries}
                          onChange={(e) => setForm(prev => ({ ...prev, max_entries: parseInt(e.target.value) }))}
                          className="form-control bg-dark text-white border-secondary"
                          min="1"
                          max="10"
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label text-white">Valor Base ($)</label>
                        <input
                          type="number"
                          step="0.01"
                          value={form.base_amount}
                          onChange={(e) => setForm(prev => ({ ...prev, base_amount: parseFloat(e.target.value) }))}
                          className="form-control bg-dark text-white border-secondary"
                          min="0.01"
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label text-white">Multiplicador Martingale</label>
                        <input
                          type="number"
                          step="0.1"
                          value={form.martingale_multiplier}
                          onChange={(e) => setForm(prev => ({ ...prev, martingale_multiplier: parseFloat(e.target.value) }))}
                          className="form-control bg-dark text-white border-secondary"
                          min="1.0"
                          required
                        />
                      </div>
                      <div className="col-12">
                        <div className="form-check">
                          <input
                            type="checkbox"
                            checked={form.is_active}
                            onChange={(e) => setForm(prev => ({ ...prev, is_active: e.target.checked }))}
                            className="form-check-input"
                            id="isActive"
                          />
                          <label className="form-check-label text-white" htmlFor="isActive">
                            Estratégia Ativa
                          </label>
                        </div>
                      </div>
                      <div className="col-12">
                        <div className="d-flex gap-2">
                          <button
                            type="submit"
                            disabled={loading}
                            className="btn btn-primary"
                          >
                            <i className="fas fa-save me-2"></i>
                            {loading ? 'Salvando...' : 'Salvar'}
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setShowForm(false);
                              setEditingStrategy(null);
                              resetForm();
                            }}
                            className="btn btn-secondary"
                          >
                            <i className="fas fa-times me-2"></i>
                            Cancelar
                          </button>
                        </div>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {/* Strategies List */}
            <div className="card bg-dark-light border-0">
              <div className="card-header bg-transparent border-0">
                <h5 className="text-white mb-0">
                  <i className="fas fa-list me-2"></i>
                  Estratégias Cadastradas
                </h5>
              </div>
              <div className="card-body">
                {loading ? (
                  <div className="text-center text-white">
                    <i className="fas fa-spinner fa-spin me-2"></i>
                    Carregando estratégias...
                  </div>
                ) : strategies.length === 0 ? (
                  <div className="text-center text-muted">
                    <i className="fas fa-inbox fa-2x mb-3"></i>
                    <p>Nenhuma estratégia cadastrada</p>
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="table table-dark table-hover">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Nome</th>
                          <th>Descrição</th>
                          <th>Gatilho</th>
                          <th>Entradas</th>
                          <th>Valor Base</th>
                          <th>Multiplicador</th>
                          <th>Status</th>
                          <th>Ações</th>
                        </tr>
                      </thead>
                      <tbody>
                        {strategies.map((strategy) => (
                          <tr key={strategy.strategy_id}>
                            <td className="fw-bold">{strategy.strategy_id}</td>
                            <td>{strategy.name || '-'}</td>
                            <td>{strategy.description || '-'}</td>
                            <td>{strategy.trigger_count}</td>
                            <td>{strategy.max_entries}</td>
                            <td>${strategy.base_amount}</td>
                            <td>{strategy.martingale_multiplier}x</td>
                            <td>
                              <span className={`badge ${strategy.is_active ? 'bg-success' : 'bg-secondary'}`}>
                                {strategy.is_active ? 'Ativa' : 'Inativa'}
                              </span>
                            </td>
                            <td>
                              <div className="btn-group btn-group-sm">
                                <button
                                  className="btn btn-outline-primary"
                                  onClick={() => handleEdit(strategy)}
                                  title="Editar"
                                >
                                  <i className="fas fa-edit"></i>
                                </button>
                                <button
                                  className="btn btn-outline-danger"
                                  onClick={() => handleDelete(strategy.strategy_id)}
                                  title="Excluir"
                                >
                                  <i className="fas fa-trash"></i>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

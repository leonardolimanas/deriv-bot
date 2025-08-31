"""
Trading API Routes
"""

from flask import Blueprint, request, jsonify, current_app
from ..services.trading_service import TradingService
import logging

logger = logging.getLogger(__name__)

# Blueprint para rotas de trading
trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')

# Instância global do serviço de trading
trading_service = TradingService()

@trading_bp.route('/strategies', methods=['POST'])
def create_strategy():
    """Cria uma nova estratégia de trading"""
    try:
        data = request.get_json()
        
        trigger_count = data.get('trigger_count', 3)
        max_entries = data.get('max_entries', 5)
        base_amount = data.get('base_amount', 1.0)
        martingale_multiplier = data.get('martingale_multiplier', 2.0)
        
        # Sempre gerar ID automaticamente
        result = trading_service.create_strategy(
            strategy_id=None,  # Será gerado automaticamente
            trigger_count=trigger_count,
            max_entries=max_entries,
            base_amount=base_amount,
            martingale_multiplier=martingale_multiplier
        )
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar estratégia: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """Retorna todas as estratégias"""
    try:
        strategies = trading_service.get_all_strategies()
        return jsonify(strategies), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estratégias: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/strategies/<strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """Retorna informações de uma estratégia específica"""
    try:
        strategy_info = trading_service.get_strategy_info(strategy_id)
        
        if "error" in strategy_info:
            return jsonify(strategy_info), 404
            
        return jsonify(strategy_info), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estratégia {strategy_id}: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/strategies/<strategy_id>/reset', methods=['POST'])
def reset_strategy(strategy_id):
    """Reseta uma estratégia"""
    try:
        result = trading_service.reset_strategy(strategy_id)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao resetar estratégia {strategy_id}: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/strategies/<strategy_id>/cancel', methods=['POST'])
def cancel_trades(strategy_id):
    """Cancela todos os trades ativos de uma estratégia"""
    try:
        result = trading_service.cancel_active_trades(strategy_id)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao cancelar trades da estratégia {strategy_id}: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/strategies/<strategy_id>/trades', methods=['POST'])
def create_trade(strategy_id):
    """Cria uma nova entrada de trade"""
    try:
        data = request.get_json()
        
        bet_type = data.get('bet_type')
        amount = data.get('amount')
        
        if not bet_type:
            return jsonify({"error": "bet_type é obrigatório"}), 400
        
        result = trading_service.create_trade(strategy_id, bet_type, amount)
        
        if "error" in result:
            return jsonify(result), 400
            
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar trade: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/strategies/<strategy_id>/ticks', methods=['POST'])
def process_tick(strategy_id):
    """Processa um novo tick para uma estratégia"""
    try:
        data = request.get_json()
        
        tick_value = data.get('tick_value')
        
        if tick_value is None:
            return jsonify({"error": "tick_value é obrigatório"}), 400
        
        if not isinstance(tick_value, int) or tick_value < 0 or tick_value > 9:
            return jsonify({"error": "tick_value deve ser um número inteiro entre 0 e 9"}), 400
        
        result = trading_service.process_tick(strategy_id, tick_value)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar tick: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/history', methods=['GET'])
def get_trade_history():
    """Retorna histórico de trades"""
    try:
        strategy_id = request.args.get('strategy_id')
        limit = request.args.get('limit', 100, type=int)
        
        history = trading_service.get_trade_history(strategy_id, limit)
        return jsonify(history), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/stats', methods=['GET'])
def get_overall_stats():
    """Retorna estatísticas gerais"""
    try:
        stats = trading_service.get_overall_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@trading_bp.route('/markets', methods=['GET'])
def get_available_markets():
    """Retorna mercados disponíveis para trading"""
    try:
        # Lista de mercados disponíveis
        markets = [
            {
                "id": "frxEURUSD",
                "name": "EUR/USD",
                "description": "Euro vs Dólar Americano",
                "type": "forex"
            },
            {
                "id": "frxGBPUSD", 
                "name": "GBP/USD",
                "description": "Libra Esterlina vs Dólar Americano",
                "type": "forex"
            },
            {
                "id": "R_10",
                "name": "Volatility 10 Index",
                "description": "Índice de Volatilidade 10",
                "type": "synthetic"
            },
            {
                "id": "R_25",
                "name": "Volatility 25 Index", 
                "description": "Índice de Volatilidade 25",
                "type": "synthetic"
            },
            {
                "id": "R_50",
                "name": "Volatility 50 Index",
                "description": "Índice de Volatilidade 50", 
                "type": "synthetic"
            },
            {
                "id": "R_75",
                "name": "Volatility 75 Index",
                "description": "Índice de Volatilidade 75",
                "type": "synthetic"
            },
            {
                "id": "R_100",
                "name": "Volatility 100 Index",
                "description": "Índice de Volatilidade 100",
                "type": "synthetic"
            }
        ]
        
        return jsonify(markets), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar mercados: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

from flask import jsonify, request, current_app
from flask_limiter.util import get_remote_address
from . import api_bp
from ..services.deriv_service import DerivService
from ..services.trading_service import TradingService
from ..utils.validators import validate_symbol
from ..utils.decorators import handle_errors
import asyncio
import threading
import time

# Global services
deriv_service = None
main_loop = None

def init_services():
    """Initialize global services."""
    global deriv_service, main_loop
    if not main_loop:
        main_loop = asyncio.new_event_loop()
        thread = threading.Thread(target=lambda: asyncio.run(run_services()), daemon=True)
        thread.start()

async def run_services():
    """Run services in event loop."""
    global deriv_service
    from flask import current_app
    with current_app.app_context():
        deriv_service = DerivService()
        await deriv_service.initialize()

@api_bp.route('/stats')
@handle_errors
def get_stats():
    """Get account balance and statistics."""
    if not deriv_service:
        return jsonify({"error": "Service not ready"}), 503
    
    try:
        balance = asyncio.run_coroutine_threadsafe(
            deriv_service.get_balance(), main_loop
        ).result(timeout=5)
        
        return jsonify({
            "balance": balance,
            "currency": "USD",
            "timestamp": asyncio.run_coroutine_threadsafe(
                deriv_service.get_timestamp(), main_loop
            ).result(timeout=2)
        })
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {e}")
        return jsonify({"error": "Failed to fetch balance"}), 500

@api_bp.route('/markets')
@handle_errors
def get_markets():
    """Get list of available markets/symbols."""
    if not deriv_service:
        return jsonify({"error": "Service not ready"}), 503
    
    try:
        markets = asyncio.run_coroutine_threadsafe(
            deriv_service.get_active_symbols(), main_loop
        ).result(timeout=10)
        
        return jsonify({
            "markets": markets,
            "count": len(markets),
            "timestamp": asyncio.run_coroutine_threadsafe(
                deriv_service.get_timestamp(), main_loop
            ).result(timeout=2)
        })
    except Exception as e:
        current_app.logger.error(f"Error getting markets: {e}")
        return jsonify({"error": "Failed to fetch markets"}), 500

@api_bp.route('/subscribe', methods=['POST'])
@handle_errors
def subscribe_to_ticks():
    """Subscribe to tick updates for a specific symbol."""
    if not deriv_service:
        return jsonify({"error": "Service not ready"}), 503
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    symbol = data.get("symbol")
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    # Validate symbol
    if not validate_symbol(symbol):
        return jsonify({"error": "Invalid symbol format"}), 400
    
    try:
        result = asyncio.run_coroutine_threadsafe(
            deriv_service.subscribe_to_ticks(symbol), main_loop
        ).result(timeout=5)
        
        if result.get("status") == "subscribed":
            current_app.logger.info(f"Subscribed to ticks for {symbol}")
            # Send Telegram notification
            asyncio.run_coroutine_threadsafe(
                telegram_service.send_notification(f"Subscribed to {symbol} tick stream"),
                main_loop
            )
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error subscribing to {symbol}: {e}")
        return jsonify({"error": f"Failed to subscribe to {symbol}"}), 500

@api_bp.route('/unsubscribe', methods=['POST'])
@handle_errors
def unsubscribe_from_ticks():
    """Unsubscribe from current tick subscription."""
    if not deriv_service:
        return jsonify({"error": "Service not ready"}), 503
    
    try:
        result = asyncio.run_coroutine_threadsafe(
            deriv_service.unsubscribe_from_ticks(), main_loop
        ).result(timeout=5)
        
        if result.get("status") == "unsubscribed":
            current_app.logger.info("Unsubscribed from tick stream")
            # Send Telegram notification
            asyncio.run_coroutine_threadsafe(
                telegram_service.send_notification("Unsubscribed from tick stream"),
                main_loop
            )
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error unsubscribing: {e}")
        return jsonify({"error": "Failed to unsubscribe"}), 500

@api_bp.route('/ticks')
@handle_errors
def get_ticks():
    """Get the latest ticks."""
    if not deriv_service:
        return jsonify({"error": "Service not ready"}), 503
    
    try:
        ticks_data = deriv_service.get_latest_ticks()
        return jsonify(ticks_data)
    except Exception as e:
        current_app.logger.error(f"Error getting ticks: {e}")
        return jsonify({"error": "Failed to fetch ticks"}), 500

@api_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "deriv-bot-api",
        "version": "1.0.0",
        "services": {
            "deriv": deriv_service is not None,
            "telegram": telegram_service is not None
        }
    })

@api_bp.route('/test-trading')
def test_trading():
    """Test endpoint for trading."""
    return jsonify({
        "message": "Trading routes are working!",
        "timestamp": time.time()
    })

@api_bp.route('/test-strategy-model')
def test_strategy_model():
    """Test endpoint for strategy model."""
    try:
        import sys
        sys.path.append('.')
        from app.models.strategy import StrategyModel
        strategy_model = StrategyModel()
        return jsonify({
            "message": "Strategy model imported successfully!",
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({
            "error": f"Failed to import strategy model: {str(e)}",
            "timestamp": time.time()
        }), 500

@api_bp.route('/debug/ticks')
def debug_ticks():
    """Debug endpoint to get detailed tick information."""
    if not deriv_service:
        return jsonify({"error": "Service not ready"}), 503
    
    try:
        ticks_data = deriv_service.get_latest_ticks()
        
        # Add debug information
        debug_info = {
            "current_symbol": ticks_data.get("symbol"),
            "total_ticks": len(ticks_data.get("ticks", [])),
            "stream_available": ticks_data.get("available"),
            "last_tick_time": deriv_service.last_tick_time,
            "current_time": int(time.time()),
            "time_diff": int(time.time()) - deriv_service.last_tick_time if deriv_service.last_tick_time else 0,
            "recent_ticks": []
        }
        
        # Get last 5 ticks with detailed info
        recent_ticks = ticks_data.get("ticks", [])[-5:]
        for i, tick in enumerate(recent_ticks):
            tick_debug = {
                "index": i + 1,
                "timestamp": tick.get("timestamp"),
                "local_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick.get("timestamp", 0))) if tick.get("timestamp") else "N/A",
                "quote": tick.get("quote"),
                "bid": tick.get("bid"),
                "ask": tick.get("ask"),
                "epoch": tick.get("epoch"),
                "pip_size": tick.get("pip_size"),
                "tick_size": tick.get("tick_size"),
                "raw_tick": tick
            }
            debug_info["recent_ticks"].append(tick_debug)
        
        return jsonify({
            "ticks_data": ticks_data,
            "debug_info": debug_info
        })
    except Exception as e:
        current_app.logger.error(f"Error in debug ticks: {e}")
        return jsonify({"error": "Failed to get debug ticks"}), 500

# Trading routes - temporary direct implementation
@api_bp.route('/trading/markets', methods=['GET'])
def get_trading_markets():
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
        current_app.logger.error(f"Erro ao buscar mercados: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# Strategy management routes
@api_bp.route('/trading/strategies', methods=['GET'])
def get_strategies():
    """Retorna todas as estratégias cadastradas"""
    try:
        from ..models.strategy import StrategyModel
        strategy_model = StrategyModel()
        strategies = strategy_model.get_all_strategies()
        return jsonify(strategies), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar estratégias: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@api_bp.route('/trading/strategies/active', methods=['GET'])
def get_active_strategies():
    """Retorna todas as estratégias ativas do serviço de trading"""
    try:
        from ..services.trading_service import TradingService
        trading_service = TradingService()
        strategies = trading_service.get_all_strategies()
        return jsonify(strategies), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar estratégias ativas: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@api_bp.route('/trading/strategies', methods=['POST'])
def create_strategy():
    """Cria uma nova estratégia"""
    try:
        from ..models.strategy import StrategyModel
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        strategy_model = StrategyModel()
        
        # Remover strategy_id se fornecido (será gerado automaticamente)
        if 'strategy_id' in data:
            del data['strategy_id']
        
        strategy = strategy_model.create_strategy(data)
        return jsonify(strategy), 201
    except Exception as e:
        current_app.logger.error(f"Erro ao criar estratégia: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@api_bp.route('/trading/strategies/<strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """Retorna uma estratégia específica"""
    try:
        from ..models.strategy import StrategyModel
        strategy_model = StrategyModel()
        strategy = strategy_model.get_strategy(strategy_id)
        
        if not strategy:
            return jsonify({"error": "Estratégia não encontrada"}), 404
        
        return jsonify(strategy), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar estratégia: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@api_bp.route('/trading/strategies/<strategy_id>', methods=['PUT'])
def update_strategy(strategy_id):
    """Atualiza uma estratégia"""
    try:
        from ..models.strategy import StrategyModel
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        strategy_model = StrategyModel()
        strategy = strategy_model.update_strategy(strategy_id, data)
        
        if not strategy:
            return jsonify({"error": "Estratégia não encontrada"}), 404
        
        return jsonify(strategy), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar estratégia: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@api_bp.route('/trading/strategies/<strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    """Exclui uma estratégia"""
    try:
        from ..models.strategy import StrategyModel
        strategy_model = StrategyModel()
        
        success = strategy_model.delete_strategy(strategy_id)
        if not success:
            return jsonify({"error": "Estratégia não encontrada"}), 404
        
        return jsonify({"message": "Estratégia excluída com sucesso"}), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir estratégia: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# Initialize services when blueprint is registered
init_services()

"""
Trading Service - Gerencia estratégias e execução de trades
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from flask import current_app
from ..strategies import EvenOddStrategy, BetType, TradeEntry

logger = logging.getLogger(__name__)

class TradingService:
    """Serviço para gerenciar estratégias de trading"""
    
    def __init__(self):
        self.strategies: Dict[str, EvenOddStrategy] = {}
        self.active_trades: Dict[str, List[TradeEntry]] = {}
        self.trade_history: List[Dict] = []
        self.is_running = False
        
    def create_strategy(self, 
                       strategy_id: Optional[str] = None,
                       trigger_count: int = 3,
                       max_entries: int = 5,
                       base_amount: float = 1.0,
                       martingale_multiplier: float = 2.0) -> Dict:
        """
        Cria uma nova estratégia
        
        Args:
            strategy_id: ID único da estratégia (opcional, será gerado automaticamente se None)
            trigger_count: Quantidade de repetições para gatilho
            max_entries: Máximo de entradas (martingales)
            base_amount: Valor base da primeira entrada
            martingale_multiplier: Multiplicador para martingale
            
        Returns:
            Dict com informações da estratégia criada
        """
        # Gerar ID automático se não fornecido
        if strategy_id is None:
            strategy_id = self._generate_strategy_id()
        
        strategy = EvenOddStrategy(
            trigger_count=trigger_count,
            max_entries=max_entries,
            base_amount=base_amount,
            martingale_multiplier=martingale_multiplier
        )
        
        self.strategies[strategy_id] = strategy
        self.active_trades[strategy_id] = []
        
        logger.info(f"Estratégia criada: {strategy_id}")
        
        return {
            "strategy_id": strategy_id,
            "trigger_count": trigger_count,
            "max_entries": max_entries,
            "base_amount": base_amount,
            "martingale_multiplier": martingale_multiplier,
            "status": "created"
        }

    def _generate_strategy_id(self) -> str:
        """Generate a unique strategy ID"""
        import uuid
        from datetime import datetime
        
        # Gerar ID baseado em timestamp + UUID curto
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"strategy_{timestamp}_{unique_id}"
    
    def process_tick(self, strategy_id: str, tick_value: int) -> Dict:
        """
        Processa um novo tick para uma estratégia específica
        
        Args:
            strategy_id: ID da estratégia
            tick_value: Valor do tick
            
        Returns:
            Dict com resultados do processamento
        """
        if strategy_id not in self.strategies:
            return {"error": "Estratégia não encontrada"}
        
        strategy = self.strategies[strategy_id]
        
        # Adiciona o tick à estratégia
        trigger_info = strategy.add_tick(tick_value)
        
        # Processa resultados de trades ativos
        trade_results = strategy.process_tick_result(tick_value)
        
        # Atualiza trades ativos
        self.active_trades[strategy_id] = strategy.active_trades.copy()
        
        # Adiciona resultados ao histórico
        for result in trade_results:
            if result.get("status") in ["win", "loss"]:
                self.trade_history.append({
                    "strategy_id": strategy_id,
                    "timestamp": datetime.now().isoformat(),
                    **result
                })
        
        return {
            "strategy_id": strategy_id,
            "tick_value": tick_value,
            "trigger_info": trigger_info,
            "trade_results": trade_results,
            "active_trades": len(strategy.active_trades),
            "stats": strategy.get_strategy_stats()
        }
    
    def create_trade(self, strategy_id: str, bet_type: str, amount: Optional[float] = None) -> Dict:
        """
        Cria uma nova entrada de trade
        
        Args:
            strategy_id: ID da estratégia
            bet_type: Tipo da aposta ("even" ou "odd")
            amount: Valor da entrada (opcional)
            
        Returns:
            Dict com informações do trade criado
        """
        if strategy_id not in self.strategies:
            return {"error": "Estratégia não encontrada"}
        
        strategy = self.strategies[strategy_id]
        
        # Converte string para enum
        try:
            bet_type_enum = BetType(bet_type.lower())
        except ValueError:
            return {"error": "Tipo de aposta inválido. Use 'even' ou 'odd'"}
        
        # Verifica se pode criar mais trades
        if len(strategy.active_trades) >= strategy.max_entries:
            return {"error": "Máximo de entradas atingido"}
        
        # Cria o trade
        trade = strategy.create_trade(bet_type_enum, amount)
        
        # Atualiza trades ativos
        self.active_trades[strategy_id] = strategy.active_trades.copy()
        
        return {
            "trade_id": trade.id,
            "strategy_id": strategy_id,
            "bet_type": trade.bet_type.value,
            "amount": trade.amount,
            "entry_time": trade.entry_time.isoformat(),
            "status": trade.status.value,
            "entry_number": len(strategy.active_trades)
        }
    
    def get_strategy_info(self, strategy_id: str) -> Dict:
        """
        Retorna informações de uma estratégia
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            Dict com informações da estratégia
        """
        if strategy_id not in self.strategies:
            return {"error": "Estratégia não encontrada"}
        
        strategy = self.strategies[strategy_id]
        
        return {
            "strategy_id": strategy_id,
            "stats": strategy.get_strategy_stats(),
            "active_trades": [
                {
                    "id": trade.id,
                    "bet_type": trade.bet_type.value,
                    "amount": trade.amount,
                    "entry_time": trade.entry_time.isoformat(),
                    "status": trade.status.value
                }
                for trade in strategy.active_trades
            ],
            "current_sequence": strategy.current_sequence
        }
    
    def get_all_strategies(self) -> Dict:
        """
        Retorna informações de todas as estratégias
        
        Returns:
            Dict com todas as estratégias
        """
        return {
            strategy_id: self.get_strategy_info(strategy_id)
            for strategy_id in self.strategies.keys()
        }
    
    def reset_strategy(self, strategy_id: str) -> Dict:
        """
        Reseta uma estratégia
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            Dict com resultado da operação
        """
        if strategy_id not in self.strategies:
            return {"error": "Estratégia não encontrada"}
        
        strategy = self.strategies[strategy_id]
        strategy.reset_strategy()
        
        # Limpa trades ativos
        self.active_trades[strategy_id] = []
        
        return {
            "strategy_id": strategy_id,
            "status": "reset",
            "message": "Estratégia resetada com sucesso"
        }
    
    def cancel_active_trades(self, strategy_id: str) -> Dict:
        """
        Cancela todos os trades ativos de uma estratégia
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            Dict com resultado da operação
        """
        if strategy_id not in self.strategies:
            return {"error": "Estratégia não encontrada"}
        
        strategy = self.strategies[strategy_id]
        strategy.cancel_active_trades()
        
        # Limpa trades ativos
        self.active_trades[strategy_id] = []
        
        return {
            "strategy_id": strategy_id,
            "status": "cancelled",
            "message": "Todos os trades ativos foram cancelados"
        }
    
    def get_trade_history(self, strategy_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Retorna histórico de trades
        
        Args:
            strategy_id: ID da estratégia (opcional)
            limit: Limite de registros
            
        Returns:
            Lista com histórico de trades
        """
        history = self.trade_history
        
        if strategy_id:
            history = [trade for trade in history if trade.get("strategy_id") == strategy_id]
        
        # Retorna os últimos registros
        return history[-limit:] if limit > 0 else history
    
    def get_overall_stats(self) -> Dict:
        """
        Retorna estatísticas gerais de todas as estratégias
        
        Returns:
            Dict com estatísticas gerais
        """
        total_profit = 0.0
        total_trades = 0
        total_wins = 0
        total_active_trades = 0
        
        for strategy in self.strategies.values():
            stats = strategy.get_strategy_stats()
            total_profit += stats["total_profit"]
            total_trades += stats["total_trades"]
            total_wins += stats["winning_trades"]
            total_active_trades += stats["active_trades"]
        
        return {
            "total_profit": total_profit,
            "total_trades": total_trades,
            "total_wins": total_wins,
            "total_active_trades": total_active_trades,
            "overall_win_rate": (total_wins / total_trades * 100) if total_trades > 0 else 0,
            "total_strategies": len(self.strategies)
        }

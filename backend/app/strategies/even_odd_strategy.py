"""
Even/Odd Strategy Implementation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BetType(Enum):
    EVEN = "even"
    ODD = "odd"

class TradeStatus(Enum):
    PENDING = "pending"
    WIN = "win"
    LOSS = "loss"
    CANCELLED = "cancelled"

@dataclass
class TradeEntry:
    id: str
    bet_type: BetType
    amount: float
    entry_time: datetime
    status: TradeStatus
    result: Optional[int] = None
    profit: Optional[float] = None

@dataclass
class EvenOddStrategy:
    """Even/Odd Strategy with Martingale support"""
    
    def __init__(self, 
                 trigger_count: int = 3,
                 max_entries: int = 5,
                 base_amount: float = 1.0,
                 martingale_multiplier: float = 2.0):
        self.trigger_count = trigger_count  # Quantidade de repetições para gatilho
        self.max_entries = max_entries      # Máximo de entradas (martingales)
        self.base_amount = base_amount      # Valor base da primeira entrada
        self.martingale_multiplier = martingale_multiplier  # Multiplicador para martingale
        
        # Estado da estratégia
        self.current_sequence: List[int] = []  # Últimos resultados
        self.active_trades: List[TradeEntry] = []
        self.total_profit: float = 0.0
        self.total_trades: int = 0
        self.winning_trades: int = 0
        
    def add_tick(self, tick_value: int) -> Optional[Dict]:
        """
        Adiciona um novo tick e verifica se deve fazer uma entrada
        
        Args:
            tick_value: Valor do tick (0-9)
            
        Returns:
            Dict com informações da entrada ou None se não deve entrar
        """
        # Adiciona o tick à sequência
        self.current_sequence.append(tick_value)
        
        # Mantém apenas os últimos ticks necessários
        if len(self.current_sequence) > self.trigger_count:
            self.current_sequence = self.current_sequence[-self.trigger_count:]
        
        # Verifica se há gatilho para entrada
        if len(self.current_sequence) >= self.trigger_count:
            return self._check_trigger()
        
        return None
    
    def _check_trigger(self) -> Optional[Dict]:
        """Verifica se há gatilho para entrada baseado na sequência"""
        if len(self.current_sequence) < self.trigger_count:
            return None
            
        # Verifica se os últimos ticks são todos even ou todos odd
        last_ticks = self.current_sequence[-self.trigger_count:]
        
        # Conta quantos são even e quantos são odd
        even_count = sum(1 for tick in last_ticks if tick % 2 == 0)
        odd_count = self.trigger_count - even_count
        
        # Se todos são even, sugere entrada em odd
        if even_count == self.trigger_count:
            return {
                "trigger_type": "even_sequence",
                "suggested_bet": BetType.ODD,
                "sequence": last_ticks.copy(),
                "reason": f"Sequência de {self.trigger_count} números even detectada"
            }
        
        # Se todos são odd, sugere entrada em even
        elif odd_count == self.trigger_count:
            return {
                "trigger_type": "odd_sequence", 
                "suggested_bet": BetType.EVEN,
                "sequence": last_ticks.copy(),
                "reason": f"Sequência de {self.trigger_count} números odd detectada"
            }
        
        return None
    
    def create_trade(self, bet_type: BetType, amount: Optional[float] = None) -> TradeEntry:
        """
        Cria uma nova entrada de trade
        
        Args:
            bet_type: Tipo da aposta (even/odd)
            amount: Valor da entrada (se None, calcula baseado no martingale)
            
        Returns:
            TradeEntry criada
        """
        # Calcula o valor da entrada baseado no martingale
        if amount is None:
            entry_number = len(self.active_trades) + 1
            amount = self.base_amount * (self.martingale_multiplier ** (entry_number - 1))
        
        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_trades)}"
        
        trade = TradeEntry(
            id=trade_id,
            bet_type=bet_type,
            amount=amount,
            entry_time=datetime.now(),
            status=TradeStatus.PENDING
        )
        
        self.active_trades.append(trade)
        logger.info(f"Nova entrada criada: {trade_id} - {bet_type.value} - ${amount:.2f}")
        
        return trade
    
    def process_tick_result(self, tick_value: int) -> List[Dict]:
        """
        Processa o resultado de um tick para trades ativos
        
        Args:
            tick_value: Valor do tick (0-9)
            
        Returns:
            Lista de resultados processados
        """
        results = []
        
        for trade in self.active_trades[:]:  # Cria uma cópia para iterar
            if trade.status != TradeStatus.PENDING:
                continue
                
            # Verifica se o trade ganhou
            is_even = tick_value % 2 == 0
            trade_won = (trade.bet_type == BetType.EVEN and is_even) or \
                       (trade.bet_type == BetType.ODD and not is_even)
            
            if trade_won:
                # Trade ganhou
                trade.status = TradeStatus.WIN
                trade.result = tick_value
                trade.profit = trade.amount * 0.95  # 95% do valor apostado
                
                self.total_profit += trade.profit
                self.winning_trades += 1
                self.total_trades += 1
                
                logger.info(f"Trade {trade.id} GANHOU! Resultado: {tick_value} - Lucro: ${trade.profit:.2f}")
                
                results.append({
                    "trade_id": trade.id,
                    "status": "win",
                    "result": tick_value,
                    "profit": trade.profit,
                    "bet_type": trade.bet_type.value,
                    "amount": trade.amount
                })
                
                # Remove o trade da lista ativa
                self.active_trades.remove(trade)
                
            else:
                # Trade perdeu, verifica se deve fazer próxima entrada
                trade.status = TradeStatus.LOSS
                trade.result = tick_value
                trade.profit = -trade.amount
                
                self.total_profit += trade.profit
                self.total_trades += 1
                
                logger.info(f"Trade {trade.id} PERDEU! Resultado: {tick_value} - Perda: ${trade.amount:.2f}")
                
                results.append({
                    "trade_id": trade.id,
                    "status": "loss",
                    "result": tick_value,
                    "profit": trade.profit,
                    "bet_type": trade.bet_type.value,
                    "amount": trade.amount
                })
                
                # Remove o trade da lista ativa
                self.active_trades.remove(trade)
                
                # Verifica se deve fazer próxima entrada (martingale)
                if len(self.active_trades) < self.max_entries:
                    next_trade = self.create_trade(trade.bet_type)
                    results.append({
                        "trade_id": next_trade.id,
                        "status": "new_entry",
                        "bet_type": next_trade.bet_type.value,
                        "amount": next_trade.amount,
                        "entry_number": len(self.active_trades)
                    })
        
        return results
    
    def get_strategy_stats(self) -> Dict:
        """Retorna estatísticas da estratégia"""
        return {
            "total_profit": self.total_profit,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "win_rate": (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            "active_trades": len(self.active_trades),
            "current_sequence": self.current_sequence[-10:] if self.current_sequence else [],
            "max_entries": self.max_entries,
            "base_amount": self.base_amount,
            "martingale_multiplier": self.martingale_multiplier
        }
    
    def reset_strategy(self):
        """Reseta a estratégia"""
        self.current_sequence = []
        self.active_trades = []
        self.total_profit = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        logger.info("Estratégia resetada")
    
    def cancel_active_trades(self):
        """Cancela todos os trades ativos"""
        for trade in self.active_trades:
            trade.status = TradeStatus.CANCELLED
            trade.profit = 0.0
        
        self.active_trades = []
        logger.info("Todos os trades ativos foram cancelados")

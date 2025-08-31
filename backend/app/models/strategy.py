import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

class StrategyModel:
    def __init__(self, db_path: str = 'deriv_bot.db'):
        self.db_path = db_path
        self.init_table()

    def init_table(self):
        """Initialize the strategies table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    description TEXT,
                    trigger_count INTEGER NOT NULL,
                    max_entries INTEGER NOT NULL,
                    base_amount REAL NOT NULL,
                    martingale_multiplier REAL NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def create_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new strategy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sempre gerar ID automático
            strategy_id = self._generate_strategy_id()
            
            cursor.execute('''
                INSERT INTO strategies (
                    strategy_id, name, description, trigger_count, max_entries,
                    base_amount, martingale_multiplier, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strategy_id,
                strategy_data.get('name'),
                strategy_data.get('description'),
                strategy_data['trigger_count'],
                strategy_data['max_entries'],
                strategy_data['base_amount'],
                strategy_data['martingale_multiplier'],
                strategy_data.get('is_active', True)
            ))
            conn.commit()
            
            return self.get_strategy(strategy_id)

    def _generate_strategy_id(self) -> str:
        """Generate a unique strategy ID"""
        import uuid
        from datetime import datetime
        
        # Gerar ID baseado em timestamp + UUID curto
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"strategy_{timestamp}_{unique_id}"

    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a strategy by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, strategy_id, name, description, trigger_count, max_entries,
                       base_amount, martingale_multiplier, is_active, created_at, updated_at
                FROM strategies WHERE strategy_id = ?
            ''', (strategy_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'strategy_id': row[1],
                    'name': row[2],
                    'description': row[3],
                    'trigger_count': row[4],
                    'max_entries': row[5],
                    'base_amount': row[6],
                    'martingale_multiplier': row[7],
                    'is_active': bool(row[8]),
                    'created_at': row[9],
                    'updated_at': row[10]
                }
            return None

    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all strategies"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, strategy_id, name, description, trigger_count, max_entries,
                       base_amount, martingale_multiplier, is_active, created_at, updated_at
                FROM strategies ORDER BY created_at DESC
            ''')
            
            strategies = []
            for row in cursor.fetchall():
                strategies.append({
                    'id': row[0],
                    'strategy_id': row[1],
                    'name': row[2],
                    'description': row[3],
                    'trigger_count': row[4],
                    'max_entries': row[5],
                    'base_amount': row[6],
                    'martingale_multiplier': row[7],
                    'is_active': bool(row[8]),
                    'created_at': row[9],
                    'updated_at': row[10]
                })
            return strategies

    def update_strategy(self, strategy_id: str, strategy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a strategy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE strategies SET
                    name = ?, description = ?, trigger_count = ?, max_entries = ?,
                    base_amount = ?, martingale_multiplier = ?, is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE strategy_id = ?
            ''', (
                strategy_data.get('name'),
                strategy_data.get('description'),
                strategy_data['trigger_count'],
                strategy_data['max_entries'],
                strategy_data['base_amount'],
                strategy_data['martingale_multiplier'],
                strategy_data.get('is_active', True),
                strategy_id
            ))
            conn.commit()
            
            if cursor.rowcount > 0:
                return self.get_strategy(strategy_id)
            return None

    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM strategies WHERE strategy_id = ?', (strategy_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_active_strategies(self) -> List[Dict[str, Any]]:
        """Get all active strategies"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT strategy_id, name, description, trigger_count, max_entries,
                       base_amount, martingale_multiplier, is_active, created_at, updated_at
                FROM strategies WHERE is_active = 1 ORDER BY created_at DESC
            ''')
            
            strategies = []
            for row in cursor.fetchall():
                strategies.append({
                    'strategy_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'trigger_count': row[3],
                    'max_entries': row[4],
                    'base_amount': row[5],
                    'martingale_multiplier': row[6],
                    'is_active': bool(row[7]),
                    'created_at': row[8],
                    'updated_at': row[9]
                })
            return strategies

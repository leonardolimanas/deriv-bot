#!/usr/bin/env python3
"""
Script para migrar a tabela de estratégias para incluir o campo id auto-incremento
"""

import sqlite3
import os

def migrate_strategy_table():
    """Migra a tabela de estratégias para a nova estrutura"""
    db_path = 'deriv_bot.db'
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado. Criando nova tabela...")
        create_new_table(db_path)
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Verificar se a coluna id já existe
        cursor.execute("PRAGMA table_info(strategies)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'id' in columns:
            print("Tabela já possui a coluna id. Migração não necessária.")
            return
        
        print("Iniciando migração da tabela strategies...")
        
        # Criar tabela temporária com a nova estrutura
        cursor.execute('''
            CREATE TABLE strategies_new (
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
        
        # Copiar dados da tabela antiga para a nova
        cursor.execute('''
            INSERT INTO strategies_new (
                strategy_id, name, description, trigger_count, max_entries,
                base_amount, martingale_multiplier, is_active, created_at, updated_at
            )
            SELECT strategy_id, name, description, trigger_count, max_entries,
                   base_amount, martingale_multiplier, is_active, created_at, updated_at
            FROM strategies
        ''')
        
        # Remover tabela antiga
        cursor.execute('DROP TABLE strategies')
        
        # Renomear tabela nova
        cursor.execute('ALTER TABLE strategies_new RENAME TO strategies')
        
        conn.commit()
        print("Migração concluída com sucesso!")

def create_new_table(db_path):
    """Cria uma nova tabela de estratégias"""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE strategies (
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
        print("Nova tabela strategies criada!")

if __name__ == "__main__":
    migrate_strategy_table()

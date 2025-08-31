#!/usr/bin/env python3
"""
Script para migrar configurações padrão para o banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

def migrate_config():
    """Migrate default configurations to database."""
    print("🔄 Migrando configurações padrão para o banco de dados...")
    
    # Default settings from config.py
    default_settings = {
        # Interface settings
        'show_debug_panel': 'true',
        'auto_refresh_interval': '5000',
        'max_ticks_display': '100',
        'enable_notifications': 'true',
        'theme': 'dark',
        
        # Telegram settings
        'telegram_enabled': 'true',
        'telegram_notification_interval': '30',
        'telegram_bot_token': '7467682243:AAHs7tUE1oi0VzbE3N62z9muDhfnA9s0M4w',
        'telegram_chat_id': '-4716814208',
        
        # Deriv API settings
        'deriv_app_id': '67203',
        'deriv_api_token': 'zROkbTwuOHdTIIw',
        'deriv_api_token_real': 'av7RmoC7wwtUFNT',
        
        # Market settings
        'default_market': 'R_100'
    }
    
    # Descriptions for each setting
    descriptions = {
        'show_debug_panel': 'Exibir painel de debug no dashboard',
        'auto_refresh_interval': 'Intervalo de atualização automática (ms)',
        'max_ticks_display': 'Número máximo de ticks exibidos na tabela',
        'enable_notifications': 'Habilitar notificações',
        'theme': 'Tema da interface (dark/light)',
        'telegram_enabled': 'Habilitar notificações do Telegram',
        'telegram_notification_interval': 'Intervalo entre notificações do Telegram (segundos)',
        'telegram_bot_token': 'Token do bot do Telegram',
        'telegram_chat_id': 'ID do chat do Telegram',
        'deriv_app_id': 'ID da aplicação Deriv',
        'deriv_api_token': 'Token da API Deriv (Demo)',
        'deriv_api_token_real': 'Token real da API Deriv',
        'default_market': 'Ativo selecionado por padrão no dashboard'
    }
    
    migrated_count = 0
    updated_count = 0
    
    for key, value in default_settings.items():
        current_value = db.get_setting(key)
        
        if current_value is None:
            # Setting doesn't exist, create it
            db.set_setting(key, value, descriptions.get(key, ''))
            print(f"✅ Criado: {key} = {value}")
            migrated_count += 1
        else:
            # Setting exists, update both value and description
            db.set_setting(key, value, descriptions.get(key, ''))
            print(f"📝 Atualizado: {key} = {value} (era {current_value})")
            updated_count += 1
    
    print(f"\n🎉 Migração concluída!")
    print(f"📊 Criados: {migrated_count} configurações")
    print(f"📝 Atualizados: {updated_count} configurações")
    
    # Show current settings
    print(f"\n📋 Configurações atuais:")
    all_settings = db.get_all_settings()
    for key, value in all_settings.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    migrate_config()

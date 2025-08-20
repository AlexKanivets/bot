#!/usr/bin/env python3
"""
Простой тест импортов для модуля legal_docs
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Тестирует базовые импорты"""
    try:
        print("Тестируем базовые импорты...")
        
        # Тестируем импорт buttons
        from buttons import BACK
        print(f"✅ buttons.BACK импортирован: {BACK}")
        
        # Тестируем импорт utils
        from utils import edit_or_send_message
        print(f"✅ utils.edit_or_send_message импортирован: {edit_or_send_message}")
        
        # Тестируем импорт logger
        from logger import logger
        print(f"✅ logger импортирован: {logger}")
        
        # Тестируем импорт hooks
        from hooks.hooks import register_hook, run_hooks
        print(f"✅ hooks импортированы: {register_hook}, {run_hooks}")
        
        # Тестируем импорт hook_buttons
        from hooks.hook_buttons import insert_hook_buttons
        print(f"✅ hook_buttons.insert_hook_buttons импортирован: {insert_hook_buttons}")
        
        print("\n✅ Все базовые импорты успешны!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_legal_docs_imports():
    """Тестирует импорты модуля legal_docs"""
    try:
        print("\nТестируем импорты модуля legal_docs...")
        
        # Тестируем импорт настроек
        from legal_docs.settings import LEGAL_DOCS_ENABLED, DISPLAY_MODE
        print(f"✅ Настройки импортированы: LEGAL_DOCS_ENABLED={LEGAL_DOCS_ENABLED}, DISPLAY_MODE={DISPLAY_MODE}")
        
        # Тестируем импорт текстов
        from legal_docs.texts import LEGAL_DOCS_MENU_TEXT, LEGAL_DOCS_BUTTON
        print(f"✅ Тексты импортированы: LEGAL_DOCS_MENU_TEXT={LEGAL_DOCS_MENU_TEXT[:50]}...")
        print(f"✅ LEGAL_DOCS_BUTTON: {len(LEGAL_DOCS_BUTTON)} документов")
        
        print("\n✅ Импорты модуля legal_docs успешны!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта модуля legal_docs: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка в модуле legal_docs: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования импортов...\n")
    
    # Тестируем базовые импорты
    if not test_basic_imports():
        print("\n❌ Тест базовых импортов не прошел!")
        sys.exit(1)
    
    # Тестируем импорты модуля legal_docs
    if not test_legal_docs_imports():
        print("\n❌ Тест импортов модуля legal_docs не прошел!")
        sys.exit(1)
    
    print("\n🎉 Все тесты импортов прошли успешно!")
    print("Модуль legal_docs готов к работе с DISPLAY_MODE = 'menu'")
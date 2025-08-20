"""
Функции для работы с кнопками хуков
"""

from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any


def insert_hook_buttons(keyboard: InlineKeyboardBuilder, module_buttons: List[Dict[str, Any]]) -> InlineKeyboardBuilder:
    """
    Вставляет кнопки из модулей в существующую клавиатуру
    
    Args:
        keyboard: Существующая клавиатура
        module_buttons: Список кнопок от модулей
    
    Returns:
        Обновленная клавиатура
    """
    if not module_buttons:
        return keyboard
    
    for button_data in module_buttons:
        if not button_data:
            continue
            
        try:
            if "button" in button_data:
                # Одна кнопка
                button = button_data["button"]
                if button:
                    keyboard.row(button)
                    
            elif "buttons" in button_data:
                # Несколько кнопок в одном ряду
                buttons = button_data["buttons"]
                if buttons and isinstance(buttons, list):
                    keyboard.row(*buttons)
                    
        except Exception as e:
            # Логируем ошибку, но продолжаем обработку других кнопок
            print(f"Ошибка при вставке кнопки хука: {e}")
            continue
    
    return keyboard
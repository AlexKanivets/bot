"""
Система хуков для модулей
"""

from typing import Dict, List, Any, Callable
import asyncio

# Словарь для хранения хуков
_hooks: Dict[str, List[Callable]] = {}

def register_hook(hook_name: str, hook_function: Callable) -> None:
    """
    Регистрирует хук для указанного имени
    
    Args:
        hook_name: Имя хука
        hook_function: Функция-хук
    """
    if hook_name not in _hooks:
        _hooks[hook_name] = []
    _hooks[hook_name].append(hook_function)

async def run_hooks(hook_name: str, **kwargs) -> List[Any]:
    """
    Запускает все зарегистрированные хуки для указанного имени
    
    Args:
        hook_name: Имя хука
        **kwargs: Аргументы для передачи в хуки
    
    Returns:
        Список результатов выполнения хуков
    """
    if hook_name not in _hooks:
        return []
    
    results = []
    for hook in _hooks[hook_name]:
        try:
            if asyncio.iscoroutinefunction(hook):
                result = await hook(**kwargs)
            else:
                result = hook(**kwargs)
            if result is not None:
                results.append(result)
        except Exception as e:
            # Логируем ошибку, но продолжаем выполнение других хуков
            print(f"Ошибка в хуке {hook_name}: {e}")
            continue
    
    return results

def get_hook_count(hook_name: str) -> int:
    """
    Возвращает количество зарегистрированных хуков для указанного имени
    
    Args:
        hook_name: Имя хука
    
    Returns:
        Количество хуков
    """
    return len(_hooks.get(hook_name, []))

def clear_hooks(hook_name: str = None) -> None:
    """
    Очищает хуки
    
    Args:
        hook_name: Имя хука для очистки (если None, очищает все)
    """
    if hook_name is None:
        _hooks.clear()
    elif hook_name in _hooks:
        _hooks[hook_name].clear()
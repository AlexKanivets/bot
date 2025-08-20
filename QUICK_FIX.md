# 🚨 Быстрое исправление: команда /start не работает

## Проблема
После подключения модуля `legal_docs` команда `/start` перестала работать.

## Решение за 5 минут

### 1. Проверьте подключение модуля
```python
# В основном файле бота (main.py, bot.py или где у вас диспетчер)
from legal_docs import router

# Подключите модуль ПОСЛЕ основного роутера
dp.include_router(router)
```

### 2. Проверьте порядок подключения
```python
# ❌ НЕПРАВИЛЬНО - модуль подключается первым
from legal_docs import router
dp.include_router(router)

from handlers.start import start_router
dp.include_router(start_router)

# ✅ ПРАВИЛЬНО - модуль подключается последним
from handlers.start import start_router
dp.include_router(start_router)

from legal_docs import router
dp.include_router(router)
```

### 3. Проверьте настройки
```python
# В legal_docs/settings.py
LEGAL_DOCS_ENABLED = True
FIRST_LAUNCH_LEGAL_DOCS_ENABLED = True
```

### 4. Включите логирование
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 5. Перезапустите бота

## Если не помогло

### Вариант A: Отключите модуль временно
```python
# В legal_docs/settings.py
LEGAL_DOCS_ENABLED = False
```

### Вариант B: Используйте другой подход
```python
# В основном файле бота
from legal_docs import router

# Подключите с явным указанием приоритета
dp.include_router(router, priority=100)
```

### Вариант C: Проверьте конфликты
```python
# Выведите все подключенные роутеры
print("Подключенные роутеры:")
for router in dp.sub_routers:
    print(f"- {router.name}: {len(router.message.handlers)} обработчиков")
```

## Проверка работы

После исправления в логах должны появиться:
```
[LegalDocs] Перехвачена команда /start от пользователя X
[LegalDocs] Проверяем первого запуска для пользователя X
```

## Структура проекта
```
your_bot/
├── main.py          ← Здесь подключайте модуль
├── legal_docs/      ← Модуль
└── handlers/
    └── start.py     ← Основной роутер
```

## Поддержка
Если проблема не решается, проверьте:
1. Логи бота на наличие ошибок
2. Правильность подключения модуля
3. Порядок подключения роутеров
4. Настройки модуля
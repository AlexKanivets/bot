# Инструкция по подключению модуля legal_docs

## 🚨 Проблема: команда /start не работает

Если после подключения модуля команда `/start` не работает, выполните следующие шаги:

## 1. Проверьте подключение модуля

Убедитесь, что модуль подключен в основном файле бота:

```python
# В основном файле бота (например, main.py или bot.py)
from legal_docs import router

# Подключите роутер к диспетчеру
dp.include_router(router)
```

## 2. Проверьте порядок подключения

**ВАЖНО**: Модуль `legal_docs` должен быть подключен **ПОСЛЕ** основного роутера с командой `/start`:

```python
# Сначала подключаем основной роутер
from handlers.start import router as start_router
dp.include_router(start_router)

# Затем подключаем legal_docs
from legal_docs import router as legal_docs_router
dp.include_router(legal_docs_router)
```

## 3. Проверьте настройки модуля

Убедитесь, что в `legal_docs/settings.py` включены нужные опции:

```python
# Включить/выключить модуль
LEGAL_DOCS_ENABLED = True

# Включить/выключить показ при первом запуске
FIRST_LAUNCH_LEGAL_DOCS_ENABLED = True
```

## 4. Проверьте логи

Включите логирование и проверьте, что модуль работает:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

В логах должны появиться сообщения:
- `[LegalDocs] Перехвачена команда /start от пользователя X`
- `[LegalDocs] Проверяем первого запуска для пользователя X`

## 5. Альтернативный способ подключения

Если проблема с приоритетом, попробуйте подключить модуль с высоким приоритетом:

```python
# В основном файле бота
from legal_docs import router

# Подключаем с высоким приоритетом
dp.include_router(router, priority=100)
```

## 6. Проверьте структуру проекта

Убедитесь, что структура проекта правильная:

```
your_bot/
├── main.py (или bot.py)
├── legal_docs/
│   ├── __init__.py
│   ├── router.py
│   ├── settings.py
│   └── texts.py
└── handlers/
    └── start.py
```

## 7. Отладка

Если ничего не помогает, добавьте отладочную информацию в основной файл бота:

```python
# В основном файле бота
import logging
logging.basicConfig(level=logging.DEBUG)

# При подключении модуля
print("Подключаем модуль legal_docs...")
from legal_docs import router
dp.include_router(router)
print("Модуль legal_docs подключен")

# Проверьте, что роутер подключен
print(f"Подключенные роутеры: {[r.name for r in dp.sub_routers]}")
```

## 8. Возможные причины проблемы

1. **Модуль не подключен** - проверьте импорт и подключение
2. **Неправильный порядок** - модуль должен быть подключен после основного роутера
3. **Конфликт обработчиков** - проверьте, нет ли других обработчиков команды `/start`
4. **Ошибка в коде** - проверьте логи на наличие ошибок
5. **Проблема с базой данных** - модуль не может проверить первого запуска

## 9. Быстрая проверка

Создайте простой тест:

```python
# test_legal_docs_simple.py
from legal_docs import router

print("✅ Модуль импортирован успешно")
print(f"✅ Название роутера: {router.name}")
print(f"✅ Количество обработчиков: {len(router.message.handlers)}")

# Проверьте, что есть обработчик команды /start
start_handlers = [h for h in router.message.handlers if hasattr(h, 'filters')]
print(f"✅ Обработчики сообщений: {len(start_handlers)}")
```

## 10. Обратная связь

Если проблема не решается, предоставьте:
1. Логи бота
2. Структуру проекта
3. Код подключения модуля
4. Версию aiogram
5. Описание проблемы
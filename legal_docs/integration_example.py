"""
Пример интеграции модуля legal_docs в основной бот

Этот файл показывает, как подключить модуль юридических документов
к основному боту Telegram и настроить его.
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем роутер модуля
from legal_docs import router as legal_docs_router

# Импортируем основные роутеры (пример)
# from handlers.start import router as start_router
# from handlers.profile import router as profile_router


def configure_legal_docs():
    """Настройка модуля юридических документов"""
    
    # Импортируем настройки модуля
    from legal_docs import settings
    
    # Пример настройки для режима "menu" (по умолчанию)
    settings.DISPLAY_MODE = "menu"
    settings.LEGAL_DOCS_ENABLED = True
    settings.TERMS_URL = "https://your-domain.com/terms.html"  # Полный валидный URL
    settings.PRIVACY_URL = "https://your-domain.com/privacy.html"  # Полный валидный URL
    
    # Или настройка для режима "direct" (кнопки напрямую в разделе "О сервисе")
    # settings.DISPLAY_MODE = "direct"
    # settings.DIRECT_LAYOUT = "separate_rows"  # или "same_row"
    # settings.BUTTONS_POSITION = "before_back"
    
    # Добавление дополнительных документов
    # settings.ADDITIONAL_DOCS = [
    #     {
    #         "text": "📜 Правила использования",
    #         "url": "https://your-domain.com/rules.html"
    #     },
    #     {
    #         "text": "⚖️ Отказ от ответственности", 
    #         "url": "https://your-domain.com/disclaimer.html"
    #     }
    # ]
    
    # Настройка текстов кнопок
    # settings.LEGAL_MENU_BUTTON_TEXT = "📄 Документы"
    # settings.TERMS_BUTTON_TEXT = "📋 Соглашение"
    # settings.PRIVACY_BUTTON_TEXT = "🔒 Конфиденциальность"
    
    print("⚙️ Модуль legal_docs настроен")


async def setup_bot():
    """Настройка бота и подключение модулей"""
    
    # Настраиваем модуль юридических документов
    configure_legal_docs()
    
    # Инициализация бота
    bot = Bot(token="YOUR_BOT_TOKEN")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем основные роутеры
    # dp.include_router(start_router)
    # dp.include_router(profile_router)
    
    # Подключаем модуль юридических документов
    dp.include_router(legal_docs_router)
    
    print("✅ Модуль legal_docs подключен к боту")
    
    return bot, dp


if __name__ == "__main__":
    import asyncio
    
    async def main():
        bot, dp = await setup_bot()
        
        # Запуск бота
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()
    
    asyncio.run(main())
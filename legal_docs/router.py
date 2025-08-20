from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, WebAppInfo, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
import re

# Импорты для логирования (если hooks недоступны)
try:
    from hooks.hooks import register_hook
    from logger import logger
    HOOKS_AVAILABLE = True
except ImportError:
    HOOKS_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)


router = Router(name="legal_docs_module")


def _validate_url(url: str) -> bool:
    """Проверяет, является ли URL валидным HTTP/HTTPS адресом"""
    if not url:
        return False
    
    # Регулярное выражение для проверки HTTP/HTTPS URL
    url_pattern = re.compile(
        r'^https?://'  # http:// или https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP адрес
        r'(?::\d+)?'  # порт
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def _build_menu_button() -> InlineKeyboardButton:
    """Создает кнопку для доступа к меню юридических документов"""
    from .texts import LEGAL_MENU_BUTTON_TEXT
    return InlineKeyboardButton(text=LEGAL_MENU_BUTTON_TEXT, callback_data="legal_docs_menu")


def _build_direct_buttons() -> list[InlineKeyboardButton]:
    """Создает кнопки для прямого доступа к документам"""
    from .texts import LEGAL_DOCS_BUTTON
    
    buttons = []
    
    # Все документы из единого массива
    for doc in LEGAL_DOCS_BUTTON:
        if _validate_url(doc.get("url", "")):
            buttons.append(InlineKeyboardButton(
                text=doc["text"],
                web_app=WebAppInfo(url=doc["url"])
            ))
        else:
            logger.error(f"[LegalDocs] Невалидный URL для документа '{doc.get('text', 'Unknown')}': {doc.get('url', '')}")
    
    return buttons





@router.message(Command("start"))
async def handle_start_command(message: Message, session: AsyncSession):
    """
    Перехватывает команду /start для показа юридических документов при первом запуске
    """
    try:
        from .settings import FIRST_LAUNCH_LEGAL_DOCS_ENABLED, LEGAL_DOCS_ENABLED
        
        if not LEGAL_DOCS_ENABLED or not FIRST_LAUNCH_LEGAL_DOCS_ENABLED:
            return  # Пропускаем обработку, позволяя основному обработчику работать
        
        # Проверяем, является ли это первым запуском пользователя
        try:
            from database import get_trial, get_key_count
            user_id = message.from_user.id
            trial_status = await get_trial(session, user_id)
            key_count = await get_key_count(session, user_id)
            
            # Если у пользователя нет ключей и не активен пробный период - это первый запуск
            if key_count == 0 and trial_status == 0:
                # Показываем юридические документы
                await show_legal_docs_first_launch(message, session)
                return  # Прерываем обработку, не позволяя основному обработчику работать
                
        except Exception as e:
            logger.error(f"[LegalDocs] Ошибка проверки первого запуска: {e}")
            
        # Если это не первый запуск, пропускаем обработку
        return
        
    except Exception as e:
        logger.error(f"[LegalDocs] Ошибка обработки команды start: {e}")
        return


async def show_legal_docs_first_launch(message, session):
    """Показывает юридические документы при первом запуске"""
    try:
        from .texts import FIRST_LAUNCH_LEGAL_MESSAGE
        from .settings import FIRST_LAUNCH_LEGAL_DOCS_ENABLED
        
        if not FIRST_LAUNCH_LEGAL_DOCS_ENABLED:
            return
            
        # Создаем клавиатуру с документами и кнопкой принятия
        kb = InlineKeyboardBuilder()
        
        # Добавляем кнопки документов
        from .texts import LEGAL_DOCS_BUTTON, ACCEPT_DOCUMENTS_BUTTON
        for doc in LEGAL_DOCS_BUTTON:
            if _validate_url(doc.get("url", "")):
                kb.row(
                    InlineKeyboardButton(
                        text=doc["text"],
                        web_app=WebAppInfo(url=doc["url"])
                    )
                )
        
        # Кнопка принятия
        kb.row(
            InlineKeyboardButton(
                text=ACCEPT_DOCUMENTS_BUTTON,
                callback_data="accept_legal_docs"
                )
            )
        
        # Показываем сообщение с юридическими документами
        from handlers.utils import edit_or_send_message
        await edit_or_send_message(
            target_message=message,
            text=FIRST_LAUNCH_LEGAL_MESSAGE,
            reply_markup=kb.as_markup()
        )
        
    except Exception as e:
        logger.error(f"[LegalDocs] Ошибка показа документов при первом запуске: {e}")





async def about_vpn_hook(**kwargs):
    """
    Хук для добавления кнопок юридических документов в раздел 'О сервисе'
    """
    try:
        from .settings import LEGAL_DOCS_ENABLED, DISPLAY_MODE, DIRECT_LAYOUT
        
        if not LEGAL_DOCS_ENABLED:
            return None
            
        buttons_to_add = []
        
        if DISPLAY_MODE == "menu":
            # Режим меню - одна кнопка ведущая в подменю
            buttons_to_add.append({"button": _build_menu_button()})
            
        elif DISPLAY_MODE == "direct":
            # Прямой режим - кнопки документов сразу в разделе "О сервисе"
            direct_buttons = _build_direct_buttons()
            
            if DIRECT_LAYOUT == "same_row":
                # Все кнопки на одной строке
                buttons_to_add.append({"buttons": direct_buttons})
            else:  # separate_rows
                # Каждая кнопка на отдельной строке
                for button in direct_buttons:
                    buttons_to_add.append({"button": button})
        
        return buttons_to_add
        
    except Exception as e:
        logger.error(f"[LegalDocs] Ошибка построения кнопок: {e}")
        return None


@router.callback_query(F.data == "legal_docs_menu")
async def show_legal_docs_menu(callback: CallbackQuery):
    """Показывает меню юридических документов с кнопками для WebApp"""
    try:
        from .settings import LEGAL_DOCS_ENABLED
        from .texts import LEGAL_DOCS_MENU_TEXT, LEGAL_DOCS_BUTTON, ERROR_MODULE_DISABLED, ERROR_NO_DOCUMENTS
        from handlers.buttons import BACK
        from handlers.utils import edit_or_send_message
        
        # Проверяем, включен ли модуль
        if not LEGAL_DOCS_ENABLED:
            await edit_or_send_message(
                target_message=callback.message,
                text=ERROR_MODULE_DISABLED,
                reply_markup=InlineKeyboardBuilder().row(
                    InlineKeyboardButton(text=BACK, callback_data="about_vpn")
                ).as_markup(),
            )
            return
        
        kb = InlineKeyboardBuilder()
        
        # Все документы из единого массива
        for doc in LEGAL_DOCS_BUTTON:
            if _validate_url(doc.get("url", "")):
                kb.row(
                    InlineKeyboardButton(
                        text=doc["text"],
                        web_app=WebAppInfo(url=doc["url"])
                    )
                )
            else:
                logger.error(f"[LegalDocs] Невалидный URL для документа '{doc.get('text', 'Unknown')}': {doc.get('url', '')}")
        
        # Кнопка "Назад" в раздел "О сервисе"
        kb.row(InlineKeyboardButton(text=BACK, callback_data="about_vpn"))
        
        await edit_or_send_message(
            target_message=callback.message,
            text=LEGAL_DOCS_MENU_TEXT,
            reply_markup=kb.as_markup(),
        )
        
    except Exception as e:
        logger.error(f"[LegalDocs] Ошибка отображения меню: {e}")
        from .texts import ERROR_NO_DOCUMENTS
        from handlers.buttons import BACK
        
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text=BACK, callback_data="about_vpn"))
        
        await edit_or_send_message(
            target_message=callback.message,
            text=ERROR_NO_DOCUMENTS,
            reply_markup=kb.as_markup(),
        )


@router.callback_query(F.data == "accept_legal_docs")
async def accept_legal_documents(callback: CallbackQuery):
    """Обрабатывает принятие юридических документов"""
    try:
        from .texts import DOCUMENTS_ACCEPTED_MESSAGE
        from handlers.utils import edit_or_send_message
        
        # Отправляем сообщение об успешном принятии
        await callback.answer("✅ Документы приняты!", show_alert=False)
        
        # Показываем стандартное меню
        await edit_or_send_message(
            target_message=callback.message,
            text=DOCUMENTS_ACCEPTED_MESSAGE,
            reply_markup=None
        )
        
        # Отправляем новую команду /start для показа стандартного меню
        await callback.message.answer("/start")
        
    except Exception as e:
        logger.error(f"[LegalDocs] Ошибка принятия документов: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте еще раз.", show_alert=True)


# Регистрируем хуки (если система хуков доступна)
if HOOKS_AVAILABLE:
    register_hook("about_vpn", about_vpn_hook)
    logger.info("[LegalDocs] Модуль инициализирован, хуки зарегистрированы")
else:
    logger.warning("[LegalDocs] Система хуков недоступна, модуль инициализирован без хуков")
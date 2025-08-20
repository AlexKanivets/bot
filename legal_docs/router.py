from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
    from .settings import LEGAL_MENU_BUTTON_TEXT
    return InlineKeyboardButton(text=LEGAL_MENU_BUTTON_TEXT, callback_data="legal_docs_menu")


def _build_direct_buttons() -> list[InlineKeyboardButton]:
    """Создает кнопки для прямого доступа к документам"""
    from .settings import (
        TERMS_BUTTON_TEXT, PRIVACY_BUTTON_TEXT, 
        TERMS_URL, PRIVACY_URL, ADDITIONAL_DOCS
    )
    
    buttons = []
    
    # Основные документы
    if _validate_url(TERMS_URL):
        buttons.append(InlineKeyboardButton(
            text=TERMS_BUTTON_TEXT, 
            web_app=WebAppInfo(url=TERMS_URL)
        ))
    else:
        logger.error(f"[LegalDocs] Невалидный URL для соглашения: {TERMS_URL}")
    
    if _validate_url(PRIVACY_URL):
        buttons.append(InlineKeyboardButton(
            text=PRIVACY_BUTTON_TEXT, 
            web_app=WebAppInfo(url=PRIVACY_URL)
        ))
    else:
        logger.error(f"[LegalDocs] Невалидный URL для политики: {PRIVACY_URL}")
    
    # Дополнительные документы
    for doc in ADDITIONAL_DOCS:
        if _validate_url(doc.get("url", "")):
            buttons.append(InlineKeyboardButton(
                text=doc["text"],
                web_app=WebAppInfo(url=doc["url"])
            ))
        else:
            logger.error(f"[LegalDocs] Невалидный URL для документа '{doc.get('text', 'Unknown')}': {doc.get('url', '')}")
    
    return buttons


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
        from .settings import (
            LEGAL_DOCS_ENABLED, LEGAL_DOCS_MENU_TEXT,
            TERMS_BUTTON_TEXT, PRIVACY_BUTTON_TEXT, 
            TERMS_URL, PRIVACY_URL, ADDITIONAL_DOCS
        )
        from .texts import ERROR_MODULE_DISABLED, ERROR_NO_DOCUMENTS
        from buttons import BACK
        from utils import edit_or_send_message
        
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
        
        # Основные документы
        if _validate_url(TERMS_URL):
            kb.row(
                InlineKeyboardButton(
                    text=TERMS_BUTTON_TEXT, 
                    web_app=WebAppInfo(url=TERMS_URL)
                )
            )
        else:
            logger.error(f"[LegalDocs] Невалидный URL для соглашения: {TERMS_URL}")
        
        if _validate_url(PRIVACY_URL):
            kb.row(
                InlineKeyboardButton(
                    text=PRIVACY_BUTTON_TEXT, 
                    web_app=WebAppInfo(url=PRIVACY_URL)
                )
            )
        else:
            logger.error(f"[LegalDocs] Невалидный URL для политики: {PRIVACY_URL}")
        
        # Дополнительные документы
        for doc in ADDITIONAL_DOCS:
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
        from buttons import BACK
        
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text=BACK, callback_data="about_vpn"))
        
        await edit_or_send_message(
            target_message=callback.message,
            text=ERROR_NO_DOCUMENTS,
            reply_markup=kb.as_markup(),
        )


# Регистрируем хук для раздела "О сервисе" (если система хуков доступна)
if HOOKS_AVAILABLE:
    register_hook("about_vpn", about_vpn_hook)
    logger.info("[LegalDocs] Модуль инициализирован, хуки зарегистрированы")
else:
    logger.warning("[LegalDocs] Система хуков недоступна, модуль инициализирован без хуков")
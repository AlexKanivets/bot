from aiogram.types import Message, InlineKeyboardMarkup
import os


async def edit_or_send_message(
    target_message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup = None,
    media_path: str = None,
    force_text: bool = True
) -> Message:
    """
    Универсальная функция для отправки или редактирования сообщения.
    
    Args:
        target_message: Целевое сообщение для редактирования
        text: Текст сообщения
        reply_markup: Клавиатура (опционально)
        media_path: Путь к медиафайлу (опционально)
        force_text: Принудительно отправлять как текст (по умолчанию True)
    
    Returns:
        Объект сообщения
    """
    try:
        # Если есть медиафайл и не принуждаем к тексту
        if media_path and os.path.exists(media_path) and not force_text:
            # Пытаемся отредактировать медиа с текстом
            try:
                if hasattr(target_message, 'photo') and target_message.photo:
                    # Если сообщение уже содержит фото, редактируем его
                    await target_message.edit_media(
                        media=target_message.media,
                        reply_markup=reply_markup
                    )
                    # Отдельно редактируем текст
                    await target_message.edit_caption(
                        caption=text,
                        reply_markup=reply_markup
                    )
                else:
                    # Если нет фото, отправляем новое
                    await target_message.answer_photo(
                        photo=open(media_path, 'rb'),
                        caption=text,
                        reply_markup=reply_markup
                    )
                    # Удаляем исходное сообщение
                    await target_message.delete()
                return target_message
            except Exception as e:
                # Если не удалось отредактировать медиа, отправляем как текст
                pass
        
        # Редактируем существующее сообщение
        try:
            await target_message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
            return target_message
        except Exception:
            # Если не удалось отредактировать, отправляем новое
            new_message = await target_message.answer(
                text=text,
                reply_markup=reply_markup
            )
            # Удаляем исходное сообщение
            try:
                await target_message.delete()
            except:
                pass
            return new_message
            
    except Exception as e:
        # В случае любой ошибки, просто отправляем новое сообщение
        try:
            new_message = await target_message.answer(
                text=text,
                reply_markup=reply_markup
            )
            return new_message
        except:
            # Если и это не работает, возвращаем исходное сообщение
            return target_message
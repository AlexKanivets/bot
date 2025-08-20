from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from hooks.hooks import register_hook
from logger import logger


router = Router(name="happ_tv_module")


class HappTVStates(StatesGroup):
    waiting_for_code = State()


def _build_happ_button(key_name: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text="📺 Подключить Happ TV", callback_data=f"happ_tv|{key_name}")


async def view_key_menu_hook(key_name: str, session=None, **kwargs):
    try:
        remove_tv = {"remove": [f"connect_tv|{key_name}"], "remove_prefix": None}
        add_happ = {"button": _build_happ_button(key_name)}
        return [remove_tv, add_happ]
    except Exception as e:
        logger.error(f"[HappTV] Ошибка построения кнопки: {e}")
        return None


@router.callback_query(F.data.startswith("happ_tv|"))
async def start_happ_tv(callback: CallbackQuery, state: FSMContext):
    key_name = callback.data.split("|")[1]
    await state.update_data(key_name=key_name)
    await state.set_state(HappTVStates.waiting_for_code)

    from .texts import HAPP_TV_CODE_REQUEST
    from handlers.buttons import BACK
    from handlers.utils import edit_or_send_message

    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text=BACK, callback_data=f"happ_tv_cancel|{key_name}"))

    await edit_or_send_message(
        target_message=callback.message,
        text=HAPP_TV_CODE_REQUEST,
        reply_markup=kb.as_markup(),
    )


@router.message(F.text, HappTVStates.waiting_for_code)
async def on_code_entered(message, state: FSMContext, session):
    data = await state.get_data()
    key_name = data.get("key_name")

    from database import get_key_details
    from .texts import HAPP_TV_ERROR, HAPP_TV_INVALID_CODE, HAPP_TV_SUCCESS
    from handlers.utils import edit_or_send_message

    code = (message.text or "").strip()

    if not (len(code) == 5 and code.isalnum()):
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data=f"happ_tv_cancel|{key_name}"))
        await edit_or_send_message(target_message=message, text=HAPP_TV_INVALID_CODE, reply_markup=kb.as_markup())
        return

    record = await get_key_details(session, key_name)
    subscription_link = record.get("key") or record.get("remnawave_link")
    if not subscription_link:
        await edit_or_send_message(target_message=message, text=HAPP_TV_ERROR, reply_markup=None)
        await state.clear()
        return

    import base64
    import aiohttp

    payload = {"data": base64.b64encode(subscription_link.encode()).decode()}
    url = f"https://check.happ.su/sendtv/{code}"

    ok = False
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, json=payload, timeout=15) as resp:
                ok = resp.status == 200
                if not ok:
                    text = await resp.text()
                    logger.error(f"[HappTV] API error {resp.status}: {text}")
    except Exception as e:
        logger.error(f"[HappTV] Network error: {e}")

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data=f"happ_tv_cancel|{key_name}"))

    await edit_or_send_message(
        target_message=message,
        text=HAPP_TV_SUCCESS if ok else HAPP_TV_ERROR,
        reply_markup=kb.as_markup(),
    )

    await state.clear()


@router.callback_query(F.data.startswith("happ_tv_cancel|"))
async def happ_tv_cancel(callback: CallbackQuery, state: FSMContext, session):
    try:
        await state.clear()
    except Exception:
        pass
    key_name = callback.data.split("|")[1]

    import os
    from handlers.keys.key_view import render_key_info

    image_path = os.path.join("img", "pic_view.jpg")
    await render_key_info(callback.message, session, key_name, image_path)

register_hook("view_key_menu", view_key_menu_hook)
logger.info("[HappTV] Модуль инициализирован, хуки зарегистрированы")



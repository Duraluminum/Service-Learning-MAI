from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest

import app.keyboards as kb
from app.database.requests import add_user, toggle_notifications, get_user_notifications_enabled

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await add_user(message.from_user.id)
    await message.answer('Нажми на кнопку ниже, чтобы открыть веб-приложение', reply_markup=kb.start)


@router.message(Command('info'))
async def cmd_info(message: Message):
    await message.answer('Бот поможет тебе с планированием домашних заданий.\nДобавь задание, выставь дату сдачи, и бот пришлёт тебе уведомление' \
    ' с напоминанием.\nТы можешь настраивать уведомления в /settings', reply_markup=kb.info)


@router.message(Command('settings'))
async def cmd_settings(message: Message):
    user = await add_user(message.from_user.id)
    notifications_enabled = user.notifications
    markup = kb.get_settings_keyboard(notifications_enabled)
    await message.answer('Выбери нужный тебе пункт ниже', reply_markup=markup)


@router.callback_query(F.data == 'go_back_to_info')
async def back_to_info(callback: CallbackQuery):
    await callback.message.edit_text(text='Бот поможет тебе с планированием домашних заданий.\n'
             'Добавь задание, выставь дату сдачи, и бот пришлёт тебе уведомление'
             ' с напоминанием.\nТы можешь настраивать уведомления в /settings', reply_markup=kb.info)
    await callback.answer()


@router.callback_query((F.data == 'bot_info'))
async def bot_settings(callback: CallbackQuery):
    await callback.message.answer('Бот поможет тебе с планированием домашних заданий.\nДобавь задание, выставь дату сдачи, и бот пришлёт тебе уведомление' \
    ' с напоминанием.\nТы можешь настраивать уведомления в /settings', reply_markup=kb.info)
    await callback.answer()


@router.callback_query(F.data == 'go_to_settings')
async def bot_settings(callback: CallbackQuery):
    tg_id = callback.from_user.id
    notifications_enabled = await get_user_notifications_enabled(tg_id)
    markup = kb.get_settings_keyboard(notifications_enabled)
    await callback.message.edit_text(text='Выбери нужный тебе пункт ниже', reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.in_({'disable_notifications', 'enable_notifications'}))
async def toggle_notifications_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id
    new_state = await toggle_notifications(tg_id)
    markup = kb.get_settings_keyboard(new_state)
    current_text = callback.message.text

    try:
        await callback.message.edit_text(text=current_text, reply_markup=markup)
    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise

    status_text = 'включены' if new_state else 'отключены'
    await callback.answer(f'Уведомления {status_text}')

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest

import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Нажми на кнопку ниже, чтобы открыть веб-приложение', reply_markup=kb.start)


@router.message(Command('info'))
async def cmd_info(message: Message):
    await message.answer('Бот поможет тебе с планированием домашних заданий.\nДобавь задание, выставь дату сдачи, и бот пришлёт тебе уведомление' \
    ' с напоминанием.\nТы можешь настраивать уведомления в /settings', reply_markup=kb.info)


@router.message(Command('settings'))
async def cmd_settings(message: Message):
    await message.answer('Выбери нужный тебе пункт ниже', reply_markup=kb.settings)


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
    await callback.message.edit_text(text='Выбери нужный тебе пункт ниже', reply_markup=kb.settings)
    await callback.answer()


@router.callback_query((F.data == 'disable_notifications') | (F.data == 'enable_notifications'))
async def toggle_notifications(callback: CallbackQuery):
    current_markup = callback.message.reply_markup

    new_keyboard = []
    for row in current_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data == 'disable_notifications':
                new_button = InlineKeyboardButton(text='Включить уведомления', callback_data='enable_notifications')

            elif button.callback_data == 'enable_notifications':
                new_button = InlineKeyboardButton(text='Выключить уведомления', callback_data='disable_notifications')
            else:
                new_button = button
            new_row.append(new_button)
        new_keyboard.append(new_row)

    new_markup = InlineKeyboardMarkup(inline_keyboard=new_keyboard)

    try:
        await callback.message.edit_reply_markup(reply_markup=new_markup)
    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise

    await callback.answer('Настройки уведомлений обновлены')

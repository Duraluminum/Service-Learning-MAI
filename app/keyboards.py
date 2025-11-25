from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Message


def get_settings_keyboard(notifications_enabled: bool) -> InlineKeyboardMarkup:
    button_text = 'Отключить уведомления' if notifications_enabled else 'Включить уведомления'
    button_data = 'disable_notifications' if notifications_enabled else 'enable_notifications'
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data=button_data)],
        [InlineKeyboardButton(text='Назад', callback_data='go_back_to_info')]
    ])


start = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Открыть веб-приложение', 
                                                    web_app=WebAppInfo(url='https://duraluminum.github.io/Service-Learning-MAI/index.html'))], 
                                            [InlineKeyboardButton(text='Информация о боте',
                                                                callback_data='bot_info')]])


info = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Перейти в настройки', 
                                                                   callback_data='go_to_settings')]])


homework = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Открыть веб-приложение', 
                                                    web_app=WebAppInfo(url='https://duraluminum.github.io/Service-Learning-MAI/index.html'))]])
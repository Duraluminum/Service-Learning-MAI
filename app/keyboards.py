from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

start = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Открыть веб-приложение', 
                                                    web_app=WebAppInfo(url='https://duraluminum.github.io/Service-Learning-MAI/index.html'))], 
                                            [InlineKeyboardButton(text='Информация о боте',
                                                                callback_data='bot_info')]])


info = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Перейти в настройки', 
                                                                   callback_data='go_to_settings')]])


settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отключить уведомления', callback_data='disable_notifications')],
                                                [InlineKeyboardButton(text='Назад', callback_data='go_back_to_info')]])




from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_menu():
    menu = [
        [InlineKeyboardButton(text="Добавить тренировку", callback_data="info")],
        [InlineKeyboardButton(text="История тренировок", callback_data="history")]
    ]

    menu = InlineKeyboardMarkup(inline_keyboard=menu)
    return menu


def register_user():
    menu = [
        [InlineKeyboardButton(text="Начать ввод данных", callback_data="data")]
    ]

    menu = InlineKeyboardMarkup(inline_keyboard=menu)
    return menu


def choice_sport():
    menu = [
        [InlineKeyboardButton(text="Ходьба", callback_data="sport_walking"),
         InlineKeyboardButton(text="Бег", callback_data="sport_running"),
         InlineKeyboardButton(text="Плавание", callback_data="sport_swimming")]
    ]

    menu = InlineKeyboardMarkup(inline_keyboard=menu)
    return menu


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаем реплай-клавиатуру с кнопками в один ряд
    :param items: список строк для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row],resize_keyboard=True)


def make_2col_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаем клавиатуру категорий с кнопками в два столбца
    :param items: список строк для кнопок
    :return: объект реплай-клавиатуры
    """
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.add(KeyboardButton(text=item))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)
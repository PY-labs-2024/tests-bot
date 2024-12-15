from aiogram import html
from aiogram import types
from keyboards import make_2col_keyboard
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

default_router = Router()
start_list = ["Тест1", "Тест2", "Тест3", "Тест4", "Тест5", "Тест6"]


@default_router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение пользователю с его именем.
    :param message: объект сообщения
    :return: None
    """
    await message.answer(f"Здравствуйте, {html.quote(message.from_user.full_name)}!",
                         reply_markup=make_2col_keyboard(start_list))


# Хэндлер на выход из автомата состояний
@default_router.message(StateFilter(None), Command(commands=["cancel"]))
@default_router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    """
    Обработчик команды /cancel или текста "отмена" вне состояния.
    Сбрасывает данные состояния, но не сбрасывает само состояние.
    :param message: объект сообщения
    :param state: объект состояния
    :return: None
    """
    # Стейт сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(text="Нечего отменять",
                         reply_markup=make_2col_keyboard(start_list))


# Хэндлер на выход из автомата состояний 2
@default_router.message(Command(commands=["cancel"]))
@default_router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Обработчик команды /cancel или текста "отмена" в любом состоянии.
    Сбрасывает состояние и данные.
    :param message: объект сообщения
    :param state: объект состояния
    :return: None
    """
    await state.clear()
    await message.answer(text="Действие отменено",
                         reply_markup=make_2col_keyboard(start_list))
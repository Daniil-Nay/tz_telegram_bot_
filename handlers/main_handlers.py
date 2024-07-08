from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from lexicon_data import handlers_text

r: Router = Router()


#Основная команда при запуске бота. Возвращает информацию о боте
@r.message(Command('start'))
async def welcoming_handler(
        message: Message
) -> None:
    """
    Хэндлер, который ловит апдейты по первому запуску бота/команде start
    :param message: Текстовое сообщение, получаемое от пользователя
    :return: None
    """

    await message.answer(
        text=f'{await handlers_text(message.from_user.language_code, "start")}',
        parse_mode='html',
    )


#Команда для вывода информации о других командах в рамках реализации ТЗ.
@r.message(Command('help'))
async def help_handler(
        message: Message
) -> None:
    """
    Хэндлер, который ловит апдейты по команде help
    :param message: Текстовое сообщение, получаемое от пользователя
    :return: None
    """
    await message.answer(
        text=f'{await handlers_text(message.from_user.language_code, "help")}',
        parse_mode='html',
    )

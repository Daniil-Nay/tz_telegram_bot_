from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from gspread import Client, service_account

from async_defs import validate_date, google_sheet_processor
from aiogram.types import Message

r: Router = Router()

#Машина состояний для ввода даты (в две итерации)
class UserDateStates(StatesGroup):
    typing_data_proccess = State()


# Хэндлер по обработке команды text_input. Первая итерация подразумевает собой
# отправку сообщения с просьбой ввести дату
@r.message(Command('text_input'))
async def text_input_handler(
        message:Message,
        state: FSMContext
)->None:
    """
    Основной хэндлер по обработке апдейтов команды text_input
    :return:
    """
    await message.answer(
        text = 'введите дату для переноса в таблицу',
        parse_mode='html'
    )
    await state.set_state(UserDateStates.typing_data_proccess)


#Вторая итерация. Проверка на корректность даты и ее перенос в таблицу
@r.message(UserDateStates.typing_data_proccess)
async def text_input_handler(
        message:Message,
        state: FSMContext,
        google_sheets_client
)->None:
    """
    Сюда мы переходим после того, как была написана дата. Идет проверка и перенос в google excel
    :param message:
    :param state:
    :param google_sheets_client:
    :return:
    """
    client = google_sheets_client

    is_date: str = message.text
    # Несколько форматов для удобства.
    date_formats: list[str] = [
        "%d.%m.%y", "%d.%m.%Y",
        "%d/%m/%y", "%d/%m/%Y",
        "%d-%m-%y", "%d-%m-%Y",
        "%m.%d.%y", "%m.%d.%Y",
        "%m/%d/%y", "%m/%d/%Y",
        "%m-%d-%y", "%m-%d-%Y"
    ]
    if await validate_date(is_date, date_formats):
        result: str = await google_sheet_processor(
            sheet_info=client,
            type='writing',
            value=is_date,
            lng_code = message.from_user.language_code
        )

        await message.answer(
            text=f'Дата введена верно.\n'
                 f'{result}'
        )
        await state.clear()
    else:
        await message.answer(
            text = 'Дата введена неверно'
        )


import requests
from aiogram import types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.router import Router
from async_defs import google_sheet_processor
from lexicon_data import handlers_text
from yoomoney import Client as y_client, Quickpay

r: Router = Router()


#FSM (машина состояний) для ввода города
class MapCityStates(StatesGroup):
    typing_city_proccess = State()


#Создаю хэндлер для получения апдейтов по команде "кнопки" (с выводом кнопок 1-4 согласно тз)
@r.message(Command('buttons'))
async def buttons_handler(message: Message) -> None:
    """
    Основной хэндлер с кнопками
    :param message:
    :return:
    """
    language_code: str = message.from_user.language_code

    # Список кнопок с текстом и соответствующими callback_data
    button_data = [
        ("Map_button", "Map_button"),
        ("Payment_button", "Payment_button"),
        ("Picture_button", "Picture_button"),
        ("A2_button", "A2_button")
    ]

    # Создание InlineKeyboardButton для каждой пары (текст, callback_data)
    buttons = [
        [
            types.InlineKeyboardButton(
                text=await handlers_text(language_code, text),
                callback_data=callback_data
            )
        ] for text, callback_data in button_data
    ]

    # Создание InlineKeyboardMarkup из списка кнопок
    start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    # Отправка сообщения с клавиатурой кнопок
    await message.answer(
        await handlers_text(language_code, 'text settings'),
        reply_markup=start_keyboard,
        parse_mode='html'
    )


# коллбэк по кнопке с получением карты по адресу. Две итерации. На этой итерации я отправляю пользователю
# сообщение о написании города
@r.callback_query(F.data == 'Map_button')
async def map_button_handler(
        callback: CallbackQuery,
        state: FSMContext
) -> None:
    """
    Коллбэк по кнопке с получением адреса. Здесь происходит отправка сообщения о написании города
    :param callback:
    :param state:
    :return:
    """
    await callback.message.edit_text(
        text=await handlers_text(language_type=callback.from_user.language_code, command='writing_city_iteration_1')
    )
    await state.set_state(MapCityStates.typing_city_proccess)


# вторая итерация. Здесь я отправляю сообщение с информацией об улице в городе, который ввел пользователь
@r.message(MapCityStates.typing_city_proccess)
async def city_input_handler(
        message: Message,
        state: FSMContext
) -> None:
    """
    Вторая функция, которая уже отправляет адрес (если он есть)
    :param message:
    :param state:
    :return:
    """
    try:
        address: str = "Ленина 1"
        city: str = message.text.split()[-1]
        yandex_maps_url: str = f"https://yandex.ru/maps/?text={address}%20{city}"
        msg_text: str = await handlers_text(
            language_type=message.from_user.language_code,
            command='writing_city_iteration_2'
        )
        await message.answer(
            text=msg_text.format(address=address, city=city, yandex_maps_url=yandex_maps_url),
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Ошибка в обработчике ввода города: {e}")
    finally:
        await state.clear()


# Кнопка с оплатой. Выводит ссылку на оплату в 2 рубля
@r.callback_query(F.data == "Payment_button")
async def payment_button_handler(
        callback: CallbackQuery,
        payment_data
) -> None:
    """
    Функция по оплате
    :param callback:
    :param payment_data:
    :return:
    """
    try:
        label: str = 'test_payment_123'
        quickpay = Quickpay(
            receiver=payment_data.receiver_card,
            quickpay_form="shop",
            targets="Оплата за тестовый товар",
            paymentType="SB",
            sum=2.00,
            label=label,
            successURL="https://example.com/success"
        )
        # ссылка на оплату (url), которая должна храниться в env

        payment_link: str = quickpay.redirected_url
        msg_text: str = await handlers_text(
            language_type=callback.from_user.language_code,
            command='payment_button_iteration_1'
        )
        await callback.message.edit_text(
            text=msg_text.format(payment_link=payment_link),
            parse_mode='Markdown'
        )

        client = y_client(payment_data.payment_token)
        operation_history = client.operation_history(label=label)
        msg_success: str = await handlers_text(
            language_type=callback.from_user.language_code,
            command='payment_success'
        )
        if operation_history.operations and operation_history.operations[0].status == "success":
            await callback.message.edit_text(
                text=msg_success
            )
    except Exception as e:
        msg_failure: str = await handlers_text(
            language_type=callback.from_user.language_code,
            command='payment_failure'
        )
        print(f"Ошибка при создании или отправке ссылки на оплату: {e}")
        await callback.message.edit_text(
            text=msg_failure
        )


# Кнопка с выводом картинки котинка! С помощью сервиса с котиками
@r.callback_query(F.data == "Picture_button")
async def picture_button_handler(
        callback: CallbackQuery,
        bot: Bot,
        other_data,
) -> None:
    """
    Функция по отправке картинки (посчитал, что лучше обратиться к сервису, чем отправлять одну и ту же картинку)
    :param callback:
    :param bot:
    :param other_data:
    :return:
    """
    error_text: str = await handlers_text(
        language_type=callback.from_user.language_code,
        command='error_text_cats_picture'
    )
    try:
        caption_text: str = await handlers_text(
            language_type=callback.from_user.language_code,
            command='cats_picture'
        )
        cat_response = requests.get(other_data.cat_API_URL)
        if cat_response.status_code == 200:
            cat_link = cat_response.json()[0]['url']
            await callback.message.delete()
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=cat_link,
                caption=caption_text
            )
    except Exception as e:
        print(f"Ошибка при получении или отправке фото: {e}")
        await callback.message.edit_text(
            text=error_text
        )


# Кнопка для вывода информации из ячейки А2 (Выводит None в случае отсутствия данных в ячейке)
@r.callback_query(F.data == "A2_button")
async def back_request(
        callback: CallbackQuery,
        google_sheets_client,

):
    """
    функция по чтению ячейки а2 из гугл таблицы. Возвращает данные ячейки
    :param callback:
    :param google_sheets_client:
    :return:
    """
    client = google_sheets_client
    result: str = await google_sheet_processor(
        sheet_info=client,
        type='reading',
        cell='A2',
        lng_code=callback.from_user.language_code
    )
    await callback.message.edit_text(
        text=f'{result}',
        parse_mode='html'
    )

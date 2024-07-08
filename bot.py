import asyncio
from aiogram import Bot, Dispatcher
from config import load_config
from handlers import main_handlers, button_tz_handlers, g_excel_tz_handler
from middlewares import InjectMiddleware


async def main(

) -> None:
    """
    Главная функция по запуску бота.
    Здесь инициализируются роутеры (с хэндлерами), а сам бот запускается.
    :return:
    """
    config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token)
    dp: Dispatcher = Dispatcher()
    g_excel_tz_handler.r.message.middleware.register(InjectMiddleware(google_sheets_client=config.google_sheets))
    button_tz_handlers.r.message.middleware.register(InjectMiddleware(google_sheets_client=config.google_sheets))
    button_tz_handlers.r.callback_query.middleware.register(InjectMiddleware(google_sheets_client=config.google_sheets,
                                                                             other_data=config.other_data,
                                                                             payment_data=config.payment_data
                                                                             ))
    dp.include_routers(main_handlers.r, button_tz_handlers.r, g_excel_tz_handler.r)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

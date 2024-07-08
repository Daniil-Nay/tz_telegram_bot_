from dataclasses import dataclass
from os import getenv
from pathlib import Path
from dotenv import load_dotenv


# Создаю несколько классов в зависимости от того, какие это данные (В целом, это нужно для сокрытия данных)
@dataclass
class TgBot:
    token: str
    creator_id: int


@dataclass
class OtherData:
    bot_API_URL: str
    cat_API_URL: str


@dataclass
class GoogleSheets:
    credentials_path: Path
    sheet_name: str


@dataclass
class PaymentData:
    payment_token: str
    receiver_card: str


@dataclass
class Config:
    tg_bot: TgBot
    google_sheets: GoogleSheets
    payment_data: PaymentData
    other_data: OtherData


# Загрузка конфига, здесь я получаю из .env данные (токены, ID, URL). Все то, что не должно лежать в открытом доступе.
def load_config(

) -> Config:
    """
    Конфигурация бота.
    :return:
    """
    load_dotenv()
    tg_bot_config = TgBot(
        token=getenv('TG_BOT_TOKEN'),
        creator_id=int(getenv('CREATOR_ID'))
    )

    google_sheets_config = GoogleSheets(
        credentials_path=Path(getenv('GOOGLE_SHEETS_CREDENTIALS')).resolve(),
        sheet_name=getenv('SHEET_NAME')
    )

    other_data_config = OtherData(
        bot_API_URL=getenv('BOT_API_URL'),
        cat_API_URL=getenv('CAT_API_URL')
    )

    payment_data_config = PaymentData(
        payment_token=getenv('PAYMENT_TOKEN'),
        receiver_card=getenv('RECEIVER_CARD')
    )
    return Config(
        tg_bot=tg_bot_config,
        google_sheets=google_sheets_config,
        other_data=other_data_config,
        payment_data=payment_data_config
    )

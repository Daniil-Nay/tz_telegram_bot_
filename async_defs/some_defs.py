import datetime
from typing import Any

from gspread import service_account

from lexicon_data import handlers_text


# Асинхронная функция для проверки соответствия на дату
async def validate_date(
        date_str: str,
        formats: list
) -> bool:
    """Проверка даты по списку форматов."""
    for date_format in formats:
        try:
            datetime.datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            continue
    return False


# Асинхронная функция, которая заполняет или считывает google excel.
async def google_sheet_processor(
        sheet_info,
        type: str,
        value: Any = None,
        cell: str = 'A2',
        lng_code: str = 'ru'
) -> str:
    """
    Асинхронная функция, которая получает в качестве параметров данные о google excel таблице и тип операции
    (Считывание или заполнение)
    :param sheet_info: информацие о листе
    :param type: тип операции
    :param value: значение в ячейку
    :param cell: ячейка
    :param lng_code: языковой код
    :return: str, вывод по результату взаимодействия с таблицей
    """
    client = sheet_info.credentials_path
    client = service_account(filename=client)
    table = client.open_by_url(sheet_info.sheet_name)
    worksheet = table.worksheets()[0]
    match type:
        case "reading":
            cell_value = worksheet.acell(cell).value
            print(f'Value in cell {cell}: {cell_value}')
            return cell_value
        case "writing":
            worksheet.update_acell(
                label=cell,
                value=value)
            success_message = await handlers_text(lng_code, 'google_excel_successfull')
            return success_message.format(table=table, worksheet=worksheet, cell=cell)

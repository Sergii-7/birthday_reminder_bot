from asyncio import sleep

from src.sql.func_system_db import get_system_data
from src.dir_schedule.some_task import BackgroundTask
from src.service.service_tools import correct_time
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


async def check_schedule(seconds: int = 25):
    """Check schedule every int: seconds"""
    background_task = BackgroundTask()
    while True:
        """ Дані для запуску перевірки дат народження користувачів, які долучені до подій """
        doc = await get_system_data(title='check_birthday')
        days_to_birthday = doc.data_digital if doc and doc.data_digital else 10
        time_to_check_birthday = doc.data_text if doc and doc.data_text else "08:00"
        """ Дані длі запуску перевірки reports """
        # doc_report = await get_system_data(title='check_report')
        # time_to_check_report = doc_report.data_text if doc_report and doc_report.data_text else "15:00"
        time_now = correct_time()
        try:
            logger.debug(f"⏱ Time now: {time_now}, waiting for {time_to_check_birthday}")
            if str(time_now)[11:16] == time_to_check_birthday:
                await background_task.check_users_birthday(days_to_birthday=days_to_birthday)
                await sleep(delay=60)
        except Exception as e:
            logger.exception("⛔ Error during check_users_birthday: %s", str(e))
        await sleep(delay=seconds)
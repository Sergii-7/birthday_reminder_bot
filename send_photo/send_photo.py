# send_photo.py
import asyncio
from pathlib import Path

from aiogram.types import FSInputFile

from config import GROUP_R_D
from src.bot_app.create_bot import bot  # тут має бути ініціалізований Bot(...)

# ⚙️ Налаштуй шлях до файлу (фото лежить поруч зі скриптом)
IMAGE_NAME = "2025-10-11 20.13.34.jpg"
IMAGE_PATH = Path(__file__).with_name(IMAGE_NAME)  # ./send_photo.py + файл поруч

CHAT_ID = GROUP_R_D


async def send_image():
    # 1) Переконайся, що файл існує
    if not IMAGE_PATH.exists():
        # Для дебага: покажемо поточну директорію та вміст
        cwd = Path.cwd()
        raise FileNotFoundError(
            f"Файл не знайдено: {IMAGE_PATH}\n"
            f"Поточна директорія: {cwd}\n"
            f"У ній є: {[p.name for p in cwd.iterdir()]}"
        )

    # 2) Відправляємо як локальний файл
    photo = FSInputFile(str(IMAGE_PATH))  # str() важливий для aiogram на деяких платформах
    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=photo,
        caption="🔥",
    )


async def main():
    try:
        await send_image()
    finally:
        # 3) Коректно закриємо HTTP-сесію aiogram, щоб не було "Unclosed client session"
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

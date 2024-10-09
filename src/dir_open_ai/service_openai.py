import base64
import os
from typing import Optional
from src.service.loggers.py_logger_openai import get_logger

logger = get_logger(__name__)


def encode_image(image_path: str) -> Optional[str]:
    """ Function to encode the image """
    try:
        logger.debug(f"encode_image(image_path={image_path})")
        # Перевіряємо, чи існує файл
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File not found: {image_path}")
        # Перевіряємо, чи файл є дійсним файлом і чи він не порожній
        if not os.path.isfile(image_path) or os.path.getsize(image_path) == 0:
            raise ValueError(f"File is invalid or empty: {image_path}")
        # Читаємо зображення у бінарному режимі
        with open(file=image_path, mode="rb") as img_file:
            encoded_string = base64.b64encode(img_file.read())
        # Повертаємо рядок у форматі base64
        return encoded_string.decode("utf-8")
    except FileNotFoundError as fnf_error:
        logger.error(fnf_error)
    except ValueError as val_error:
        logger.error(val_error)
    except Exception as e:
        logger.error(e)
    return None

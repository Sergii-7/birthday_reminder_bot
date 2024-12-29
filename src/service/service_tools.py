from datetime import datetime
import pytz, secrets, string, random
from stdnum.luhn import is_valid
import phonenumbers

from src.sql.models import User


def correct_time(timezone_: str = 'Europe/Kyiv') -> datetime:
    """ Back time now 'Europe/Kyiv': object=datetime """
    return datetime.now(tz=pytz.timezone(timezone_)).replace(tzinfo=None)


def generate_users_password():
    """Генеруємо 'password' для 'user', безпечний для передачі через URL."""
    characters = string.ascii_letters + string.digits  # Всі латинські літери (малі та великі) + цифри
    n = random.choice([25, 26, 27, 28, 29, 30])  # Довжина пароля
    password = ''.join(secrets.choice(characters) for _ in range(n))  # Генеруємо пароль з випадкових символів
    return password


def check_card_number(card_number: str) -> bool:
    """ Check card number """
    # card_number = "4111 1111 1111 1111"  # Приклад номера Visa
    if is_valid(card_number):
        return True
    else:
        return False


def validate_phone(phone_number: str) -> str | None:
    """ Перевіряємо валідність номера телефону. """
    try:
        parsed_number = phonenumbers.parse(number=phone_number, region=None)
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        if phonenumbers.is_valid_number(parsed_number):
            return formatted_number
    except:
        pass
    return


def user_data(user: User, is_birthday: bool = True) -> str:
    """Create text data about User by Data from Telegram."""
    last_name = f"\n{user.last_name}" if user.last_name else ""
    username = f"\n@{user.username}" if user.username else ""
    phone_number = f"\n{user.phone_number}" if user.phone_number else ""
    if is_birthday:
        birthday = f"\nдата народження (місяць-день): {str(user.birthday)[5:]}" if user.birthday else ""
        data_text = f"<u>іменинник(іменинниця)</u>:\n{user.first_name}{last_name}{username}{phone_number}{birthday}"
    else:
        data_text = f"{user.first_name}{last_name}{username}{phone_number}"
    return data_text

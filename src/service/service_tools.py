from datetime import datetime
import pytz, secrets, string, random
from stdnum.luhn import is_valid


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
    """ Check_card_number """
    # card_number = "4111 1111 1111 1111"  # Приклад номера Visa
    if is_valid(card_number):
        print("Номер картки валідний!")
        return True
    else:
        print("Номер картки невалідний!")
        return False
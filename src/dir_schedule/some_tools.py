from typing import Any, Dict, List, Optional

from src.bot_app.create_bot import bot
from src.bot_app.dir_service.bot_service import send_compressed_image
from src.dir_open_ai.open_ai_tools import ResponseImageAI, ResponseTextAI
from src.service.create_data import user_data
from src.service.loggers.py_logger_tel_bot import get_logger
from src.sql.func_db import create_new_doc, get_doc_by_id, get_report
from src.sql.models import Chat, Holiday, Report, User, UserChat

logger = get_logger(__name__)


class DataAI:
    async def get_title(self, chat: Chat) -> str:
        """Get title of Group"""
        try:
            chat_data = await bot.get_chat(chat_id=chat.chat_id)
            title = chat_data.title
        except Exception as e:
            logger.error(e)
            title = "Аврора"
        return title

    def get_prompt_for_greet_birthday_user(self, first_name: str, title: str) -> Dict[str, str]:
        """Get prompt for birthday_user"""
        get_text_ai = (
            f"Напиши привітання з днем народження для {first_name} від імені команди "
            f"{title}. Привітання має бути дружнім і теплим, побажання стосуватимуться здоров'я, "
            f"успіху в роботі та особистого щастя. Має бути лише привітання і нічого зайвого."
        )
        get_image_ai = (
            f"Зробіть зображення, яким ми зможемо привітати свого колегу по роботі "
            f"{first_name} від імені колективу {title}."
        )
        return {"get_text_ai": get_text_ai, "get_image_ai": get_image_ai}

    def if_error_ai_get_text_for_birthday_user(self, first_name: str, title: str) -> str:
        """If error with AI - create own content for greet user"""
        text = (
            f"Дорогий {first_name}!\n\nВітаємо тебе з цим чудовим днем і бажаємо тільки найкращого! "
            f"Ти – невід'ємна частина нашої команди, і твоя праця надихає кожного з нас. "
            f"Нехай у твоєму житті буде багато успіхів, нових досягнень і яскравих моментів.\n\n"
            f"Бажаємо натхнення, сил і безмежної енергії для нових звершень! Ми раді працювати з тобою "
            f"і цінуємо твій вклад у спільну справу.\n\nЗ найкращими побажаннями,\nКолектив {title}"
        )
        return text

    def get_prompt_for_asking_money(
        self,
        first_name: str,
        title: str,
        amount: int,
        birthday_user_name: str,
        days_to_birthday: int,
        user_data: Optional[str] = None,
        user_birthday_data: Optional[str] = None,
    ) -> Dict[str, str]:
        """Get prompt for asking money from member of chat"""
        user_data = user_data if user_data else first_name
        user_birthday_data = user_birthday_data if user_birthday_data else birthday_user_name
        get_text_ai = (
            f"Напиши дружнє і чемне повідомлення для\n{user_data}\nвід імені команди {title}. "
            f"У повідомленні попроси його скинутися {amount} грн, бо всі члени команди збирають гроші, щоб "
            f"зробити подарунок для {user_birthday_data}, у якого день народження за {days_to_birthday} "
            f"днів. Повідомлення повинно бути легким і доброзичливим, а також містити подяку за підтримку. "
            f"Має бути лише повідомлення і нічого зайвого."
        )
        get_image_ai = (
            f"Зробіть зображення, в якому команда {title} просить колегу\n{user_data}\nскинутися {amount} "
            f"грн, бо всі члени команди збирають гроші, щоб зробити подарунок для\n{user_birthday_data}."
        )
        return {"get_text_ai": get_text_ai, "get_image_ai": get_image_ai}

    def if_error_ai_get_text_for_asking_money(
        self,
        first_name: str,
        title: str,
        amount: int,
        birthday_user_name: str,
        days_to_birthday: int,
        birthday_user: Optional[User] = None,
    ) -> str:
        """If error with AI - create own content for asking money."""
        if birthday_user:
            data_b_user = user_data(user=birthday_user, is_birthday=True)
            text = (
                f"Привіт, {first_name}!\n\nКоманда Аврора збирається зробити подарунок для:\n{data_b_user}\n\n"
                f"Всі скидаються по {amount} грн, і було б чудово, якби ти теж міг долучитися до цієї ініціативи."
                f"\nЗаздалегідь дякуємо за твою підтримку!\n\nЗ найкращими побажаннями,\nКоманда {title}"
            )
        else:
            text = (
                f"Привіт, {first_name}!\n\nКоманда Аврора збирається зробити подарунок для "
                f"{birthday_user_name}, у якого день народження через {days_to_birthday} днів. "
                f"Всі скидаються по {amount} грн, і було б чудово, якби ти теж міг долучитися до цієї ініціативи."
                f"\nЗаздалегідь дякуємо за твою підтримку!\n\nЗ найкращими побажаннями,\nКоманда {title}"
            )
        return text


class GreetingsUser:
    """Greetings to the user"""

    async def to_group(self, get_text_ai: str, get_image_ai: str, chat: Chat, user: User, title: str):
        """AI sends Greetings to the user group"""
        logger.debug(f">>> GreetingsUser().to_group()")
        data_from_ai = await ResponseTextAI(prompt_for_ai=get_text_ai).get_content()
        if isinstance(data_from_ai, dict) and "content" in data_from_ai:
            text = data_from_ai["content"]
        else:
            text = DataAI().if_error_ai_get_text_for_birthday_user(first_name=user.first_name, title=title)
        data_image = await ResponseImageAI().get_image_from_ai(prompt_for_ai=get_image_ai)
        if isinstance(data_image, dict) and "image_url" in data_image:
            image_url = data_image["image_url"]
            filename = f"image_for_{chat.id}.jpg"
            res: bool = await send_compressed_image(
                chat_id=chat.chat_id,
                filename=filename,
                caption=text,
                disable_notification=False,
                url=image_url,
                reply_markup=None,
            )
            if not res:
                res: bool = await send_compressed_image(
                    chat_id=user.telegram_id,
                    filename=filename,
                    caption=text,
                    disable_notification=False,
                    url=image_url,
                    reply_markup=None,
                )
        else:
            try:
                await bot.send_message(chat_id=chat.chat_id, text=text)
            except Exception as e:
                logger.error(e)
                await bot.send_message(chat_id=user.telegram_id, text=text)

    async def start_greet(self, user_chat: UserChat):
        """Start Greeting User"""
        chat: Optional[Chat] = await get_doc_by_id(model="chat", doc_id=user_chat.chat_id)
        data_for_ai = DataAI()
        title = await data_for_ai.get_title(chat=chat)
        prompts_ai = data_for_ai.get_prompt_for_greet_birthday_user(first_name=user_chat.user.first_name, title=title)
        get_text_ai = prompts_ai["get_text_ai"]
        get_image_ai = prompts_ai["get_image_ai"]
        try:
            logger.debug(f"send greet")
            await self.to_group(
                get_text_ai=get_text_ai, get_image_ai=get_image_ai, chat=chat, user=user_chat.user, title=title
            )
            logger.info(
                f"user {user_chat.user.first_name} | {user_chat.user.telegram_id} was congratulated on his birthday"
            )
        except Exception as e:
            logger.error(e)


class AskingMoney:
    """Asking for money from chat users"""

    async def to_user(
        self,
        get_text_ai: str,
        get_image_ai: str,
        user: User,
        title: str,
        amount: int,
        birthday_user_name: str,
        days_to_birthday: int,
        card_number: str,
        birthday_user: Optional[User] = None,
    ):
        """AI sends Greetings to the user group"""
        logger.debug(f">>> AskingMoney().to_user()")
        data_from_ai = await ResponseTextAI(prompt_for_ai=get_text_ai).get_content()
        if isinstance(data_from_ai, dict) and "content" in data_from_ai:
            text = data_from_ai["content"]
        else:
            text = DataAI().if_error_ai_get_text_for_asking_money(
                first_name=user.first_name,
                title=title,
                amount=amount,
                birthday_user_name=birthday_user_name,
                days_to_birthday=days_to_birthday,
                birthday_user=birthday_user,
            )
        if birthday_user:
            cv = user_data(user=birthday_user, is_birthday=True)
            text = text + f"\n\n{cv}\nкарта для перерахування внеску: <code>{card_number}</code>"
        else:
            text = text + f"\n\nкарта для перерахування внеску: <code>{card_number}</code>"
        data_image = await ResponseImageAI().get_image_from_ai(prompt_for_ai=get_image_ai)
        if isinstance(data_image, dict) and "image_url" in data_image:
            image_url = data_image["image_url"]
            filename = f"image_for_{user.id}.jpg"
            await send_compressed_image(
                chat_id=user.telegram_id,
                filename=filename,
                caption=text,
                disable_notification=False,
                url=image_url,
                reply_markup=None,
            )
        else:
            await bot.send_message(chat_id=user.telegram_id, text=text)

    async def start_asking(
        self, birthday_user: User, users_chats: List[UserChat], days_to_birthday: int, holiday: Holiday
    ):
        """Start Send asking for money to users"""
        for user_chat in users_chats:
            if user_chat.status:
                """User take part in chat party"""
                if user_chat.user_telegram_id != birthday_user.telegram_id:
                    """Order the text and image from AI for user"""
                    chat: Optional[Chat] = await get_doc_by_id(model="chat", doc_id=user_chat.chat_id)
                    report: Report = await get_report(user_pk=user_chat.user.id, chat_pk=chat.id, holiday_pk=holiday.id)
                    if report:
                        ask_money = False if report.status else True
                    else:
                        ask_money = True
                        report: Dict[str, Any] = {
                            "user_id": user_chat.user.id,
                            "chat_id": chat.id,
                            "holiday_id": holiday.id,
                        }
                        await create_new_doc(model="report", data=report)
                        # report = await get_report(user_pk=user_chat.user.id, chat_pk=chat.id, holiday_pk=holiday.id)
                    if ask_money:
                        """Start process asking_money"""
                        data_for_ai = DataAI()
                        title = await data_for_ai.get_title(chat=chat)
                        prompts_ai = data_for_ai.get_prompt_for_asking_money(
                            first_name=user_chat.user.first_name,
                            title=title,
                            amount=holiday.amount,
                            birthday_user_name=birthday_user.first_name,
                            days_to_birthday=days_to_birthday,
                            user_data=user_data(user=user_chat.user, is_birthday=False),
                            user_birthday_data=user_data(user=birthday_user, is_birthday=True),
                        )
                        get_text_ai = prompts_ai["get_text_ai"]
                        get_image_ai = prompts_ai["get_image_ai"]
                        try:
                            logger.debug("send asking money to_user")
                            await self.to_user(
                                get_text_ai=get_text_ai,
                                get_image_ai=get_image_ai,
                                user=user_chat.user,
                                title=title,
                                amount=holiday.amount,
                                birthday_user_name=birthday_user.first_name,
                                days_to_birthday=days_to_birthday,
                                card_number=chat.card_number,
                            )
                        except Exception as e:
                            logger.error(e)

import asyncio
from bson import ObjectId
from pymongo.results import UpdateResult
from typing import List, Dict, Any, Optional, Union

from src.mongo_db.connect import db
from src.mongo_db.pydantic_model import UserModel
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


class User:
    """ Class User for working with MongoDB """
    def __init__(self, telegram_id: int) -> None:
        self.telegram_id = telegram_id
        self._id = None
        self.first_name = None
        self.last_name = None
        self.username = None
        self.language_code = None
        self.created_at = None
        self.phone_number = None
        self.birthday = None
        self.status = None
        self.info = None

    async def find_user(self,) -> bool:
        user = await db.Users.find_one({'telegram_id': self.telegram_id})
        if user is None:
            return False
        self._id = str(user['_id'])
        self.telegram_id = self.telegram_id
        self.first_name = user['first_name']
        self.last_name = user.get('last_name')
        self.username = user.get('username')
        self.language_code = user.get('language_code')
        self.created_at = user.get('created_at')
        self.phone_number = user.get('phone_number')
        self.birthday = user.get('birthday')
        self.status = user.get('status')
        self.info = user.get('info')
        return True

    async def get_user_by_id(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Пошук користувача за ObjectId."""
        user = await db.Users.find_one({'_id': ObjectId(object_id)})
        return user

    async def insert_user(self, **kwargs) -> Optional[bool]:
        if await self.find_user():
            logger.error(f"User with telegram_id {self.telegram_id} already exists.")
            return False
        try:
            user_data = UserModel(telegram_id=self.telegram_id, **kwargs).dict()
            res = await db.Users.insert_one(document=user_data)
            logger.info(f"User created with ID {res.inserted_id}")
            return res.acknowledged
        except Exception as e:
            logger.error(f"Error while inserting user: {e}")
            return False

    async def update_user(self, data: Dict[str, Optional[Any]]) -> UpdateResult:
        """Змінюємо та/або додаємо дані в документі."""
        res: UpdateResult = await db.Users.update_one(
            {"telegram_id": self.telegram_id}, {"$set": data}
        )
        await self.find_user()
        return res

    async def get_users(self, data_search: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all users from Users collection."""
        if data_search:
            cursor = db.Users.find(data_search)
        else:
            cursor = db.Users.find()
        users = await cursor.to_list(length=None)
        return users

    async def _delete_user(self) -> bool:
        """Видаляємо користувача за telegram_id."""
        res = await db.Users.delete_one({'telegram_id': self.telegram_id})
        logger.info(msg=f"Deleted user with telegram_id: {self.telegram_id}, count: {res.deleted_count}")
        return res.deleted_count > 0


async def testing():
    """Testing this module."""
    # items = await Item().get_items(type_report='only_categories')
    # print(items)
    user = User(telegram_id=620527199)
    res = await user.find_user()
    print(res)
    print(user._id)
    res = await user.update_user(
        data={'username': 'username', 'last_name': 'Бешляга', 'first_name': 'Сергій', 'info': 'test'})
    # users = await user.get_users()
    users = await user.get_users({'telegram_id': 620527199})
    print(users)

# asyncio.run(main=testing())
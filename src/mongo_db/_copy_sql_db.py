import asyncio
from datetime import datetime, time
from typing import List, Optional, Union

from src.mongo_db.connect import db
from src.mongo_db.model import User
from src.sql import func_db


async def transfer_users():
    """Transfer docs from PostgreSQL to MongoDB."""
    # 'user': User, 'user_login': UserLogin, 'user_chat': UserChat, 'chat': Chat, 'holiday': Holiday, 'report': Report
    docs = await func_db.get_all_docs(model='user')
    [await User(telegram_id=doc.telegram_id).insert_user(
        first_name=doc.first_name,
        last_name=doc.last_name,
        username=doc.username,
        language_code=doc.language_code,
        created_at=doc.created_at,
        phone_number=doc.phone_number,
        birthday=datetime.combine(doc.birthday, time.min) if doc.birthday else None,
        status=doc.status,
        info=doc.info
    ) for doc in docs]


async def working():
    """Func for some operations."""
    ...

# asyncio.run(main=working())

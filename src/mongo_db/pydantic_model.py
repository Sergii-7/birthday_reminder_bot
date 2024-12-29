from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from src.service.service_tools import correct_time


class UserModel(BaseModel):
    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    created_at: datetime = Field(default_factory=correct_time)
    phone_number: Optional[str] = None
    birthday: Optional[datetime] = None
    status: Optional[bool] = False
    info: Optional[str] = None

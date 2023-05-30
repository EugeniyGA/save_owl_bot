from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class AppealModel:
    appeal_id: Optional[int] = None
    fullname: Optional[str] = None
    username: Optional[str] = None
    telegram_id: Optional[int] = None
    address: Optional[str] = None
    animal: Optional[str] = None
    count_animal: Optional[int] = None
    contact: Optional[str] = None
    media: Optional[bool] = None
    date_create: Optional[datetime] = None
    status: Optional[str] = None
    answer: Optional[str] = None
    channel_message_id: Optional[int] = None

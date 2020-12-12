from typing import List, Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    question: str
    answer: Optional[str] = None


class Item(ItemBase):
    id: int
    card_id: int

    class Config:
        orm_mode = True


class CardBase(BaseModel):
    card_name: str


class Card(CardBase):
    id: int

    user_id: int
    items: List[Item] = []

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    telegram_id: str


class User(BaseModel):
    id: int
    telegram_id: str
    cards: List[Card] = []

    class Config:
        orm_mode = True

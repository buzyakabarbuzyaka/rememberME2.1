from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.orm.database import Base, engine


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    cards = relationship("Card", back_populates="user")


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    card_name = Column(String, index=True)  # TODO: add uniqueness to user_id, card_name

    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="cards", passive_deletes=False)

    items = relationship("Item", back_populates="card")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete='CASCADE'))

    question = Column(String, nullable=False, index=True)  # TODO: add uniqueness to question, card_id
    answer = Column(String)

    card = relationship("Card", back_populates="items", passive_deletes=False)

Base.metadata.create_all(bind=engine)
if __name__ == '__main__':
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
# from .credit_card_model import CreditCard
from models import db
from models.user_friends import Friends

class User(db.Model):
    __tablename__ = 'user'
    
    dni = Column(String(36), primary_key=True, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    pwd = Column(String(255), nullable=False)  # Se debe hashear la contraseña
    birth_date = Column(Date, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    image = Column(String(255), nullable=True)
    amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    administrator = Column(Boolean, default=False, nullable=False)
    created_at = Column(Date, default=datetime.utcnow, nullable=False)
    updated_at = Column(Date, onupdate=datetime.utcnow)
    phone =  Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    
    # Define a relationship to CreditCard (one-to-many)
    credit_cards = relationship('CreditCard', back_populates='user', cascade="all, delete-orphan")
    
    friends = relationship(
        'User',
        secondary=Friends,
        primaryjoin=dni == Friends.c.user_dni,
        secondaryjoin=dni == Friends.c.friend_dni,
        backref='friend_of'
    )

    def to_json(self):
        return {
            "dni": self.dni,
            "name": self.name,
            "email": self.email,
            "birth_date": self.birth_date.strftime('%d/%m/%Y'),
            "active": self.active,
            "image": self.image,
            "amount": float(self.amount),
            "administrator": self.administrator,
            "address": self.address,
            "phone": self.phone,
            "created_at": self.created_at.strftime('%d/%m/%Y') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%d/%m/%Y') if self.updated_at else None,
            "credit_cards": [card.to_json() for card in self.credit_cards],
             "friends": [{"dni": friend.dni, "name": friend.name, "image":friend.image} for friend in self.friends],
        }

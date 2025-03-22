from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
# from .credit_card_model import CreditCard
from models import db 

class User(db.Model):
    __tablename__ = 'user'
    
    dni = Column(String(36), primary_key=True, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    pwd = Column(String(255), nullable=False)  # Se debe hashear la contraseña
    birth_date = Column(Date, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    image = Column(String(255), nullable=False)
    amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    administrator = Column(Boolean, default=False, nullable=False)
    created_at = Column(Date, default=datetime.utcnow, nullable=False)
    updated_at = Column(Date, onupdate=datetime.utcnow)

    # Use back_populates to resolve the conflict between User and CreditCard
    # credit_cards = relationship('CreditCard', back_populates='user', cascade='all, delete-orphan', lazy='joined')

    # Relación con amigos (Many-to-Many)
    # friends = db.Table(
    #     'user_friends',
    #     db.Column('user_dni', String(36), ForeignKey('user.dni'), primary_key=True),
    #     db.Column('friend_dni', String(36), ForeignKey('user.dni'), primary_key=True)
    # )

    # # Relación con solicitudes de amistad
    # sent_requests = relationship('FriendshipRequest', foreign_keys='FriendshipRequest.sender_dni', backref='sender', lazy='dynamic')
    # received_requests = relationship('FriendshipRequest', foreign_keys='FriendshipRequest.receiver_dni', backref='receiver', lazy='dynamic')
    

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
            "created_at": self.created_at.strftime('%d/%m/%Y') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%d/%m/%Y') if self.updated_at else None,
        }

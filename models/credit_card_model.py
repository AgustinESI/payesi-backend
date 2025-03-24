# models/credit_card_model.py
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DECIMAL, Date, Boolean, BigInteger
from sqlalchemy.orm import relationship
from models import db 

class CreditCard(db.Model):
    __tablename__ = 'creditcard'

    number = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    cvv = Column(String(3), nullable=False)
    type = Column(String(50), nullable=False)
    expiration_date = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    card_holder_name = Column(String(255), nullable=False)
    created_at = Column(Date, nullable=False, default=datetime.utcnow)
    updated_at = Column(Date, onupdate=datetime.utcnow)
    
    # Add foreign key to user
    user_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
    # Relationship to User
    user = relationship('User', back_populates='credit_cards')


    def to_json(self):
        return {
            "number": str(self.number),
            "type": self.type,
            "expiration_date": self.expiration_date.strftime('%d/%m/%Y'),
            "active": self.active,
            "card_holder_name": self.card_holder_name,
            "user_dni": self.user_dni,
            "created_at": self.created_at.strftime('%d/%m/%Y') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%d/%m/%Y') if self.updated_at else None
        }
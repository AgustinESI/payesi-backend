# models/transaction_request_model.py

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, DECIMAL
from models import db

class RequestStatusEnum(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class TransactionRequest(db.Model):
    __tablename__ = 'transactions_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(10, 2), nullable=False, default=0.0)
    message = Column(String(255), nullable=False)
    sender_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
    receiver_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
    status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    

    def to_json(self):

        return {
            "id": self.id,
            "amount": float(self.amount),
            "message": self.message,
            "sender_dni": self.sender_dni,
            "receiver_dni": self.receiver_dni,
            "status": self.status.value,
            "created_at": self.created_at.strftime('%d/%m/%Y %H:%M'),
            "responded_at": self.responded_at.strftime('%d/%m/%Y %H:%M') if self.responded_at else None,
        }

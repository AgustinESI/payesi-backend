# models/friendship_request_model.py

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from models import db

class RequestStatusEnum(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class FriendshipRequest(db.Model):
    __tablename__ = 'friendship_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
    receiver_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
    status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    
    sender = None  # Placeholder for the sender user object
    receiver = None  # Placeholder for the receiver user object

    def to_json(self):
        sender_json = self.sender.to_json() if self.sender else None
        receiver_json = self.receiver.to_json() if self.receiver else None

        return {
            "id": self.id,
            "sender_dni": self.sender_dni,
            "receiver_dni": self.receiver_dni,
            "status": self.status.value,
            "created_at": self.created_at.strftime('%d/%m/%Y %H:%M'),
            "responded_at": self.responded_at.strftime('%d/%m/%Y %H:%M') if self.responded_at else None,
            "sender": sender_json,  # Include sender information
            "receiver": receiver_json  # Include receiver information
        }

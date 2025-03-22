# from datetime import datetime
# from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date
# from sqlalchemy.orm import relationship
# from models import db 
# import enum

# class RequestStatusEnum(enum.Enum):
#     PENDING = "PENDING"
#     ACCEPTED = "ACCEPTED"
#     REJECTED = "REJECTED"

# class FriendshipRequest(db.Model):
#     __tablename__ = 'friendship_requests'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     status = Column(Enum(RequestStatusEnum), nullable=False, default=RequestStatusEnum.PENDING)
#     created_at = Column(Date, nullable=False, default=datetime.utcnow)
#     updated_at = Column(Date, onupdate=datetime.utcnow)

#     # Relationship with the user sending the request (sender)
#     sender_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
#     sender = relationship('User', foreign_keys=[sender_dni], backref='sent_requests_relation')  # Renamed backref

#     # Relationship with the user receiving the request (receiver)
#     receiver_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
#     receiver = relationship('User', foreign_keys=[receiver_dni], backref='received_requests_relation')  # Renamed backref

#     def to_json(self):
#         return {
#             "id": self.id,
#             "status": self.status.value,
#             "created_at": self.created_at.strftime('%d/%m/%Y') if self.created_at else None,
#             "updated_at": self.updated_at.strftime('%d/%m/%Y') if self.updated_at else None,
#             "sender_dni": self.sender_dni,
#             "receiver_dni": self.receiver_dni,
#         }

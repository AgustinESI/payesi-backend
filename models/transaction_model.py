from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DECIMAL, Date, Integer, BigInteger
from sqlalchemy.orm import relationship
from models import db 

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(10, 2), nullable=False, default=0.0)
    transaction_type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    status = Column(String(50), nullable=False)

    credit_card_number = Column(BigInteger, ForeignKey('creditcard.number'), nullable=False)
    sender_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
    receiver_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)

    credit_card = relationship('CreditCard', backref='transactions')
    sender = relationship('User', foreign_keys=[sender_dni], backref='sent_transactions')
    receiver = relationship('User', foreign_keys=[receiver_dni], backref='received_transactions')


    def to_json(self):
        return {
            "id": self.id,
            "amount": float(self.amount),
            "transaction_type": self.transaction_type,
            "message": self.message,
            "date": self.date.strftime('%d/%m/%Y'),
            "status": self.status,
            "credit_card_number": str(self.credit_card_number),
            "sender_dni": self.sender_dni,
            "receiver_dni": self.receiver_dni,
            "sender": self.sender.to_json(),
            "receiver": self.receiver.to_json()
        }

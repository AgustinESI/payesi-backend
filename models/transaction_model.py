# from datetime import datetime
# from sqlalchemy import Column, String, ForeignKey, DECIMAL, Date, Integer, BigInteger
# from sqlalchemy.orm import relationship
# from models import db 

# class Transaction(db.Model):
#     __tablename__ = 'transaction'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     amount = Column(DECIMAL(10, 2), nullable=False, default=0.0)
#     transaction_type = Column(String(50), nullable=False)
#     message = Column(String(255), nullable=False)
#     date = Column(Date, nullable=False, default=datetime.utcnow)
#     status = Column(String(50), nullable=False)

#     # Relación con usuario origen
#     user_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)
#     user = relationship('User', backref='transactions')

#     # Relación con tarjeta de crédito
#     credit_card_number = Column(BigInteger, ForeignKey('creditcard.number'), nullable=False)
#     credit_card = relationship('CreditCard', backref='transactions')

#     # Relación con usuario destino (puede ser nulo si es una compra o retiro)
#     target_user_dni = Column(String(36), ForeignKey('user.dni'))
#     target_user = relationship('User', foreign_keys=[target_user_dni])

#     def to_json(self):
#         return {
#             "id": self.id,
#             "amount": float(self.amount),
#             "transaction_type": self.transaction_type,
#             "message": self.message,
#             "date": self.date.strftime('%d/%m/%Y'),
#             "status": self.status,
#             "user_dni": self.user_dni,
#             "target_user_dni": self.target_user_dni,
#             "credit_card_number": self.credit_card_number
#         }

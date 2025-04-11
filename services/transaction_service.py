from models.transaction_model import Transaction
from models import db
from datetime import datetime

class TransactionService:
    
    @staticmethod
    def create_request(transaction):
        """Get a single credit card by its number."""
        try:
            db.session.add(transaction)
            db.session.commit()
            return transaction
        except Exception as e:
            db.session.rollback()
            raise e
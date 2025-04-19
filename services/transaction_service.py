from models.transaction_model import Transaction
from models.enums import RequestStatusEnum
from models import db
from datetime import datetime

class TransactionService:
    
    @staticmethod
    def create_transaction(transaction):
        """Get a single credit card by its number."""
        try:
            db.session.add(transaction)
            db.session.commit()
            return transaction
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def create_request(transactionrequest):
        """Get a single credit card by its number."""
        try:
            db.session.add(transactionrequest)
            db.session.commit()
            return transactionrequest
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def accept_transaction_request(transaction_request):
        """Accept a transaction request."""
        try:
            transaction_request.status = RequestStatusEnum.COMPLETED
            transaction_request.responded_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def reject_transaction_request(transaction_request):
        """Accept a transaction request."""
        try:
            transaction_request.status = RequestStatusEnum.REJECTED
            transaction_request.responded_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
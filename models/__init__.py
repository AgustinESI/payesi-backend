from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  

def init_models():
    """Importar los modelos aquí para evitar importaciones circulares"""
    from .user_model import User
    from .user_friends import Friends
    from .transaction_model import Transaction
    from .credit_card_model import CreditCard
    from .friendship_request_model import FriendshipRequest

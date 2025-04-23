from models import db
from models.apikey_model import ApiKey
  
class ApiService:
    """Service to handle API requests and responses."""
    @staticmethod
    def save_api_key(api_key):
        """Save a new API key"""
        try:
            db.session.add(api_key)
            db.session.commit()
            return api_key
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def update_api_key(api_key):
        """Update an existing API key"""
        try:
            db.session.commit()
            return api_key
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def delete_api_key(api_key):
        """Delete an API key"""
        try:
            db.session.delete(api_key)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

# user_service.py
from models import db
from models.user_model import User
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing

class UserService:
    
    @staticmethod
    def create_user(dni, name, email, pwd, birth_date, image, amount=0.0, administrator=False):
        """Create a new user"""
        try:
            hashed_pwd = generate_password_hash(pwd)  # Hash the password before storing it
            new_user = User(
                dni=dni, 
                name=name, 
                email=email, 
                pwd=hashed_pwd, 
                birth_date=birth_date, 
                image=image, 
                amount=amount, 
                administrator=administrator
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_by_dni(dni):
        """Get a user by DNI"""
        return User.query.filter_by(dni=dni).first()
    
    @staticmethod
    def get_user_by_email_and_password(email, pwd):
        """Check if the given password matches the stored hash"""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.pwd, pwd):
            return user
        return None


    @staticmethod
    def update_user(dni, name=None, email=None, pwd=None, birth_date=None, image=None, amount=None, administrator=None):
        """Update a user"""
        user = User.query.filter_by(dni=dni).first()
        if user:
            if name:
                user.name = name
            if email:
                user.email = email
            if pwd:
                user.pwd = generate_password_hash(pwd)  # Re-hash the password if changed
            if birth_date:
                user.birth_date = birth_date
            if image:
                user.image = image
            if amount is not None:
                user.amount = amount
            if administrator is not None:
                user.administrator = administrator
            db.session.commit()
            return user
        return None

    @staticmethod
    def delete_user(dni):
        """Delete a user"""
        user = User.query.filter_by(dni=dni).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return user
        return None

    @staticmethod
    def check_password(email, password):
        """Check if the given password matches the stored hash"""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.pwd, password):
            return True
        return False

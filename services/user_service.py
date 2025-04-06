# user_service.py
from models import db
from models.user_model import User
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
from sqlalchemy import text

class UserService:
    
    @staticmethod
    def create_user(dni, name, email, pwd, birth_date, image, phone, address, amount=0.0, administrator=False):
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
                administrator=administrator,
                phone=phone,
                address=address
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
    def get_user_by_email(email):
        """Check if the given password matches the stored hash"""
        return User.query.filter_by(email=email).first()
        


    @staticmethod
    def update_user(dni,name=None, phone=None, address=None,  birth_date=None, image=None):
        """Update a user"""
        user = User.query.filter_by(dni=dni).first()
        if user:
            if name:
                user.name = name
            if birth_date:
                user.birth_date = datetime.strptime(birth_date, "%d/%m/%Y").date()
            if image:
                user.image = image
            if phone is not None:
                user.phone = phone
            if address is not None:
                user.address = address
                
            print(user.name)
            db.session.flush()
            db.session.commit()
            return user
        return None


    @staticmethod
    def update_image_user(dni:str,image=None):
        """Update a user"""
        user = User.query.filter_by(dni=dni).first()
        if user:
            if image:
                user.image = image
                
            print(user.name)
            db.session.flush()
            db.session.commit()
            return user
        return None

    @staticmethod
    def deactivate_user(dni):
        user = User.query.filter_by(dni=dni).first()
        if user:
            user.active = False
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def activate_user(dni):
        user = User.query.filter_by(dni=dni).first()
        if user:
            user.active = True
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

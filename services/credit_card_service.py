# services/credit_card_service.py
from models.credit_card_model import CreditCard
from models import db
from datetime import datetime

class CreditCardService:

    @staticmethod
    def create_credit_card(card_data):
        """Create a new credit card for a user."""
        try:
            new_card = CreditCard(
                number=card_data['number'],
                cvv=card_data['cvv'],
                type=card_data['type'],
                expiration_date=datetime.strptime(card_data['expiration_date'], '%d/%m/%Y').date(),
                card_holder_name=card_data['card_holder_name'],
                user_dni=card_data['user_dni'],
                active=True
            )
            db.session.add(new_card)
            db.session.commit()
            return new_card
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating credit card: {str(e)}")

    @staticmethod
    def get_my_credit_cards(dni):
        """Get a single credit card by its number."""
        return CreditCard.query.filter_by(user_dni=dni).first()

    @staticmethod
    def get_credit_card(number):
        """Get a single credit card by its number."""
        return CreditCard.query.filter_by(number=number).first()

    @staticmethod
    def get_all_credit_cards(user_dni):
        """Get all credit cards for a user."""
        return CreditCard.query.filter_by(user_dni=user_dni).all()

    @staticmethod
    def update_credit_card(number, card_data):
        """Update a credit card."""
        card = CreditCard.query.filter_by(number=number).first()
        if card:
            card.cvv = card_data.get('cvv', card.cvv)
            card.type = card_data.get('type', card.type)
            card.expiration_date = datetime.strptime(card_data.get('expiration_date', card.expiration_date.strftime('%d/%m/%Y')), '%d/%m/%Y').date()
            card.active = card_data.get('active', card.active)
            card.card_holder_name = card_data.get('card_holder_name', card.card_holder_name)
            db.session.commit()
            return card
        return None

    @staticmethod
    def delete_credit_card(number):
        """Delete a credit card by its number."""
        card = CreditCard.query.filter_by(number=number).first()
        if card:
            db.session.delete(card)
            db.session.commit()
            return True
        return False


    def validate_and_convert(mm_yy):
        try:
            # Extract month and year
            month, year = mm_yy.split("/")
            
            # Convert two-digit year to full year
            year = int(year)
            if year < 100:  # Assuming 00-99 means 2000-2099
                year += 2000
            
            # Check if the year is a leap year
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

            # Default to first day of the month
            day = 1  

            # Special case: February
            if int(month) == 2:
                day = 29 if is_leap else 28
            
            # Create a valid date
            valid_date = datetime(year, int(month), day)
            return valid_date.strftime("%d/%m/%Y") 
        except ValueError:
            return "Invalid date"
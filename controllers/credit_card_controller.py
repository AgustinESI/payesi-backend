# controllers/credit_card_controller.py
from flask import Blueprint, request, jsonify
from services.credit_card_service import CreditCardService
from models import db
from datetime import datetime
from models.errors.error_response_model import ErrorResponse
from models.errors.custom_exception_model import CustomException
from services.user_service import UserService
from flask_cors import cross_origin
import requests
from os import getenv

credit_card_controller = Blueprint('credit_card_controller', __name__)

# Route to create a new credit card
@credit_card_controller.route('/card', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def create_credit_card():
    try:
        
        if not hasattr(request, "user"):  # Ensure user is set
            return jsonify({"error": "Unauthorized"}), 401

        user = UserService.get_user_by_email(request.user.get("email"))
        if not user:
            raise CustomException("User not found", 404)
        
        card_data = request.get_json()

        # Check if credit card with the same number already exists
        existing_card = CreditCardService.get_credit_card(card_data.get('number'))
        if existing_card:
            raise CustomException(f"Credit card with number '{card_data['number']}' already exists", 400)

        # Check for missing or invalid data
        required_fields = ['cvv', 'type', 'expiration_date', 'card_holder_name']
        for field in required_fields:
            if field not in card_data:
                raise CustomException(f"Missing required field: {field}", 400)

        # Convert expiration date to correct format if necessary
        try:
            expiration_date = CreditCardService.validate_and_convert(card_data.get('expiration_date'))
            card_data['expiration_date'] = expiration_date
        except ValueError:
            raise CustomException("Invalid expiration date format. Use 'DD/MM/YYYY'", 400)

        card_data['user_dni'] = user.dni
        card_data['number'] = card_data['number'].replace(" ", "")

        print(card_data)

        # Validate the credit card information with the payesi-creditcards backend
        headers = {"Content-Type": "application/json"}
        external_api_url = f"{getenv('CREDITCARD_BACKEND')}api/cards"
        resonse = requests.post(external_api_url, json=card_data, headers=headers)
        
        if resonse.status_code !=201:
            error_message = resonse.json().get("error", "Unknown error")
            raise CustomException(f"Credit card valdiation failed: {error_message}", 400)


        # Call the CreditCardService to create the card
        new_card = CreditCardService.create_credit_card(card_data)
        
        return jsonify(new_card.to_json()), 201

    except CustomException as e:
        # Handle custom exceptions with specific error response
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        # Catch all other exceptions
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

# Route to get a single credit card by its number
@credit_card_controller.route('/card/<int:number>', methods=['GET'])
def get_credit_card(number):
    try:
        card = CreditCardService.get_credit_card(number)
        if card:
            return jsonify(card.to_json()), 200
        raise CustomException(f"Credit card with number '{number}' not found", 404)
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@credit_card_controller.route('/all', methods=['GET'])
def get_all_credit_cards():
    try:
        
        if not hasattr(request, "user"):  # Ensure user is set
            return jsonify({"error": "Unauthorized"}), 401

        user = UserService.get_user_by_email(request.user.get("email"))
        if not user:
            raise CustomException("User not found", 404)
        
        if  user.administrator == False:
            raise CustomException("Unauthorized", 401)
        
    
        credit_cards = CreditCardService.get_all_credit_cards()
        return jsonify([card.to_json() for card in credit_cards]), 200
    
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

# Route to update a credit card
@credit_card_controller.route('/card/<int:number>', methods=['PUT'])
def update_credit_card(number):
    try:
        card_data = request.get_json()

        # Check if the credit card exists
        card = CreditCardService.get_credit_card(number)
        if not card:
            raise CustomException(f"Credit card with number '{number}' not found", 404)

        # Update the card with the new data
        updated_card = CreditCardService.update_credit_card(number, card_data)

        return jsonify(updated_card.to_json()), 200

    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

# Route to delete a credit card
@credit_card_controller.route('/card/<int:number>', methods=['DELETE'])
def delete_credit_card(number):
    try:
        # Check if the credit card exists
        card = CreditCardService.get_credit_card(number)
        if not card:
            raise CustomException(f"Credit card with number '{number}' not found", 404)

        # Delete the card
        success = CreditCardService.delete_credit_card(number)
        if success:
            return jsonify({'message': 'Credit card deleted successfully'}), 200
        raise CustomException(f"Failed to delete credit card with number '{number}'", 500)

    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

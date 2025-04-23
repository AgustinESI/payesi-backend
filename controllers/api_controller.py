# controllers/api_controller.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from services.user_service import UserService
from models.errors.custom_exception_model import CustomException
from models.errors.error_response_model import ErrorResponse
from models.user_model import User
from models.apikey_model import ApiKey
from services.api_service import ApiService
import uuid

api_controller = Blueprint('api_controller', __name__)

@api_controller.route('/requestkey', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def request_key():
    # This is a placeholder for the actual payment request logic.
    # You would typically call a service to handle the payment request.
    # For now, we'll just return a success message.
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user's email from the request
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        if len(ApiKey.query.filter_by(user_dni=current_user.dni).all()) >= 5:
            raise CustomException("You have reached the maximum number of API keys", 400)
        
        # Get the payment request data from the request body
        data = request.get_json()
        if not data:
            raise CustomException("Invalid request data", 400)
        app_name = data.get('application_name')
        if not app_name:
            raise CustomException("Application name is required", 400)
        
        key = str(uuid.uuid4())
        # Create a new API key for the user
        new_api_key = ApiKey(
            name=app_name,
            api_key=key,
            user_dni=current_user.dni
        )
        # Save the API key to the database
        ApiService.save_api_key(new_api_key)
        return jsonify(new_api_key.recently_created_to_json()), 200
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

@api_controller.route('/getkeys', methods=['GET'])
@cross_origin(origins='http://localhost:4200')
def get_keys():
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user's email from the request
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        # Get all API keys for the user
        api_keys = ApiKey.query.filter_by(user_dni=current_user.dni).all()
        return jsonify([key.to_json() for key in api_keys]), 200
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@api_controller.route('/updatekey', methods=['PUT'])
@cross_origin(origins='http://localhost:4200')
def update_key():
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user's email from the request
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        data = request.get_json()
        if not data:
            raise CustomException("Invalid request data", 400)
        old_api_key_id = data.get('api_key_id')
        if not old_api_key_id:
            raise CustomException("Api key id is required", 400)
        
        # Get the API key by ID
        api_key_data = ApiKey.query.filter_by(id=old_api_key_id, user_dni=current_user.dni).first()
        if not api_key_data:
            raise CustomException("API key not found", 404)
        
        api_key_data.api_key = str(uuid.uuid4())  # Generate a new API key

        ApiService.update_api_key(api_key_data)
        return jsonify(api_key_data.recently_created_to_json()), 200
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@api_controller.route('/deletekey/<string:api_key_id>', methods=['DELETE'])
@cross_origin(origins='http://localhost:4200')
def delete_key(api_key_id):
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user's email from the request
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        api_key_data = ApiKey.query.filter_by(id=api_key_id, user_dni=current_user.dni).first()
        if not api_key_data:
            raise CustomException("API key not found", 404)
        
        ApiService.delete_api_key(api_key_data)
        return jsonify({'message': 'API Key deleted successfully'}), 200
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@api_controller.route('/payments/request', methods=['POST'])
def request_payment():
    return jsonify({"message": "Payment request received"}), 200

@api_controller.route('/payments/confirm/<int:request_id>', methods=['POST'])
def confirm_payment(request_id):
    return {"message": "Payment confirmation received"}, 200
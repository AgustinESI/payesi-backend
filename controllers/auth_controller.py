from flask import Blueprint, request, jsonify
from configuration.auth_filter import create_jwt_token, validate_jwt_token
from models.errors.error_response_model import ErrorResponse
from models.errors.custom_exception_model import CustomException
from services.user_service import UserService

auth_controller = Blueprint('auth_controller', __name__)

@auth_controller.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": " ✅ Service is working"})   

@auth_controller.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        data = request.get_json()
        email = data.get('email')
        pwd = data.get('password')
        
        if not email:
            raise CustomException("Email is required", 400)
        
        if not pwd:
            raise CustomException("Password is required", 400)
        
        value = UserService.check_password(email, pwd)
        
        if value is False:
            raise CustomException("Invalid credentials", 401)
        
        user = UserService.get_user_by_email(email)
        if not user.active:
            raise CustomException("Your account is disabled. To be able to operate, you must speak with the administrator.", 500)
        
        return create_jwt_token(data =request.get_json())
        
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
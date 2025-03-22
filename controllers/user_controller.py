# user_controller.py
from flask import Blueprint, request, jsonify
from services.user_service import UserService
from models.user_model import User
from datetime import datetime
from models.errors.error_response_model import ErrorResponse
from models.errors.custom_exception_model import CustomException

# Create a Blueprint for the user controller
user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/ping', methods=['GET'])
def ping(): 
    return jsonify({"message": " ✅ Service is working"})

# Route to create a user
@user_controller.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()
    
    dni = data.get('dni')
    name = data.get('name')
    email = data.get('email')
    pwd = data.get('pwd')
    birth_date = data.get('birth_date')  # This will be a string in the 'YYYY-MM-DD' format
    image = data.get('image')
    amount = data.get('amount', 0.0)  # Default to 0 if not provided
    administrator = data.get('administrator', False)  # Default to False if not provided
    
    try:
        # Check if the user already exists
        existing_user = UserService.get_user_by_dni(dni)
        if existing_user:
            raise CustomException(f"User with DNI {dni} already exists", 400)     
                      
        # Convert the 'birth_date' string to a datetime.date object
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()

        # Call the UserService to create the user
        new_user = UserService.create_user(dni, name, email, pwd, birth_date, image, amount, administrator)

        # Prepare response
        response = { new_user.to_json() }
        return jsonify(response), 201

    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

# Route to get a user by DNI
@user_controller.route('/<dni>', methods=['GET'])
def get_user(dni):
    try:
        user = UserService.get_user_by_dni(dni)
        if user:
            response = {
                "status": "success",
                "user": user.to_json()
            }
            return jsonify(response), 200
        raise CustomException(f"User not found", 404) 
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    return jsonify(response), 404

# Route to update a user
@user_controller.route('/<dni>/update', methods=['PUT'])
def update_user(dni):
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        pwd = data.get('pwd')
        birth_date = data.get('birth_date')
        image = data.get('image')
        amount = data.get('amount')
        administrator = data.get('administrator')
        
        user = UserService.update_user(dni, name, email, pwd, birth_date, image, amount, administrator)
        if user:
            response = {
                "status": "success",
                "message": "User updated successfully",
                "user": user.to_json()
            }
            return jsonify(response), 200
        else:
            raise CustomException(f"An error occurred while trying to update the client", 500) 
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        error_response = ErrorResponse.from_exception(e,500)
        return jsonify(error_response.to_dict()), 500

# Route to delete a user
@user_controller.route('/<dni>/delete', methods=['DELETE'])
def delete_user(dni):
    try:
        user = UserService.delete_user(dni)
        if user:
            response = {
                "status": "success",
                "message": "User deleted successfully"
            }
            return jsonify(response), 200
        raise CustomException("User not found", 404)
    
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

# Route to check password (for authentication purposes)
@user_controller.route('/<dni>/check_password', methods=['POST'])
def check_password(dni):
    try:
        data = request.get_json()
        password = data.get('password')
        
        if UserService.check_password(dni, password):
            response = {
                "status": "success",
                "message": "Password is correct"
            }
            return jsonify(response), 200
        
        raise CustomException("Incorrect password", 400)
        
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
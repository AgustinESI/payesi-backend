from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.user_model import User
from models.friendship_request_model import FriendshipRequest, RequestStatusEnum
from models.errors.custom_exception_model import CustomException
from models.errors.error_response_model import ErrorResponse
from services.user_service import UserService

friendship_controller = Blueprint('friendship_controller', __name__)


@friendship_controller.route('/pending', methods=['GET'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def get_pending_friendship_requests():
    """ Get all pending friendship requests where the current user is the receiver. """
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        # Get all the pending friendship requests where the current user is the receiver
        pending_requests = FriendshipRequest.query.filter(
            FriendshipRequest.receiver_dni == current_user.dni,
            FriendshipRequest.status == RequestStatusEnum.PENDING
        ).all()
        
        if not pending_requests:
            return jsonify([]), 200
        
        # Fetch the sender and receiver for each request
        for req in pending_requests:
            req.sender = UserService.get_user_by_dni(req.sender_dni)
            req.receiver = UserService.get_user_by_dni(req.receiver_dni)
        
        # Return the results as JSON
        return jsonify([req.to_json() for req in pending_requests]), 200

    except Exception as e:
        # Handle any exceptions and return an error response
        return jsonify({"error": str(e)}), 500

@friendship_controller.route('/favourite', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def add_user_favourite_request():
    """ Add user to favourite list. """
    
    try:
        if not hasattr(request, "user"):  # Ensure user is set
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get the logged-in user and the friend to add
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        data = request.get_json()
        favourite_dni = data.get('favourite_dni')
        
        favourite = UserService.get_user_by_dni(favourite_dni)
        if not favourite:
            raise CustomException("Friend not found", 404)
        
        UserService.add_user_favourite(current_user.dni, favourite_dni)
    
        current_user = UserService.get_user_by_email(request.user.get("email"))
        return jsonify(current_user.to_json())
    
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

@friendship_controller.route('/favourite/remove', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def remove_user_favourite_request():
    """ Remove user from favourite list. """
    
    try:
        if not hasattr(request, "user"):  # Ensure user is set
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get the logged-in user and the friend to remove
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        data = request.get_json()
        favourite_dni = data.get('favourite_dni')
        
        favourite = UserService.get_user_by_dni(favourite_dni)
        if not favourite:
            raise CustomException("Favorite not found", 404)
        
        UserService.remove_user_favourite(current_user.dni, favourite_dni)
        
        current_user = UserService.get_user_by_email(request.user.get("email"))
        return jsonify(current_user.to_json())
    
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500



@friendship_controller.route('/new', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def create_friendship_request():
    """ Create a friendship request. """
    try:
        if not hasattr(request, "user"):  # Ensure user is set
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get the logged-in user and the friend to add
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        data = request.get_json()
        friend_dni = data.get('friend_dni')
        
        if not friend_dni:
            raise CustomException("Friend's DNI is required", 400)
        
        # Fetch the user to be added as a friend
        friend = UserService.get_user_by_dni(friend_dni)
        if not friend:
            raise CustomException("Friend not found", 404)
        
        if current_user in friend.blocked_users:
            raise CustomException("Cannot request transaction. You have been blocked by the other user.", 403)
        
        if friend in current_user.blocked_users:
            raise CustomException("Cannot request transaction. You have blocked the other user.", 403)
        
        # Check if already friends or if there's already a pending request
        existing_request = FriendshipRequest.query.filter(
            (FriendshipRequest.sender_dni == current_user.dni) &
            (FriendshipRequest.receiver_dni == friend.dni) &
            (FriendshipRequest.status == RequestStatusEnum.PENDING)
        ).first()
        
        if existing_request:
            raise CustomException("Friendship request already exists", 400)

        new_request = FriendshipRequest(
            sender_dni=current_user.dni,
            receiver_dni=friend.dni,
            status="PENDING"
        )
        
        # Save to the database
        UserService.create_friendship_request(new_request)

        return jsonify({"message": "Friendship request sent successfully"}), 201
    
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500


@friendship_controller.route('/accept/<int:request_id>', methods=['POST'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def accept_friendship_request(request_id):
    """ Accept a pending friendship request and create mutual friendships """
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        # Call the service to accept the friendship request and create mutual friendships
        success, message = UserService.accept_friendship_request(current_user.dni, request_id)

        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

@friendship_controller.route('/reject/<int:request_id>', methods=['POST'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def reject_friendship_request(request_id):
    """ Reject a pending friendship request """
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        # Call the service to reject the request
        success, message = UserService.reject_friendship_request(current_user.dni, request_id)

        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@friendship_controller.route('/delete/<string:friend_dni>', methods=['DELETE'])
@cross_origin(origins='http://localhost:4200')
def delete_friend(friend_dni):
    try:
        # Verificar autenticación
        if not hasattr(request, "user"):
            return jsonify({"error": "Unauthorized"}), 401

        # Obtener el usuario actual
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        # Obtener al amigo a eliminar
        friend = UserService.get_user_by_dni(friend_dni)
        if not friend:
            raise CustomException("Friend not found", 404)

        # Eliminar la relación en ambas direcciones
        UserService.remove_friendship(current_user.dni, friend_dni)
        UserService.remove_friendship(friend_dni, current_user.dni)

        return jsonify({"message": "Friendship deleted successfully"}), 200

    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code

    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500


@friendship_controller.route('/block', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def block_user_request():
    """ Block a user. """
    try:
        if not hasattr(request, "user"):
            return jsonify({"error": "Unauthorized"}), 401

        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        data = request.get_json()
        blocked_dni = data.get('blocked_dni')

        blocked_user = UserService.get_user_by_dni(blocked_dni)
        if not blocked_user:
            raise CustomException("User to block not found", 404)

        UserService.block_user(current_user.dni, blocked_dni)

        # Optional: Return updated user info
        current_user = UserService.get_user_by_email(current_user.email)
        return jsonify(current_user.to_json())

    except CustomException as e:
        return jsonify(ErrorResponse.from_exception(e, e.status_code).to_dict()), e.status_code
    except Exception as e:
        return jsonify(ErrorResponse.from_exception(e, 500).to_dict()), 500


@friendship_controller.route('/unblock', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def unblock_user_request():
    """ Unblock a user. """
    try:
        if not hasattr(request, "user"):
            return jsonify({"error": "Unauthorized"}), 401

        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        data = request.get_json()
        blocked_dni = data.get('blocked_dni')

        blocked_user = UserService.get_user_by_dni(blocked_dni)
        if not blocked_user:
            raise CustomException("User to unblock not found", 404)

        UserService.unblock_user(current_user.dni, blocked_dni)

        # Optional: Return updated user info
        current_user = UserService.get_user_by_email(current_user.email)
        return jsonify(current_user.to_json())

    except CustomException as e:
        return jsonify(ErrorResponse.from_exception(e, e.status_code).to_dict()), e.status_code
    except Exception as e:
        return jsonify(ErrorResponse.from_exception(e, 500).to_dict()), 500

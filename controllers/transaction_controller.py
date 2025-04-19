from operator import or_, and_
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.user_model import User
from models.credit_card_model import CreditCard
from models.transaction_model import Transaction
from models.enums import RequestStatusEnum, TransactionTypeEnum
from models.errors.custom_exception_model import CustomException
from models.errors.error_response_model import ErrorResponse
from services.transaction_service import TransactionService
from services.user_service import UserService

transaction_controller = Blueprint('transaction_controller', __name__)

@transaction_controller.route('/me', methods=['GET'])
@cross_origin(origins='http://localhost:4200')  # Ajusta la política CORS según sea necesario
def get_requests():
    """ Obtener todas las transacciones donde el usuario actual es el receptor o el emisor. """
    try:
        if not hasattr(request, "user"):
            return jsonify({"error": "Unauthorized"}), 401

        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        requests = Transaction.query.filter(
            and_(
                or_(
                    Transaction.sender_dni == current_user.dni,
                    Transaction.receiver_dni == current_user.dni
                ),
                Transaction.status == RequestStatusEnum.COMPLETED
            )
        ).all()

        # Añadir el nombre del emisor y receptor a cada transacción
        requests_json = []
        for req in requests:
            req_json = req.to_json()
            sender = User.query.filter_by(dni=req.sender_dni).first()
            receiver = User.query.filter_by(dni=req.receiver_dni).first()
            
            # Añadir los nombres de los usuarios
            req_json["sender_name"] = sender.name if sender else "Unknown"
            req_json["receiver_name"] = receiver.name if receiver else "Unknown"
            
            requests_json.append(req_json)

        # Devolver los resultados como JSON
        return jsonify(requests_json), 200

    except Exception as e:
        # Manejar cualquier excepción y devolver una respuesta de error
        return jsonify({"error": str(e)}), 500
    
@transaction_controller.route('/<int:transaction_id>', methods=['GET'])
@cross_origin(origins='http://localhost:4200')
def get_transaction_by_id(transaction_id):
    """ Obtener una transacción específica por ID si pertenece al usuario actual y está COMPLETED. """
    try:
        if not hasattr(request, "user"):
            return jsonify({"error": "Unauthorized"}), 401

        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        transaction = Transaction.query.filter(
            and_(
                Transaction.id == transaction_id,
                Transaction.status == RequestStatusEnum.PENDING
            )
        ).first()
        
        if not transaction:
            raise CustomException(f"Transaction not found or access denied", 403) 
        
        transaction_json = transaction.to_json()
        
        sender = User.query.filter_by(dni=transaction.sender_dni).first()
        receiver = User.query.filter_by(dni=transaction.receiver_dni).first()
        
        transaction_json["sender_name"] = sender.name if sender else "Unknown"
        transaction_json["receiver_name"] = receiver.name if receiver else "Unknown"

        return jsonify(transaction_json), 200
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

@transaction_controller.route('/create', methods=['POST'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def create_transaction():
    """ Create a new transaction from sender to receiver. """
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user (sender)
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        # Get the data from the request
        data = request.get_json()
        sender_dni = current_user.dni
        receiver_dni = data.get("receiver_dni")
        amount = int(data.get("amount"))
        message = data.get("message")
        credit_card_number = data.get("credit_card_number")

        # Check if the receiver exists
        receiver = User.query.filter_by(dni=receiver_dni).first()
        if not receiver:
            raise CustomException(f"Receiver not found", 400) 

        # Check if the sender has enough money
        if current_user.amount < amount:
            raise CustomException(f"Insufficient funds", 400) 

        # Check if the credit card exists and belongs to the sender
        credit_card = CreditCard.query.filter_by(number=credit_card_number, user_dni=sender_dni).first()
        if not credit_card:
            return jsonify({"error": "Invalid credit card"}), 400
    
        # Create the transaction record
        transaction = Transaction(
            amount=amount,
            transaction_type=TransactionTypeEnum.SENT,
            message=message,
            sender_dni=sender_dni,
            receiver_dni=receiver_dni,
            credit_card_number=credit_card_number,
            status=RequestStatusEnum.COMPLETED
        )
        
        # Add the transaction to the database
        TransactionService.create_transaction(transaction)
        
        # Update the amounts for both sender and receiver
        current_user.amount -= amount
        receiver.amount += amount
        
        UserService.update_user(current_user.dni,None,None,None,None,None, current_user.amount)
        UserService.update_user(receiver.dni,None,None,None,None,None, receiver.amount)
        
        # Return the transaction data as JSON
        
        transaction_json = transaction.to_json()
        transaction_json["sender_name"] = current_user.name
        transaction_json["receiver_name"] = receiver.name
        return jsonify(transaction_json), 201
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500

@transaction_controller.route('/createrequest', methods=['POST'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def request_transaction():
    """ Create a new transaction request from sender to receiver. """
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user (sender)
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        # Get the data from the request
        data = request.get_json()
        receiver_dni = current_user.dni
        sender_dni = data.get("sender_dni")
        amount = int(data.get("amount"))
        message = data.get("message")

        # Check if the receiver exists
        sender = User.query.filter_by(dni=sender_dni).first()
        if not sender:
            raise CustomException(f"Sender not found", 400)
        
        if current_user in sender.blocked_users:
            raise CustomException("Cannot request transaction. You have been blocked by the other user.", 403)
        
        if sender in current_user.blocked_users:
            raise CustomException("Cannot request transaction. You have blocked the other user.", 403)
            
        
        # Create the transaction record
        transaction_request = Transaction(
            amount=amount,
            message=message,
            sender_dni=sender.dni,
            receiver_dni=receiver_dni,
            transaction_type=TransactionTypeEnum.REQUEST,
            status=RequestStatusEnum.PENDING,
        )
        # Add the transaction to the database
        TransactionService.create_request(transaction_request)
        return jsonify(transaction_request.to_json()), 201
    except CustomException as e:
        error_response = ErrorResponse.from_exception(e,e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@transaction_controller.route('/acceptrequest/<int:request_id>', methods=['POST'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def accept_transaction_request(request_id):
    """ Accept a pending transaction request. """
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        current_request = Transaction.query.get(request_id)
        
        data = request.get_json()
        card_number = data.get("card_number")
        
        if not card_number:
            raise CustomException("Card number is required", 400)
        
        creditcard = CreditCard.query.filter_by(number=card_number, user_dni=current_user.dni).first()
        if not creditcard:
            raise CustomException("Credit card not found", 404)
        
        if not current_request:
            raise CustomException("Request not found", 404)
        if current_request.status == RequestStatusEnum.COMPLETED:
            raise CustomException("Request already accepted", 400)
        if current_request.sender_dni != current_user.dni:
            raise CustomException("You are not authorized to accept this request", 403)
        
        receiver_user = UserService.get_user_by_dni(current_request.receiver_dni)
        if not receiver_user:
            raise CustomException("Receiver user not found", 404)

        if current_user.amount < current_request.amount:
            raise CustomException(f"Insufficient funds", 400) 
        
        current_user.amount -= current_request.amount
        receiver_user.amount += current_request.amount
        
        UserService.update_user(current_user.dni,None,None,None,None,None, current_user.amount)
        UserService.update_user(receiver_user.dni,None,None,None,None,None, receiver_user.amount)
        
        current_request.credit_card_number = card_number
        
        TransactionService.accept_transaction_request(current_request)
        
        transaction = Transaction.query.get(request_id)
        
        return jsonify(transaction.to_json()), 200

    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@transaction_controller.route('/rejectrequest/<int:request_id>', methods=['POST'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def reject_transaction_request(request_id):
    """ Reject a pending transaction request. """
    try:
        # Ensure user is authenticated
        if not hasattr(request, "user"):  # Check if the user is set in the request
            return jsonify({"error": "Unauthorized"}), 401

        # Get the logged-in user
        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)

        # Find the transaction request by its ID
        transaction_request = Transaction.query.get(request_id)
        if not transaction_request:
            raise CustomException("Transaction request not found", 404)
        if transaction_request.sender_dni != current_user.dni:
            raise CustomException("You are not authorized to accept this request", 403)

        TransactionService.reject_transaction_request(transaction_request)

        return jsonify({"message": "Transaction request rejected."}), 200

    except Exception as e:
        error_response = ErrorResponse.from_exception(e, 500)
        return jsonify(error_response.to_dict()), 500
    
@transaction_controller.route('/pending', methods=['GET'])
@cross_origin(origins='http://localhost:4200')  # Adjust your CORS policy as needed
def get_pending_transaction_requests():
    """ Obtener todas las solicitudes de transacción pendientes donde el usuario actual es el receptor. """
    try:
        if not hasattr(request, "user"):
            return jsonify({"error": "Unauthorized"}), 401

        current_user = UserService.get_user_by_email(request.user.get("email"))
        if not current_user:
            raise CustomException("User not found", 404)
        
        requests = Transaction.query.filter(
            Transaction.sender_dni == current_user.dni,
            Transaction.status == RequestStatusEnum.PENDING
        ).all()

        # Añadir el nombre del emisor y receptor a cada solicitud
        requests_json = []
        for req in requests:
            req_json = req.to_json()
            sender = User.query.filter_by(dni=req.sender_dni).first()
            
            # Añadir los nombres de los usuarios
            req_json["sender_name"] = sender.name if sender else "Unknown"
            
            requests_json.append(req_json)

        # Devolver los resultados como JSON
        return jsonify(requests_json), 200

    except Exception as e:
        # Manejar cualquier excepción y devolver una respuesta de error
        return jsonify({"error": str(e)}), 500
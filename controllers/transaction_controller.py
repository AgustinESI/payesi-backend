from operator import or_
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.user_model import User
from models.credit_card_model import CreditCard
from models.transaction_model import Transaction
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
            or_(
                Transaction.sender_dni == current_user.dni,
                Transaction.receiver_dni == current_user.dni
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
        transaction_type = data.get("transaction_type")
        message = data.get("message")
        credit_card_number = data.get("credit_card_number")

        print("1")
        # Check if the receiver exists
        receiver = User.query.filter_by(dni=receiver_dni).first()
        if not receiver:
            raise CustomException(f"Receiver not found", 400) 
        
        print("2")
        # Check if the sender has enough money
        if current_user.amount < amount:
            raise CustomException(f"Insufficient funds", 400) 
    
        print("3")
        # Check if the credit card exists and belongs to the sender
        credit_card = CreditCard.query.filter_by(number=credit_card_number, user_dni=sender_dni).first()
        if not credit_card:
            return jsonify({"error": "Invalid credit card"}), 400
    
        print("4")
        # Create the transaction record
        transaction = Transaction(
            amount=amount,
            transaction_type=transaction_type,
            message=message,
            sender_dni=sender_dni,
            receiver_dni=receiver_dni,
            credit_card_number=credit_card_number,
            status='completed'
        )
        
        
        print("5")
        # Add the transaction to the database
        TransactionService.create_request(transaction)
        
        
        print("6")
        # Update the amounts for both sender and receiver
        current_user.amount -= amount
        receiver.amount += amount
        
        print("7")
        UserService.update_user(current_user.dni,None,None,None,None,None, current_user.amount)
        print("8")
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

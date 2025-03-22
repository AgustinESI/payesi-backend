from jwt import encode, decode
from os import getenv
from datetime import datetime, timedelta
from jwt import exceptions
from models.errors.error_response_model import ErrorResponse
from models.errors.custom_exception_model import CustomException
from flask import jsonify, request

def expired_token():
    current_date = datetime.now()
    expiration_seconds = int(getenv('JWT_EXPIRATION_SECONDS')) 
    expiration_date = current_date + timedelta(seconds=expiration_seconds)
    
    return expiration_date

def create_jwt_token(data: dict):    
    token = encode(payload={**data, "exp":expired_token()}, key=getenv("SECRET_KEY"), algorithm='HS256')
    response = {
        "token": token.encode("UTF-8") if isinstance(token, bytes) else token,
        "expiresIn": getenv('JWT_EXPIRATION_SECONDS'),
        "date": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        "user": data.get('email')
    }
    return jsonify(response)
    
    

def validate_jwt_token(token: str, output=False):
    try:
       if output:
           return decode(token, key=getenv('SECRET_KEY'), algorithms=['HS256'])
       decode(token, key=getenv('SECRET_KEY'), algorithms=['HS256'])
       
    except exceptions.DecodeError as e:
        exception = Exception("Invalid token")
        error_response = ErrorResponse.from_exception(exception, 401)
        return jsonify(error_response.to_dict()), 401
    
    
    except exceptions.ExpiredSignatureError as e:
        exception = Exception("Token has expired")
        error_response = ErrorResponse.from_exception(exception, 401)
        return jsonify(error_response.to_dict()), 401
    
    
def verify_token():
    """ Middleware to verify JWT before each request. """
    print("🔍 Verifying request...")
    print(f"🔗 Path: {request.path}")
    
    if request.method == 'OPTIONS':
        return None
    
    if request.path in ['/auth/authenticate', 'public_route']:  # Exclude public routes
        return
    
    try:    
        token = request.headers.get('Authorization')
        if not token:
            raise CustomException("Authorization header is missing. Please provide a valid Bearer token.", 401)
        
        token = token.split(" ")[1]  # Expecting "Bearer <token>"
        decoded = validate_jwt_token(token, output=True)  # Get decoded data
        
        if isinstance(decoded, tuple):  # If validation failed, return the response
            return decoded
        
        request.user = decoded  # Attach user info to the request

    except CustomException as e:
        error_response = ErrorResponse.from_exception(e, e.status_code)
        return jsonify(error_response.to_dict()), e.status_code
    
    except Exception as e:
        return jsonify({"error": str(e)}), 401
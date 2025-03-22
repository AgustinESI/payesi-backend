from jwt import encode, decode
from os import getenv
from datetime import datetime, timedelta
from jwt import exceptions
from models.errors.error_response_model import ErrorResponse
from models.errors.custom_exception_model import CustomException
from flask import jsonify

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
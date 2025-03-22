from datetime import datetime
from flask import request, jsonify

class ErrorResponse:
    def __init__(self, status_code: int, message: str, path: str):
        self.status_code = status_code
        self.status = "error"
        self.path = path
        self.timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.message = message

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "status": self.status,
            "path": self.path,
            "timestamp": self.timestamp,
            "message": self.message
        }

    @staticmethod
    def from_exception(exception: Exception, code: int = 500):
        print(f"❌ An error occurred: {str(exception)}")
        path = request.path
        return ErrorResponse(
            status_code=code,
            message=str(exception),
            path=path
        )
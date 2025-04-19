from enum import Enum

class TransactionTypeEnum(str, Enum):
    REQUEST = "REQUEST"
    SENT = "SENT"

    def __str__(self):
        return self.value

class RequestStatusEnum(str, Enum):
    PENDING = "PENDING"  # Cuando la solicitud es enviada pero aún no aceptada
    COMPLETED = "COMPLETED"      # Cuando la solicitud es aceptada
    REJECTED = "REJECTED"        # Cuando la solicitud es rechazada
    REVOKED = "REVOKED"      # Cuando el remitente cancela la solicitud

    def __str__(self):
        return self.value
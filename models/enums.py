from enum import Enum

class TransactionTypeEnum(str, Enum):
    REQUEST = "REQUEST"
    SENT = "SENT"

    def __str__(self):
        return self.value

class RequestStatusEnum(str, Enum):
    REQUESTED = "REQUESTED"  # Cuando la solicitud es enviada pero aún no aceptada
    ALLOWED = "ALLOWED"      # Cuando la solicitud es aceptada
    DENIED = "DENIED"        # Cuando la solicitud es rechazada
    REVOKED = "REVOKED"      # Cuando el remitente cancela la solicitud

    def __str__(self):
        return self.value
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from models import db
from datetime import datetime
import uuid

class ApiKey(db.Model):
    __tablename__ = 'apikeys'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # ID único para la API key
    user_dni = Column(String(36), ForeignKey('user.dni'), nullable=False)  # Relación con el usuario
    api_key = Column(Text, nullable=False, default=lambda: str(uuid.uuid4()))  # API key única
    name = Column(String(255), nullable=False)  # Nombre de la aplicación
    created_at = Column(db.DateTime, default=datetime.utcnow)  # Fecha de creación

    # Relación inversa con el modelo User
    user = relationship('User', back_populates='api_keys')

    def to_json(self):
        return {
            "id": self.id,
            "user_dni": self.user_dni,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def recently_created_to_json(self):
        return {
            "id": self.id,
            "user_dni": self.user_dni,
            "api_key": self.api_key,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
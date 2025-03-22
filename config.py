import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Ruta base del proyecto
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")  # Ruta fija dentro del proyecto

# Crear la carpeta si no existe
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

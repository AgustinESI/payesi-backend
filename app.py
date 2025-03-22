from flask import Flask
from config import Config
from models import db, init_models
from controllers.user_controller import user_controller 
from controllers.auth_controller import auth_controller 
from os import getenv
from dotenv import load_dotenv

# Load enviorement variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

db.init_app(app)  # Initialize SQLAlchemy 

# Register the user controller blueprint
app.register_blueprint(user_controller, url_prefix='/users')
app.register_blueprint(auth_controller, url_prefix='/auth')

# Check if we should create the database on startup
if getenv('CREATE_DB_ON_STARTUP', False):
    print(" 🚀 Creating database...")
    with app.app_context():
        init_models()  
        db.create_all()
        print(" ✅ Database created!")
else:
    print(" ⚠️  Database creation skipped.")
    
      
if __name__ == '__main__':
    app.run(debug=True)

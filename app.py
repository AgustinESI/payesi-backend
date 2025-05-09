from flask import Flask
from flask_cors import CORS
from config import Config
from models import db, init_models
from controllers.user_controller import user_controller 
from controllers.auth_controller import auth_controller 
from controllers.credit_card_controller import credit_card_controller
from controllers.friendship_controller import friendship_controller
from controllers.transaction_controller import transaction_controller
from controllers.api_controller import api_controller
from os import getenv
from dotenv import load_dotenv
from configuration.auth_filter import verify_token

# Load enviorement variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# Enable CORS for all routes
# CORS(app) # Allows all origins
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]}}) # Restrict to a single origin
db.init_app(app)  # Initialize SQLAlchemy 


# Register the middleware (apply before every request)
# ✅ This ensures token validation before each request
app.before_request(verify_token)

# Register the user controller blueprint
app.register_blueprint(user_controller, url_prefix='/users')
app.register_blueprint(auth_controller, url_prefix='/auth')
app.register_blueprint(credit_card_controller, url_prefix='/credit_cards')
app.register_blueprint(friendship_controller, url_prefix='/friendship')
app.register_blueprint(transaction_controller, url_prefix='/transactions')
app.register_blueprint(api_controller, url_prefix='/api')  


# Check if we should create the database on startup
if getenv('CREATE_DB_ON_STARTUP', False):
    print("🚀 Creating database...")
    with app.app_context():
        init_models()  
        db.create_all()
        print("✅ Database created!")
else:
    print(" ⚠️  Database creation skipped.")
    
      
if __name__ == '__main__':
    app.run(debug=True)

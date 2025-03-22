from flask import Flask
from flask_cors import CORS
from config import Config
from models import db, init_models
from controllers.user_controller import user_controller 
from controllers.auth_controller import auth_controller 
from os import getenv
from dotenv import load_dotenv
from configuration.auth_filter import verify_token

# Load enviorement variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# Enable CORS for all routes
# CORS(app) # Allows all origins
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}}) # Restrict to a single origin
db.init_app(app)  # Initialize SQLAlchemy 


# Register the middleware (apply before every request)
# ✅ This ensures token validation before each request
app.before_request(verify_token)

# Register the user controller blueprint
app.register_blueprint(user_controller, url_prefix='/users')
app.register_blueprint(auth_controller, url_prefix='/auth')

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

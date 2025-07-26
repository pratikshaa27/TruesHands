from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import google.generativeai as genai
from pymongo import MongoClient
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# MongoDB Connection
app.mongo_client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
app.db = app.mongo_client[os.getenv('MONGO_DB', 'Truehands')]

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
app.gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Chatbot context
app.chatbot_context = """
You are a chatbot for a donation platform. Only answer questions about:
1. User Registration (Institute, Donor, Supplier)
2. Institute Dashboard (requests, tracking)
3. Donor Dashboard (browsing, donating)
4. Supplier Dashboard (orders, deliveries)
5. Admin Dashboard (monitoring, disputes)
"""

# Initialize JWT
jwt = JWTManager(app)

# Import and register blueprints at the end
def register_blueprints():
    from chat import chat_bp
    from login import login_bp
    from register import register_bp
    
    app.register_blueprint(chat_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)

if __name__ == '__main__':
    # Create indexes
    with app.app_context():
        for collection_name in ['donor', 'institute', 'supplier']:
            app.db[collection_name].create_index("email", unique=True)
            app.db[collection_name].create_index("createdAt")
    
    register_blueprints()
    app.run(host='0.0.0.0', port=5000, debug=True)
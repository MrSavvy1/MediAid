import os
from flask_jwt_extended import JWTManager # type: ignore
from dotenv import load_dotenv # type: ignore
from flask import jsonify # type: ignore

# Load environment variables from the .env file
load_dotenv()

# Function to initialize JWT
def init_jwt(app):
    # Set the JWT secret key from the .env file
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Initialize JWTManager
    jwt = JWTManager(app)

    # Define custom error handling for JWT-related issues

    # Handle missing authorization token
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({
            'error': 'Missing Authorization Header'
        }), 401

    # Handle expired JWT token
    @jwt.expired_token_loader
    def expired_token_callback(expired_token):
        return jsonify({
            'error': 'Token has expired',
            'expired_token': expired_token
        }), 401

    # Handle invalid JWT token
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token'
        }), 401

    # Handle revoked token (if revocation is implemented)
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has been revoked'
        }), 401

    return jwt

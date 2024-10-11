from flask import Blueprint, request, jsonify # type: ignore
from flask_bcrypt import check_password_hash # type: ignore
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity # type: ignore
from models import create_user, find_user_by_email
from bson import ObjectId # type: ignore
import datetime
from pymongo.errors import DuplicateKeyError # type: ignore

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# User Registration (Signup) Route
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'error': 'Email, password, and name are required'}), 400

    try:
        # Create the user in MongoDB
        user_id = create_user(mongo=request.app.mongo, email=email, password=password, name=name)
        return jsonify({'message': 'User created successfully', 'user_id': str(user_id.inserted_id)}), 201

    except DuplicateKeyError:
        return jsonify({'error': 'Email already exists'}), 400

# User Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Find the user by email
    user = find_user_by_email(mongo=request.app.mongo, email=email)

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Check if the password is correct
    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Create a JWT token valid for 24 hours
    access_token = create_access_token(identity={'email': user['email'], 'name': user['name'], 'id': str(user['_id'])},
                                       expires_delta=datetime.timedelta(hours=24))
    
    return jsonify({
        'access_token': access_token,
        'message': 'Login successful'
    }), 200

# Protected Route (Example for JWT usage)
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    # Retrieve the current user's identity from the JWT token
    current_user = get_jwt_identity()
    return jsonify({
        'message': f"Welcome {current_user['name']}! Here is your profile information.",
        'user': current_user
    }), 200

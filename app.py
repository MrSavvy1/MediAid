from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from chat import get_response
import requests
import logging
import re
import random
import string
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for simplicity
app.secret_key = os.getenv("SECRET_KEY")

APPWRITE_ENDPOINT = os.getenv("APPWRITE_URl")
APPWRITE_PROJECT_ID = os.getenv("PROJECT_ID_APPWRITE")
APPWRITE_API_KEY = os.getenv("API_KEY_APPWRITE")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def generate_user_id(username):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    user_id = f"{username}_{random_string}"
    user_id = re.sub(r'[^a-zA-Z0-9._-]', '', user_id)  # Remove invalid characters
    return user_id[:36]  # Ensure the user_id is at most 36 characters long

@app.get("/")
def index_get():
    return render_template("index.html")

@app.route('/store-session', methods=['POST'])
def store_session():
    data = request.get_json()

    try:
        # Store session data in Flask's session object
        session['user'] = {
            'id': data.get('id'),
            'createdAt': data.get('createdAt'),
            'updatedAt': data.get('updatedAt'),
            'accessedAt': data.get('accessedAt'),
            'email': data.get('email'),
            'formEmail': data.get('formEmail'),
            'emailVerification': data.get('emailVerification'),
            'name': data.get('name'),
            'mfa': data.get('mfa'),
            'registration': data.get('registration'),
            'status': data.get('status')
        }

        return jsonify({"message": "Session stored successfully!"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/base')
def base():
    
    if 'user' in session:
        user = session['user']
        logging.debug(f"Response status: {session}")
        stored_email = user.get('email')
        form_email = user.get('formEmail')

        # Logic to check if the email from the form matches the stored email
        if stored_email == form_email:
            return render_template("base.html")
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")

@app.post("/predict")
def predict():
    #if 'user' not in session:
     #   return jsonify({"error": "Unauthorized"}), 401
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Please fill in all fields"}), 400

    user_id = generate_user_id(username)

    response = requests.post(f'{APPWRITE_ENDPOINT}/account', json={
        'userId': user_id,
        'email': email,
        'password': password,
        'name': username
    }, headers={
        'X-Appwrite-Project': APPWRITE_PROJECT_ID,
        'X-Appwrite-Key': APPWRITE_API_KEY,
        'Content-Type': 'application/json'
    })

    logging.debug(f"Response status: {response.status_code}")
    logging.debug(f"Response content: {response.json()}")

    if response.status_code == 201:
        return jsonify({"message": "Registration successful"})
    else:
        return jsonify({"error": response.json().get('message', 'Registration failed')}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    response = requests.post(f'{APPWRITE_ENDPOINT}/account/sessions/email', json={
        'email': email,
        'password': password
    }, headers={
        'X-Appwrite-Project': APPWRITE_PROJECT_ID,
        'Content-Type': 'application/json'
    })

    logging.debug(f"Response status: {response.status_code}")
    logging.debug(f"Response content: {response.json()}")

    if response.status_code == 201:
        session['user'] = response.json()
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": response.json().get('message', 'Login failed')}), 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index_get'))

if __name__ == "__main__":
    app.run(debug=True)
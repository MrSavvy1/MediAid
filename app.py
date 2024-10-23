from flask import Flask, render_template, request, jsonify, redirect, url_for, session as flask_session
from flask_cors import CORS
from chat import get_response
import requests
import logging
import re
import random
import string
import os
from dotenv import load_dotenv

try:
    from appwrite.client import Client
except ImportError:
    print("Error: Failed to import 'appwrite.client'. Make sure you have installed the 'appwrite' package.")
from appwrite.services.users import Users

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = os.getenv("SECRET_KEY")

app.secret_key = os.getenv("SECRET_KEY", ''.join(random.choices(string.ascii_letters + string.digits, k=24)))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Appwrite client
client = Client()

# Set endpoint, project, and key using environment variables
APPWRITE_ENDPOINT = os.getenv('APPWRITE_URL')
APPWRITE_PROJECT_ID = os.getenv('PROJECT_ID_APPWRITE')
APPWRITE_API_KEY = os.getenv('API_KEY_APPWRITE')

client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)
users_service = Users(client)

def generate_user_id(username):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    user_id = f"{username}_{random_string}"
    user_id = re.sub(r'[^a-zA-Z0-9._-]', '', user_id)
    return user_id[:36]

@app.get("/")
def index_get():
    return render_template("index.html")

@app.route('/users', methods=['GET'])
def get_users():
    try:
        result = users_service.list()
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/store-session', methods=['POST'])
def store_session():
    data = request.get_json()
    try:
        # Store session data in Flask's session object
        flask_session['user'] = {
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
        logging.debug(f"Session stored: {flask_session['user']}")
        return jsonify({"message": "Session stored successfully!"}), 200
    except Exception as e:
        logging.error(f"Error storing session: {e}")
        return jsonify({"message": str(e)}), 500

@app.route('/base')
def base():
    logging.debug(f"Session data: {flask_session}")
    if 'user' in flask_session:
        user = flask_session['user']
        logging.debug(f"User session data: {user}")
        return render_template("base.html")
    else:
        return render_template("index.html")

@app.post("/predict")
def predict():
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
        flask_session['user'] = response.json()
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": response.json().get('message', 'Login failed')}), 401

@app.route('/logout')
def logout():
    flask_session.pop('user', None)
    return redirect(url_for('index_get'))

if __name__ == "__main__":
    app.run(debug=True)
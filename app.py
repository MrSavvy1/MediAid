from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from chat import get_response
import requests
import logging
import re
import random
import string


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for simplicity
app.secret_key = 'standard_d6f545703000041713307cc8800beb804e766f49d9bf0e30e1d591f2d7165dd6a1850f10e742045e714feb42ea2fa38e99d682d70c22f2e0ec0d5f87d54f9a28db5e6ec39559d8cf02d94751348e832a9cf3c3b081f0ca3e16049fb245afef0d102c241afd7c6f76f73e0f710197f19b1286c27dadede0730914088ecd95d02e'

APPWRITE_ENDPOINT = 'https://cloud.appwrite.io/v1'
APPWRITE_PROJECT_ID = '670da57a0034f6496f28'
APPWRITE_API_KEY = 'Edethu'

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
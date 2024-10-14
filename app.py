from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from chat import get_response
import requests

app = Flask(__name__)
CORS(app)
app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5lZGhlc2dzZnl3cHNiaHJ3bmFrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyODkxMDU0MSwiZXhwIjoyMDQ0NDg2NTQxfQ.ZdQVXgedsLjSLCsjFbhRoW3DeyCGEPn7ac9K5qycMfE'

SUPABASE_URL = 'https://nedhesgsfywpsbhrwnak.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5lZGhlc2dzZnl3cHNiaHJ3bmFrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg5MTA1NDEsImV4cCI6MjA0NDQ4NjU0MX0.8KahX7pzXlZw0bVaX4nYeOTkJEYTIm71nyhv5z4Vs4c'

@app.get("/")
def index_get():
    return render_template("index.html")

@app.route('/base')
def base():
    if 'user' in session:
        return render_template("base.html")
    else:
        return redirect(url_for('index_get'))

@app.post("/predict")
def predict():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    response = requests.post(f'{SUPABASE_URL}/auth/v1/token?grant_type=password', json={
        'email': email,
        'password': password
    }, headers={
        'apikey': SUPABASE_KEY,
        'Content-Type': 'application/json'
    })
    if response.status_code == 200:
        session['user'] = response.json()
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Login failed"}), 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index_get'))

if __name__ == "__main__":
    app.run(debug=True)
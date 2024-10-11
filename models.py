import os
from dotenv import load_dotenv # type: ignore
from flask_pymongo import PyMongo # type: ignore
from flask_bcrypt import Bcrypt # type: ignore

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

# Load environment variables from the .env file
load_dotenv()

# MongoDB initialization function
def init_db(app):
    # Get the MongoDB URI from the .env file
    app.config["MONGO_URI"] = os.getenv("MONGO_URL")
    mongo = PyMongo(app)  # Initialize the PyMongo connection
    return mongo

# Function to create a new user in MongoDB
def create_user(mongo, email, password, name):
    users = mongo.db.users  # Reference the 'users' collection in the database
    # Hash the password using bcrypt
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    # Insert the new user into the 'users' collection
    user_id = users.insert_one({
        'email': email, 
        'password': hashed_pw, 
        'name': name
    })
    return user_id

# Function to find a user by email in MongoDB
def find_user_by_email(mongo, email):
    users = mongo.db.users  # Reference the 'users' collection in the database
    return users.find_one({'email': email})  # Search for the user by email

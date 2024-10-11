from flask import Flask # type: ignore
from models import init_db
from auth_routes import auth_bp
from utils import init_jwt
from dotenv import load_dotenv # type: ignore
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set the JWT Secret Key from the .env file
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Initialize MongoDB and JWT
mongo = init_db(app)
jwt = init_jwt(app)

# Register authentication routes
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import datetime
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask import make_response
from security import SecurityManager, rate_limit

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, supports_credentials=True)

# Security configuration
app.config["JWT_SECRET"] = os.getenv("JWT_SECRET")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
security = SecurityManager(app)
security.init_app(app)

# MongoDB setup
mongo = PyMongo(app)

# Default admin credentials
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
DEFAULT_ADMIN_PASSWORD_PLAIN = os.getenv("DEFAULT_ADMIN_PASSWORD")

def create_default_admin():
    admin = mongo.db.users.find_one({"email": DEFAULT_ADMIN_EMAIL})
    if not admin:
        hashed_pw = security.hash_password(DEFAULT_ADMIN_PASSWORD_PLAIN)
        mongo.db.users.insert_one({
            "email": DEFAULT_ADMIN_EMAIL,
            "password": hashed_pw,
            "role": "admin",
            "tenant_id": "system",
            "2fa_enabled": False,
            "created_at": datetime.datetime.utcnow()
        })
        print("Default admin created.")
    else:
        print("ℹAdmin already exists.")

# Initialize admin
create_default_admin()

# New token verification decorator 
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT passed in Authorization header as "Bearer <token>"
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
            if data.get("role") != "admin":
                return jsonify({"error": "Unauthorized, admin only"}), 403
            request.user = data  # you can access user info from request.user in the route if needed
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

# --- HTML Page Routes ---
@app.route("/")
def serve_home():
    return render_template("index.html", google_client_id=os.getenv("GOOGLE_CLIENT_ID"))

@app.route("/admin")
@security.verify_session
@security.require_role(["admin"])
def serve_admin():
    return render_template("admin.html")

@app.route("/user")
@security.verify_session
def serve_user():
    return render_template("user.html")

# --- API Endpoints ---
@app.route("/api/auth/login", methods=["POST"])
@rate_limit("5 per minute")
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    two_factor_token = data.get("2fa_token")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = mongo.db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 401

    if not security.verify_password(password, user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # Check 2FA if enabled
    if user.get("2fa_enabled"):
        if not two_factor_token:
            return jsonify({"error": "2FA token required"}), 401
        if not security.verify_2fa(user["2fa_secret"], two_factor_token):
            return jsonify({"error": "Invalid 2FA token"}), 401

    return security.create_session_token(user)

@app.route("/api/auth/2fa/setup", methods=["POST"])
@security.verify_session
def setup_2fa():
    user = request.user
    db_user = mongo.db.users.find_one({"email": user["email"]})
    
    if db_user.get("2fa_enabled"):
        return jsonify({"error": "2FA already enabled"}), 400

    setup_data = security.setup_2fa(user["email"])
    
    # Store the secret temporarily (user needs to verify before enabling)
    mongo.db.users.update_one(
        {"email": user["email"]},
        {"$set": {"2fa_temp_secret": setup_data["secret"]}}
    )
    
    return jsonify({
        "secret": setup_data["secret"],
        "uri": setup_data["uri"]
    })

@app.route("/api/auth/2fa/verify", methods=["POST"])
@security.verify_session
def verify_2fa_setup():
    data = request.get_json()
    token = data.get("token")
    
    user = request.user
    db_user = mongo.db.users.find_one({"email": user["email"]})
    
    if not db_user.get("2fa_temp_secret"):
        return jsonify({"error": "No pending 2FA setup"}), 400
    
    if not security.verify_2fa(db_user["2fa_temp_secret"], token):
        return jsonify({"error": "Invalid token"}), 401
    
    # Enable 2FA
    mongo.db.users.update_one(
        {"email": user["email"]},
        {
            "$set": {
                "2fa_enabled": True,
                "2fa_secret": db_user["2fa_temp_secret"]
            },
            "$unset": {"2fa_temp_secret": ""}
        }
    )
    
    return jsonify({"message": "2FA enabled successfully"})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.delete_cookie('session_token')
    return response

@app.route("/api/tenants", methods=["GET"])
@security.verify_session
@security.require_role(["admin"])
def get_tenants():
    tenants = list(mongo.db.tenants.find({}, {"_id": 0}))
    return jsonify(tenants)

@app.route("/api/tenants", methods=["POST"])
@security.verify_session
@security.require_role(["admin"])
def create_tenant():
    data = request.get_json()
    tenant_id = data.get("tenant_id")
    name = data.get("name")
    
    if not tenant_id or not name:
        return jsonify({"error": "Tenant ID and name required"}), 400
    
    if mongo.db.tenants.find_one({"tenant_id": tenant_id}):
        return jsonify({"error": "Tenant ID already exists"}), 400
    
    tenant = {
        "tenant_id": tenant_id,
        "name": name,
        "settings": data.get("settings", {}),
        "quota": data.get("quota", {}),
        "created_at": datetime.datetime.utcnow()
    }
    
    mongo.db.tenants.insert_one(tenant)
    return jsonify({"message": "Tenant created successfully"})

@app.route("/api/drift/configs", methods=["GET"])
@security.verify_session
def get_drift_configs():
    tenant_id = request.user.get("tenant_id")
    if not tenant_id:
        return jsonify({"error": "Tenant ID required"}), 400
    
    configs = list(mongo.db.drift_configs.find(
        {"tenant_id": tenant_id},
        {"_id": 0}
    ))
    return jsonify(configs)

@app.route("/api/drift/configs", methods=["POST"])
@security.verify_session
def create_drift_config():
    tenant_id = request.user.get("tenant_id")
    if not tenant_id:
        return jsonify({"error": "Tenant ID required"}), 400
    
    data = request.get_json()
    config = {
        "tenant_id": tenant_id,
        "config_id": data.get("config_id"),
        "thresholds": data.get("thresholds", {}),
        "alerts": data.get("alerts", []),
        "created_at": datetime.datetime.utcnow()
    }
    
    mongo.db.drift_configs.insert_one(config)
    return jsonify({"message": "Drift configuration created successfully"})

#Block back button from sending admin or user back to dashboard after logging out
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5500)

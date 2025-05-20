from functools import wraps
from flask import request, jsonify, make_response
import jwt
import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pyotp
import bcrypt
from flask import current_app

class SecurityManager:
    def __init__(self, app):
        self.app = app
        self.limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
    def init_app(self, app):
        # Configure security headers
        @app.after_request
        def add_security_headers(response):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            return response

    def create_session_token(self, user_data):
        """Create a secure session token with HTTP-only cookie"""
        payload = {
            "email": user_data["email"],
            "role": user_data["role"],
            "tenant_id": user_data.get("tenant_id"),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
        
        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie(
            'session_token',
            token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=7200  # 2 hours
        )
        return response

    def verify_session(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get('session_token')
            if not token:
                return jsonify({"error": "Session token missing"}), 401

            try:
                data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
                request.user = data
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Session expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid session"}), 401

            return f(*args, **kwargs)
        return decorated

    def require_role(self, roles):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if not hasattr(request, 'user'):
                    return jsonify({"error": "Authentication required"}), 401
                
                if request.user.get("role") not in roles:
                    return jsonify({"error": "Insufficient permissions"}), 403
                
                return f(*args, **kwargs)
            return decorated
        return decorator

    def setup_2fa(self, user_id):
        """Generate 2FA secret for a user"""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_id,
            issuer_name="BlindSpotX"
        )
        return {
            "secret": secret,
            "uri": provisioning_uri
        }

    def verify_2fa(self, secret, token):
        """Verify 2FA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

    def hash_password(self, password):
        """Hash password with bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Rate limiting decorators
def rate_limit(limit_string):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            return Limiter.limit(limit_string)(f)(*args, **kwargs)
        return decorated
    return decorator 
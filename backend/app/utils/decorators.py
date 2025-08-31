from functools import wraps
from flask import jsonify, current_app
import traceback

def handle_errors(f):
    """Decorator to handle errors in API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            
            # Return appropriate error response
            return jsonify({
                "error": "Internal server error",
                "message": str(e) if current_app.debug else "Something went wrong"
            }), 500
    return decorated_function

def require_json(f):
    """Decorator to require JSON request body."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        return f(*args, **kwargs)
    return decorated_function

def cache_response(timeout=300):
    """Decorator to cache API responses."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory cache implementation
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if hasattr(current_app, 'cache') and cache_key in current_app.cache:
                cached_data, timestamp = current_app.cache[cache_key]
                if time.time() - timestamp < timeout:
                    return cached_data
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Cache result
            if hasattr(current_app, 'cache'):
                current_app.cache[cache_key] = (result, time.time())
            
            return result
        return decorated_function
    return decorator

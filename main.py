import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
import json
from retrying import retry
import requests
import logging

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",
    enabled=not os.environ.get('TESTING', False)  # Disable in testing mode
)


limiter.init_app(app)

@app.route('/users', methods=['POST'])
@limiter.limit("10 per minute")
def register_user():
    """
    Register a new user
    Expects JSON payload with user data
    """
    try:

        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        user_data = request.get_json()
        

        required_fields = ['name', 'email']
        missing_fields = []
        for field in required_fields:
            if field not in user_data or user_data[field] is None or (isinstance(user_data[field], str) and not user_data[field].strip()):
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        

        if not user_data['name'].strip():
            return jsonify({'error': 'Name cannot be empty or just whitespace'}), 400
        

        try:
            external_response = call_external_api_with_retry(user_data)
            
            
            response_data = {
                'message': 'User registered successfully',
                'user_data': {
                    'name': user_data['name'],
                    'email': user_data['email']
                },
                'external_api_response': external_response
            }
            return jsonify(response_data), 201
            
        except Exception as e:
            logger.error(f"External API call failed: {str(e)}")
            
            return jsonify({
                'message': 'User data validated and processed',
                'warning': 'External API call failed, but user data saved',
                'user_data': {
                    'name': user_data['name'],
                    'email': user_data['email']
                }
            }), 201
    
    except Exception as e:
        logger.error(f"Unexpected error in register_user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@retry(stop_max_attempt_number=3, wait_fixed=1000)
def call_external_api_with_retry(user_data):
    """
    Make an external API call with retry logic
    Retries up to 3 times with 1 second delay between attempts
    """
    import random
    

    if random.random() < 0.3:
        raise requests.exceptions.RequestException("Simulated external API failure")
    

    return {'status': 'success', 'user_id': f"user_{len(user_data['name'])}"}


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded error"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429


if __name__ == '__main__':
    app.run(debug=True)
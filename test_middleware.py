#!/usr/bin/env python3
"""
Quick test to see if field normalization middleware is working
"""

from flask import Flask, request, g
import logging
logging.basicConfig(level=logging.INFO)

# Test the middleware function directly
from utils.field_normalization_middleware import normalize_request_middleware

app = Flask(__name__)

@app.before_request
def test_middleware():
    print('Middleware called!')
    normalize_request_middleware()
    if hasattr(g, 'normalized_request_data'):
        print(f'Normalized data: {g.normalized_request_data}')
    else:
        print('No normalized data found')

@app.route('/test', methods=['POST'])
def test_endpoint():
    return {'status': 'ok'}

if __name__ == '__main__':
    with app.test_client() as client:
        print("Testing middleware with Plant Name...")
        response = client.post('/test', json={'Plant Name': 'Test Plant'})
        print(f'Response: {response.status_code}')


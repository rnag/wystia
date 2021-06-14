"""
Utilities for API Gateway response formatting
"""
import json


def format_response(data, status=200):
    return {
        'body': json.dumps(data),
        'headers': {
            'Content-Type': 'application/json'
        },
        'statusCode': int(status)
    }


def format_error(msg, code='BadRequest', status=400):
    data = {
        'success': False,
        'error': {
            'code': code,
            'message': msg
        }
    }

    return format_response(data, status)

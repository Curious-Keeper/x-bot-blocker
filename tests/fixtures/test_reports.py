import json
from datetime import datetime, timedelta

def create_test_report_data():
    """Create sample report data for testing"""
    now = datetime.now()
    return {
        'period': {
            'start': (now - timedelta(days=7)).isoformat(),
            'end': now.isoformat()
        },
        'summary': {
            'total_api_calls': 1000,
            'total_blocks': 150,
            'total_false_positives': 10,
            'average_cpu_usage': 45.5,
            'average_memory_usage': 55.5,
            'average_api_response_time': 0.15
        },
        'trends': {
            'api_calls': 10.5,
            'blocks': 5.2,
            'false_positives': -0.5,
            'cpu_usage': 2.1,
            'memory_usage': 1.8,
            'api_response_time': -0.02
        },
        'errors': [
            {
                'timestamp': (now - timedelta(days=1)).isoformat(),
                'type': 'API_ERROR',
                'message': 'Rate limit exceeded',
                'count': 5
            }
        ]
    }

def create_test_report_file(filepath):
    """Create a test report JSON file"""
    data = create_test_report_data()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    return filepath 
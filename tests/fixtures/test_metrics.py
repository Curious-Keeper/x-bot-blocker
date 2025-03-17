import pandas as pd
from datetime import datetime, timedelta

def create_test_metrics_data():
    """Create sample metrics data for testing"""
    dates = [datetime.now() - timedelta(days=i) for i in range(30)]
    
    # Create blocks data (100 blocks per day for 30 days)
    blocks = [100 for _ in range(30)]
    
    # Create error data (2 types of errors on specific days)
    errors = []
    for i in range(30):
        if i % 15 == 0:  # Every 15th day
            errors.append({
                'timestamp': dates[i].isoformat(),
                'type': 'API_ERROR',
                'message': 'Rate limit exceeded',
                'count': 5
            })
        elif i % 15 == 7:  # Every 15th day + 7
            errors.append({
                'timestamp': dates[i].isoformat(),
                'type': 'VALIDATION_ERROR',
                'message': 'Invalid response format',
                'count': 3
            })
    
    data = {
        'timestamp': dates,
        'api_calls': [1000 + i * 10 for i in range(30)],
        'failed_requests': [5 + i for i in range(30)],
        'blocks': blocks,
        'false_positives': [2 + i for i in range(30)],
        'cpu_usage': [30 + i for i in range(30)],
        'memory_usage': [40 + i for i in range(30)],
        'api_response_time': [0.1 + i * 0.01 for i in range(30)],
        'errors': errors
    }
    return pd.DataFrame(data)

def create_test_metrics_file(filepath):
    """Create a test metrics CSV file"""
    df = create_test_metrics_data()
    df.to_csv(filepath, index=False)
    return filepath 
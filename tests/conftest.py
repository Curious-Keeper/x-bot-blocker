import os
import pytest
import json
import pandas as pd
from datetime import datetime, timedelta
from x_bot_blocker.config_manager import ConfigManager

@pytest.fixture(scope="session")
def config():
    """Fixture for configuration manager"""
    return ConfigManager()

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Fixture for test data directory"""
    test_dir = tmp_path_factory.mktemp("test_data")
    return test_dir

@pytest.fixture(scope="function")
def metrics_data(test_data_dir):
    """Fixture for test metrics data"""
    # Create test data
    dates = pd.date_range(start=datetime.now() - timedelta(days=60), periods=60, freq='D')
    data = []
    
    for date in dates:
        # Calculate detection accuracy for this day
        blocks = 100
        false_positives = 5
        accuracy = (blocks - false_positives) / blocks if blocks > 0 else 1.0
        
        # Add test errors on specific days for error analysis
        errors = []
        if date.day in [1, 15]:  # Add errors on 1st and 15th of each month
            errors = [
                {'error': 'API Connection Error', 'count': 5, 'timestamp': str(date)},
                {'error': 'Rate Limit Exceeded', 'count': 3, 'timestamp': str(date)}
            ]
        
        data.append({
            'timestamp': date,
            'blocks_count': blocks,
            'false_positives': false_positives,
            'detection_accuracy': accuracy,
            'api_calls': 1000,
            'failed_requests': 50,
            'avg_response_time': 0.5,
            'resource_usage_cpu': 50,
            'resource_usage_memory': 60,
            'resource_usage_disk': 70,
            'errors': json.dumps(errors)
        })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    metrics_file = test_data_dir / 'test_metrics.csv'
    df.to_csv(metrics_file, index=False)
    
    # Create data directories if they don't exist
    for dir_name in ['metrics', 'reports', 'progress']:
        dir_path = os.path.join('data', dir_name)
        os.makedirs(dir_path, exist_ok=True)
    
    return metrics_file

@pytest.fixture(scope="function")
def clean_data_dirs():
    """Fixture to ensure data directories are clean before and after tests"""
    # Clean up before test
    for dir_name in ['metrics', 'reports', 'progress']:
        dir_path = os.path.join('data', dir_name)
        os.makedirs(dir_path, exist_ok=True)
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    yield
    
    # Clean up after test
    for dir_name in ['metrics', 'reports', 'progress']:
        dir_path = os.path.join('data', dir_name)
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path) 
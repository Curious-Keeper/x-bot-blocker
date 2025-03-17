import json
from datetime import datetime, timedelta

def create_test_progress_data():
    """Create sample progress data for testing"""
    now = datetime.now()
    return {
        'tasks': {
            'task_1': {
                'description': 'Implement bot detection algorithm',
                'type': 'development',
                'milestone_id': 'milestone_1',
                'status': 'completed',
                'progress': 100,
                'dependencies': [],
                'created_at': (now - timedelta(days=2)).isoformat(),
                'completed_at': (now - timedelta(days=1)).isoformat()
            },
            'task_2': {
                'description': 'Add unit tests for bot detection',
                'type': 'testing',
                'milestone_id': 'milestone_1',
                'status': 'in_progress',
                'progress': 75,
                'dependencies': ['task_1'],
                'created_at': (now - timedelta(days=1)).isoformat(),
                'completed_at': None
            }
        },
        'milestones': {
            'milestone_1': {
                'description': 'Core bot detection functionality',
                'type': 'feature',
                'tasks': ['task_1', 'task_2'],
                'created_at': (now - timedelta(days=2)).isoformat(),
                'completed_at': None
            }
        },
        'last_updated': now.isoformat()
    }

def create_test_progress_file(filepath):
    """Create a test progress JSON file"""
    data = create_test_progress_data()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    return filepath 
import pytest
import os
import json
from datetime import datetime, timedelta
from x_bot_blocker.progress import ProgressTracker
from x_bot_blocker.config_manager import ConfigManager
from tests.fixtures.test_progress import create_test_progress_data

def test_task_tracking(config, clean_data_dirs):
    """Test task tracking functionality"""
    # Initialize progress tracker
    tracker = ProgressTracker(config)
    
    # Create test task
    task_id = tracker.create_task("Test task", "Testing task tracking")
    
    # Verify task creation
    task = tracker.get_task(task_id)
    assert task is not None
    assert task['description'] == "Test task"
    assert task['type'] == "Testing task tracking"
    assert task['status'] == "pending"
    assert task['progress'] == 0
    
    # Update task progress
    tracker.update_task(task_id, progress=50, status="in_progress")
    task = tracker.get_task(task_id)
    assert task['progress'] == 50
    assert task['status'] == "in_progress"
    
    # Complete task
    tracker.update_task(task_id, progress=100, status="completed")
    task = tracker.get_task(task_id)
    assert task['progress'] == 100
    assert task['status'] == "completed"

def test_milestone_tracking(config, clean_data_dirs):
    """Test milestone tracking functionality"""
    # Initialize progress tracker
    tracker = ProgressTracker(config)
    
    # Create test milestone
    milestone_id = tracker.create_milestone("Test milestone", "Testing milestone tracking")
    
    # Create tasks for milestone
    task1_id = tracker.create_task("Task 1", "First task", milestone_id=milestone_id)
    task2_id = tracker.create_task("Task 2", "Second task", milestone_id=milestone_id)
    
    # Verify milestone creation
    milestone = tracker.milestones[milestone_id]
    assert milestone is not None
    assert milestone['description'] == "Test milestone"
    assert milestone['type'] == "Testing milestone tracking"
    assert len(milestone['tasks']) == 2
    
    # Update tasks
    tracker.update_task(task1_id, progress=100, status="completed")
    tracker.update_task(task2_id, progress=50, status="in_progress")
    
    # Verify milestone progress
    milestone = tracker.milestones[milestone_id]
    assert len(milestone['tasks']) == 2
    
    # Complete all tasks
    tracker.update_task(task2_id, progress=100, status="completed")
    
    # Verify milestone completion
    assert tracker.check_milestone_completion(milestone_id) is True

def test_progress_reporting(config, clean_data_dirs):
    """Test progress reporting functionality"""
    # Initialize progress tracker
    tracker = ProgressTracker(config)
    
    # Create test data
    milestone_id = tracker.create_milestone("Test milestone", "Testing progress reporting")
    task1_id = tracker.create_task("Task 1", "First task", milestone_id=milestone_id)
    task2_id = tracker.create_task("Task 2", "Second task", milestone_id=milestone_id)
    
    # Update tasks
    tracker.update_task(task1_id, progress=100, status="completed")
    tracker.update_task(task2_id, progress=50, status="in_progress")
    
    # Generate progress report
    report = tracker.get_progress_report()
    
    # Verify report structure
    assert 'total_tasks' in report
    assert 'completed_tasks' in report
    assert 'completion_percentage' in report
    assert 'total_milestones' in report
    assert 'completed_milestones' in report
    assert 'milestone_completion_percentage' in report
    assert 'tasks' in report
    assert 'milestones' in report
    
    # Verify report content
    assert report['total_tasks'] == 2
    assert report['completed_tasks'] == 1
    assert report['completion_percentage'] == 50.0
    assert report['total_milestones'] == 1
    assert report['completed_milestones'] == 0
    assert report['milestone_completion_percentage'] == 0.0

def test_task_dependencies(config, clean_data_dirs):
    """Test task dependency handling"""
    # Initialize progress tracker
    tracker = ProgressTracker(config)
    
    # Create test tasks
    task1_id = tracker.create_task("Task 1", "First task")
    task2_id = tracker.create_task("Task 2", "Second task", dependencies=[task1_id])
    
    # Verify task2 is blocked
    task2 = tracker.get_task(task2_id)
    assert task2['status'] == "pending"
    
    # Complete task1
    tracker.update_task(task1_id, progress=100, status="completed")
    
    # Verify task2 is unblocked
    task2 = tracker.get_task(task2_id)
    assert task2['status'] == "pending"

def test_progress_persistence(config, clean_data_dirs):
    """Test progress data persistence"""
    # Initialize progress tracker
    tracker = ProgressTracker(config)
    
    # Create test data
    task_id = tracker.create_task("Test task", "Testing persistence")
    tracker.update_task(task_id, progress=50, status="in_progress")
    
    # Save progress data
    tracker.save_progress()
    
    # Create new tracker instance
    new_tracker = ProgressTracker(config)
    
    # Verify data was loaded
    task = new_tracker.get_task(task_id)
    assert task is not None
    assert task['progress'] == 50
    assert task['status'] == "in_progress"

def test_load_existing_progress(config, clean_data_dirs):
    """Test loading existing progress data"""
    # Create test progress data
    test_data = create_test_progress_data()
    
    # Save test data
    progress_dir = config.get('progress.data_directory', 'data/progress')
    os.makedirs(progress_dir, exist_ok=True)
    progress_file = os.path.join(progress_dir, 'progress.json')
    
    with open(progress_file, 'w') as f:
        json.dump(test_data, f, indent=4)
    
    # Initialize progress tracker
    tracker = ProgressTracker(config)
    
    # Verify loaded data
    assert len(tracker.tasks) == 2
    assert len(tracker.milestones) == 1
    
    # Check task data
    task1 = tracker.get_task('task_1')
    assert task1['description'] == 'Implement bot detection algorithm'
    assert task1['status'] == 'completed'
    assert task1['progress'] == 100
    
    task2 = tracker.get_task('task_2')
    assert task2['description'] == 'Add unit tests for bot detection'
    assert task2['status'] == 'in_progress'
    assert task2['progress'] == 75
    
    # Check milestone data
    milestone = tracker.milestones['milestone_1']
    assert milestone['description'] == 'Core bot detection functionality'
    assert len(milestone['tasks']) == 2 
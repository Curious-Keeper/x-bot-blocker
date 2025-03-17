import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from x_bot_blocker.config_manager import ConfigManager

class ProgressTracker:
    """Class for tracking progress of tasks and milestones"""
    
    def __init__(self, config: ConfigManager):
        """Initialize progress tracker with configuration"""
        self.config = config
        self.tasks = {}
        self.milestones = {}
        self.load_progress()
    
    def create_task(self, description: str, task_type: str, milestone_id: Optional[str] = None, dependencies: Optional[List[str]] = None) -> str:
        """Create a new task and return its ID"""
        task_id = f"task_{len(self.tasks) + 1}"
        self.tasks[task_id] = {
            'description': description,
            'type': task_type,
            'milestone_id': milestone_id,
            'status': 'pending',
            'progress': 0,
            'dependencies': dependencies or [],
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        if milestone_id:
            if milestone_id not in self.milestones:
                raise ValueError(f"Milestone {milestone_id} not found")
            self.milestones[milestone_id]['tasks'].append(task_id)
        
        self.save_progress()
        return task_id
    
    def get_task(self, task_id: str) -> Dict:
        """Get task details by ID"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.tasks[task_id]
    
    def update_task(self, task_id: str, progress: Optional[int] = None, status: Optional[str] = None) -> None:
        """Update task progress and/or status"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        if progress is not None:
            if not 0 <= progress <= 100:
                raise ValueError("Progress must be between 0 and 100")
            task['progress'] = progress
        
        if status is not None:
            task['status'] = status
            if status == 'completed':
                task['progress'] = 100
                task['completed_at'] = datetime.now().isoformat()
        
        self.save_progress()
    
    def create_milestone(self, description: str, milestone_type: str, tasks: Optional[List[str]] = None) -> str:
        """Create a new milestone and return its ID"""
        milestone_id = f"milestone_{len(self.milestones) + 1}"
        self.milestones[milestone_id] = {
            'description': description,
            'type': milestone_type,
            'tasks': tasks or [],
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        self.save_progress()
        return milestone_id
    
    def check_milestone_completion(self, milestone_id: str) -> bool:
        """Check if all tasks in a milestone are completed"""
        if milestone_id not in self.milestones:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        milestone = self.milestones[milestone_id]
        all_completed = all(
            self.tasks.get(task_id, {}).get('status') == 'completed'
            for task_id in milestone['tasks']
        )
        
        if all_completed and not milestone.get('completed_at'):
            milestone['completed_at'] = datetime.now().isoformat()
            self.save_progress()
        
        return all_completed
    
    def get_progress_report(self) -> Dict:
        """Generate a progress report"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task['status'] == 'completed')
        total_milestones = len(self.milestones)
        completed_milestones = sum(1 for m_id in self.milestones if self.check_milestone_completion(m_id))
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_milestones': total_milestones,
            'completed_milestones': completed_milestones,
            'milestone_completion_percentage': (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0,
            'tasks': self.tasks,
            'milestones': self.milestones
        }
    
    def save_progress(self) -> None:
        """Save progress data to file"""
        progress_dir = self.config.get('progress.data_directory', 'data/progress')
        os.makedirs(progress_dir, exist_ok=True)
        
        progress_file = os.path.join(progress_dir, 'progress.json')
        progress_data = {
            'tasks': self.tasks,
            'milestones': self.milestones,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=4)
    
    def load_progress(self) -> None:
        """Load progress data from file"""
        progress_dir = self.config.get('progress.data_directory', 'data/progress')
        progress_file = os.path.join(progress_dir, 'progress.json')
        
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
                self.tasks = progress_data.get('tasks', {})
                self.milestones = progress_data.get('milestones', {})
    
    def check_dependencies(self, task_id: str) -> bool:
        """Check if all dependencies for a task are completed"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        return all(
            self.tasks.get(dep_id, {}).get('status') == 'completed'
            for dep_id in task['dependencies']
        ) 
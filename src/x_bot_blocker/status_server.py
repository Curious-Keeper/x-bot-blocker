from flask import Flask, jsonify, render_template, url_for
import psutil
import os
from datetime import datetime
import json
from functools import lru_cache
import time

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

# Cache metrics for 5 seconds
@lru_cache(maxsize=1)
def get_bot_process():
    """Get the bot process if it's running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'x_bot_blocker.py' in ' '.join(proc.info['cmdline']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

# Cache logs for 10 seconds
@lru_cache(maxsize=1)
def read_recent_logs():
    """Read recent logs from the bot's log file"""
    log_file = os.getenv('LOG_FILE', 'bot_blocker.log')
    try:
        with open(log_file, 'r') as f:
            # Get last 10 lines
            return f.readlines()[-10:]
    except Exception:
        return []

# Cache metrics for 5 seconds
@lru_cache(maxsize=1)
def get_bot_metrics():
    """Get current bot metrics"""
    # Get the project root directory (two levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    metrics_file = os.path.join(project_root, 'data', 'metrics.json')
    
    try:
        with open(metrics_file, 'r') as f:
            return json.load(f)
    except Exception:
        return {
            'total_blocks': 0,
            'false_positives': 0,
            'api_calls': 0,
            'last_scan_time': None,
            'errors': []
        }

# Cache process info for 5 seconds
@lru_cache(maxsize=1)
def get_process_info():
    """Get cached process information"""
    bot_process = get_bot_process()
    if not bot_process:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'uptime': 0
        }
    
    try:
        return {
            'cpu_percent': bot_process.cpu_percent(interval=1.0),  # Use interval to reduce CPU usage
            'memory_percent': bot_process.memory_percent(),
            'uptime': (datetime.now() - datetime.fromtimestamp(bot_process.create_time())).total_seconds()
        }
    except Exception:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'uptime': 0
        }

@app.route('/')
def index():
    """Serve the status dashboard"""
    process_info = get_process_info()
    recent_logs = read_recent_logs()
    metrics = get_bot_metrics()
    bot_process = get_bot_process()
    
    return render_template('status.html',
                         status='running' if bot_process else 'stopped',
                         process=process_info,
                         metrics=metrics,
                         recent_logs=recent_logs)

@app.route('/status')
def get_status():
    """Get overall bot status"""
    bot_process = get_bot_process()
    recent_logs = read_recent_logs()
    metrics = get_bot_metrics()
    process_info = get_process_info()
    
    return jsonify({
        'status': 'running' if bot_process else 'stopped',
        'pid': bot_process.info['pid'] if bot_process else None,
        'uptime': process_info['uptime'],
        'recent_logs': recent_logs,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def get_health():
    """Get detailed health information"""
    bot_process = get_bot_process()
    if not bot_process:
        return jsonify({
            'status': 'unhealthy',
            'reason': 'Bot process not running',
            'timestamp': datetime.now().isoformat()
        })
    
    process_info = get_process_info()
    
    return jsonify({
        'status': 'healthy',
        'process': {
            'pid': bot_process.info['pid'],
            'cpu_percent': process_info['cpu_percent'],
            'memory_percent': process_info['memory_percent'],
            'uptime': process_info['uptime']
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('STATUS_SERVER_PORT', 8080))
    # Use threaded=False to reduce CPU usage
    app.run(host='0.0.0.0', port=port, threaded=False) 
from flask import Flask, jsonify, render_template
import psutil
import os
from datetime import datetime
import json

app = Flask(__name__)

def get_bot_process():
    """Get the bot process if it's running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'x_bot_blocker.py' in ' '.join(proc.info['cmdline']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

def read_recent_logs():
    """Read recent logs from the bot's log file"""
    log_file = os.getenv('LOG_FILE', 'bot_blocker.log')
    try:
        with open(log_file, 'r') as f:
            # Get last 10 lines
            return f.readlines()[-10:]
    except Exception:
        return []

def get_bot_metrics():
    """Get current bot metrics"""
    metrics_file = 'data/metrics.json'
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

@app.route('/')
def index():
    """Serve the status dashboard"""
    bot_process = get_bot_process()
    recent_logs = read_recent_logs()
    metrics = get_bot_metrics()
    
    process_info = {
        'cpu_percent': bot_process.cpu_percent() if bot_process else 0,
        'memory_percent': bot_process.memory_percent() if bot_process else 0,
        'uptime': (datetime.now() - datetime.fromtimestamp(bot_process.create_time())).total_seconds() if bot_process else 0
    }
    
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
    
    return jsonify({
        'status': 'running' if bot_process else 'stopped',
        'pid': bot_process.info['pid'] if bot_process else None,
        'uptime': (datetime.now() - datetime.fromtimestamp(bot_process.create_time())).total_seconds() if bot_process else 0,
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
    
    # Get process metrics
    try:
        cpu_percent = bot_process.cpu_percent()
        memory_percent = bot_process.memory_percent()
        
        return jsonify({
            'status': 'healthy',
            'process': {
                'pid': bot_process.info['pid'],
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'uptime': (datetime.now() - datetime.fromtimestamp(bot_process.create_time())).total_seconds()
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'reason': str(e),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('STATUS_SERVER_PORT', 8080))
    app.run(host='0.0.0.0', port=port) 
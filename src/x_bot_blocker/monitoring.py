import logging
import psutil
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from x_bot_blocker.config_manager import ConfigManager
import requests
import json
import os
import csv
import threading
import queue

class MonitoringSystem:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load monitoring settings
        self.settings = self.config.get('monitoring', {})
        
        # Initialize metrics
        self.metrics = {
            'start_time': datetime.now(),
            'blocks_count': 0,
            'api_calls': 0,
            'errors': [],
            'false_positives': 0,
            'detection_accuracy': 1.0,
            'system_uptime': 0,
            'resource_usage': {
                'cpu': 0.0,
                'memory': 0.0,
                'disk': 0.0
            },
            'response_times': [],
            'failed_requests': 0
        }
        
        # Alert thresholds
        self.thresholds = {
            'max_cpu_usage': self.settings.get('max_cpu_usage', 80.0),
            'max_memory_usage': self.settings.get('max_memory_usage', 80.0),
            'max_disk_usage': self.settings.get('max_disk_usage', 90.0),
            'min_detection_accuracy': self.settings.get('min_detection_accuracy', 0.95),
            'max_error_rate': self.settings.get('max_error_rate', 0.01),
            'max_false_positive_rate': self.settings.get('max_false_positive_rate', 0.01)
        }
        
        # Initialize alert history
        self.alert_history = {}
        
        # Metrics queue for batch processing
        self.metrics_queue = queue.Queue()
        
        # Start monitoring threads if enabled
        if self.config.get('monitoring.enabled', True):
            self._start_monitoring_threads()
        
    def _start_monitoring_threads(self):
        """Start background monitoring threads"""
        # Metrics collection thread
        if self.config.get('monitoring.metrics.collection.enabled', True):
            threading.Thread(
                target=self._metrics_collection_loop,
                daemon=True
            ).start()
        
        # Metrics export thread
        if self.config.get('monitoring.metrics.export.enabled', True):
            threading.Thread(
                target=self._metrics_export_loop,
                daemon=True
            ).start()

    def _metrics_collection_loop(self):
        """Background thread for collecting metrics"""
        interval = self.config.get('monitoring.metrics.collection.interval', 60)
        while True:
            try:
                self.update_metrics()
                self._check_thresholds()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {str(e)}")

    def _metrics_export_loop(self):
        """Background thread for exporting metrics"""
        interval = self.config.get('monitoring.metrics.export.interval', 3600)
        while True:
            try:
                self._export_metrics()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in metrics export: {str(e)}")

    def update_metrics(self):
        """Update system metrics"""
        try:
            # Update system uptime
            self.metrics['system_uptime'] = time.time() - psutil.boot_time()
            
            # Update resource usage
            self.metrics['resource_usage']['cpu'] = psutil.cpu_percent()
            self.metrics['resource_usage']['memory'] = psutil.virtual_memory().percent
            self.metrics['resource_usage']['disk'] = psutil.disk_usage('/').percent
            
            # Calculate average response time
            if self.metrics['response_times']:
                avg_response = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
                self.metrics['avg_response_time'] = avg_response
            
            # Calculate error rate
            total_requests = self.metrics['api_calls']
            if total_requests > 0:
                self.metrics['error_rate'] = (self.metrics['failed_requests'] / total_requests) * 100
            
            # Add to metrics queue for batch processing
            self.metrics_queue.put({
                'timestamp': datetime.now().isoformat(),
                **self.metrics
            })
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {str(e)}")

    def _check_thresholds(self):
        """Check all monitoring thresholds and generate alerts"""
        self._check_system_thresholds()
        self._check_performance_thresholds()
        self._check_detection_thresholds()
        self._check_api_thresholds()
        return self._check_alerts()

    def _check_system_thresholds(self):
        """Check system resource thresholds"""
        cpu_usage = self.metrics['resource_usage']['cpu']
        memory_usage = self.metrics['resource_usage']['memory']
        disk_usage = self.metrics['resource_usage']['disk']
        
        # CPU checks
        if cpu_usage >= self.config.get('monitoring.thresholds.system.cpu_critical', 85):
            self.send_alert('CRITICAL', f'CPU usage critical: {cpu_usage}%')
        elif cpu_usage >= self.config.get('monitoring.thresholds.system.cpu_warning', 70):
            self.send_alert('WARNING', f'CPU usage high: {cpu_usage}%')
        
        # Memory checks
        if memory_usage >= self.config.get('monitoring.thresholds.system.memory_critical', 90):
            self.send_alert('CRITICAL', f'Memory usage critical: {memory_usage}%')
        elif memory_usage >= self.config.get('monitoring.thresholds.system.memory_warning', 75):
            self.send_alert('WARNING', f'Memory usage high: {memory_usage}%')
        
        # Disk checks
        if disk_usage >= self.config.get('monitoring.thresholds.system.disk_critical', 90):
            self.send_alert('CRITICAL', f'Disk usage critical: {disk_usage}%')
        elif disk_usage >= self.config.get('monitoring.thresholds.system.disk_warning', 80):
            self.send_alert('WARNING', f'Disk usage high: {disk_usage}%')

    def _check_performance_thresholds(self):
        """Check performance thresholds"""
        if self.metrics.get('avg_response_time'):
            resp_time = self.metrics['avg_response_time']
            if resp_time >= self.config.get('monitoring.thresholds.performance.response_time_critical', 2.0):
                self.send_alert('CRITICAL', f'Response time critical: {resp_time:.2f}s')
            elif resp_time >= self.config.get('monitoring.thresholds.performance.response_time_warning', 1.5):
                self.send_alert('WARNING', f'Response time high: {resp_time:.2f}s')

    def _check_detection_thresholds(self):
        """Check detection accuracy thresholds"""
        accuracy = self.metrics['detection_accuracy'] * 100
        if accuracy <= self.config.get('monitoring.thresholds.detection.accuracy_critical', 90):
            self.send_alert('CRITICAL', f'Detection accuracy critical: {accuracy:.1f}%')
        elif accuracy <= self.config.get('monitoring.thresholds.detection.accuracy_warning', 95):
            self.send_alert('WARNING', f'Detection accuracy low: {accuracy:.1f}%')

    def _check_api_thresholds(self):
        """Check API-related thresholds"""
        if self.metrics['api_calls'] > 0:
            error_rate = (self.metrics['failed_requests'] / self.metrics['api_calls']) * 100
            if error_rate >= self.config.get('monitoring.thresholds.api.failed_requests_critical', 10):
                self.send_alert('CRITICAL', f'API error rate critical: {error_rate:.1f}%')
            elif error_rate >= self.config.get('monitoring.thresholds.api.failed_requests_warning', 5):
                self.send_alert('WARNING', f'API error rate high: {error_rate:.1f}%')

    def send_alert(self, level: str, message: str):
        """Send an alert through configured channels"""
        now = datetime.now()
        alert_key = f"{level}:{message}"
        
        # Check cooldown
        if alert_key in self.alert_history:
            last_sent = self.alert_history[alert_key]
            cooldown = self.config.get(f'monitoring.alerts.cooldown.{level.lower()}', 300)
            if (now - last_sent).total_seconds() < cooldown:
                return
        
        # Update alert history
        self.alert_history[alert_key] = now
        
        # Log alert
        self.logger.log(
            logging.CRITICAL if level == 'CRITICAL' else logging.WARNING,
            f"Alert: {message}"
        )
        
        # Send to configured channels
        if self.config.get('monitoring.alerts.enabled', True):
            if self.config.get('monitoring.alerts.channels.slack.enabled', False):
                self._send_slack_alert(level, message)

    def _send_slack_alert(self, level: str, message: str):
        """Send alert to Slack"""
        try:
            webhook_url = self.config.get('monitoring.alerts.channels.slack.webhook_url')
            if not webhook_url:
                return
            
            color = self.config.get(f'monitoring.alerts.levels.{level.lower()}.color', '#ff0000')
            
            payload = {
                'username': self.config.get('monitoring.alerts.channels.slack.username', 'Bot Blocker Monitor'),
                'icon_emoji': self.config.get('monitoring.alerts.channels.slack.icon_emoji', ':robot_face:'),
                'channel': self.config.get('monitoring.alerts.channels.slack.channel', '#bot-blocker-alerts'),
                'attachments': [{
                    'color': color,
                    'title': f'{level} Alert',
                    'text': message,
                    'fields': [
                        {
                            'title': 'Time',
                            'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'short': True
                        },
                        {
                            'title': 'Level',
                            'value': level,
                            'short': True
                        }
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {str(e)}")

    def _export_metrics(self):
        """Export collected metrics"""
        try:
            # Create metrics directory if it doesn't exist
            metrics_dir = self.config.get('monitoring.metrics.export.directory', 'metrics')
            os.makedirs(metrics_dir, exist_ok=True)
            
            # Get batch size
            batch_size = self.config.get('monitoring.metrics.collection.batch_size', 100)
            
            # Collect metrics from queue
            metrics_batch = []
            while len(metrics_batch) < batch_size and not self.metrics_queue.empty():
                metrics_batch.append(self.metrics_queue.get_nowait())
            
            if not metrics_batch:
                return
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            format = self.config.get('monitoring.metrics.export.format', 'csv')
            filename = f"metrics_{timestamp}.{format}"
            filepath = os.path.join(metrics_dir, filename)
            
            # Export based on format
            if format == 'csv':
                self._export_csv(filepath, metrics_batch)
            else:  # default to json
                self._export_json(filepath, metrics_batch)
                
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {str(e)}")

    def _export_csv(self, filepath: str, metrics_batch: List[Dict]):
        """Export metrics to CSV"""
        if not metrics_batch:
            return
            
        # Get all unique keys from all metrics
        fieldnames = set()
        for metric in metrics_batch:
            self._get_all_keys(metric, fieldnames)
            
        # Write to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            for metric in metrics_batch:
                # Flatten the metric dictionary
                flat_metric = {}
                self._flatten_dict(metric, flat_metric)
                writer.writerow(flat_metric)

    def _export_json(self, filepath: str, metrics_batch: List[Dict]):
        """Export metrics to JSON"""
        with open(filepath, 'w') as f:
            json.dump(metrics_batch, f, indent=2)

    def _get_all_keys(self, d: Dict, keys: set, prefix: str = ''):
        """Recursively get all keys from nested dictionary"""
        for k, v in d.items():
            new_key = f"{prefix}{k}" if prefix else k
            if isinstance(v, dict):
                self._get_all_keys(v, keys, f"{new_key}_")
            else:
                keys.add(new_key)

    def _flatten_dict(self, d: Dict, flat_dict: Dict, prefix: str = ''):
        """Recursively flatten nested dictionary"""
        for k, v in d.items():
            new_key = f"{prefix}{k}" if prefix else k
            if isinstance(v, dict):
                self._flatten_dict(v, flat_dict, f"{new_key}_")
            else:
                flat_dict[new_key] = v

    def record_api_call(self, success: bool = True, response_time: float = None):
        """Record an API call"""
        self.metrics['api_calls'] += 1
        if not success:
            self.metrics['failed_requests'] += 1
        if response_time is not None:
            self.metrics['response_times'].append(response_time)
            # Keep only recent response times
            max_samples = 100
            if len(self.metrics['response_times']) > max_samples:
                self.metrics['response_times'] = self.metrics['response_times'][-max_samples:]

    def record_block(self, is_false_positive: bool = False):
        """Record a blocked account"""
        self.metrics['blocks_count'] += 1
        if is_false_positive:
            self.metrics['false_positives'] += 1
            # Update detection accuracy
            total_blocks = self.metrics['blocks_count']
            self.metrics['detection_accuracy'] = (total_blocks - self.metrics['false_positives']) / total_blocks

    def record_error(self, error: str):
        """Record an error"""
        self.metrics['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': error
        })
        # Keep only recent errors
        max_errors = 100
        if len(self.metrics['errors']) > max_errors:
            self.metrics['errors'] = self.metrics['errors'][-max_errors:]

    def get_metrics_report(self) -> Dict:
        """Generate a comprehensive metrics report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': self.metrics['system_uptime'],
            'blocks': {
                'total': self.metrics['blocks_count'],
                'false_positives': self.metrics['false_positives'],
                'accuracy': self.metrics['detection_accuracy'] * 100
            },
            'api': {
                'total_calls': self.metrics['api_calls'],
                'failed_requests': self.metrics['failed_requests'],
                'error_rate': (self.metrics['failed_requests'] / self.metrics['api_calls'] * 100) if self.metrics['api_calls'] > 0 else 0,
                'avg_response_time': sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0
            },
            'resources': self.metrics['resource_usage'],
            'errors': self.metrics['errors'][-5:]  # Last 5 errors
        }

    def _check_alerts(self) -> List[Dict]:
        """Check all monitoring thresholds and generate alerts"""
        alerts = []
        timestamp = datetime.now().isoformat()
        
        # Check CPU usage
        cpu_usage = self.metrics['resource_usage']['cpu']
        if cpu_usage >= 85:
            alerts.append({
                'level': 'critical',
                'message': f'CPU usage critical: {cpu_usage}%',
                'timestamp': timestamp
            })
        elif cpu_usage >= 70:
            alerts.append({
                'level': 'warning',
                'message': f'CPU usage high: {cpu_usage}%',
                'timestamp': timestamp
            })
        
        # Check memory usage
        memory_usage = self.metrics['resource_usage']['memory']
        if memory_usage >= 90:
            alerts.append({
                'level': 'critical',
                'message': f'Memory usage critical: {memory_usage}%',
                'timestamp': timestamp
            })
        elif memory_usage >= 75:
            alerts.append({
                'level': 'warning',
                'message': f'Memory usage high: {memory_usage}%',
                'timestamp': timestamp
            })
        
        # Check error rate
        error_rate = self.metrics.get('error_rate', 0)
        if error_rate >= 10:
            alerts.append({
                'level': 'critical',
                'message': f'Error rate critical: {error_rate}%',
                'timestamp': timestamp
            })
        elif error_rate >= 5:
            alerts.append({
                'level': 'warning',
                'message': f'Error rate high: {error_rate}%',
                'timestamp': timestamp
            })
        
        return alerts

    def check_health(self) -> Dict:
        """Check system health status"""
        timestamp = datetime.now().isoformat()
        
        # Check metrics collection
        metrics_check = {
            'name': 'metrics_collection',
            'status': 'passed',
            'message': 'Metrics are being collected'
        }
        
        # Check API health
        api_check = {
            'name': 'api_health',
            'status': 'passed',
            'message': 'API is responding normally'
        }
        
        # Check resource usage
        resource_check = {
            'name': 'resource_usage',
            'status': 'passed',
            'message': 'Resource usage is within limits'
        }
        
        # Update status based on metrics
        if self.metrics.get('error_rate', 0) > 10:
            api_check['status'] = 'failed'
            api_check['message'] = 'High error rate detected'
        
        if self.metrics['resource_usage']['cpu'] > 85 or self.metrics['resource_usage']['memory'] > 90:
            resource_check['status'] = 'failed'
            resource_check['message'] = 'Resource usage is high'
        
        return {
            'status': 'healthy' if all(c['status'] == 'passed' for c in [metrics_check, api_check, resource_check]) else 'degraded',
            'checks': [metrics_check, api_check, resource_check],
            'timestamp': timestamp
        } 
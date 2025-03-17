import pytest
import os
import json
from datetime import datetime, timedelta
from x_bot_blocker.monitoring import MonitoringSystem
from x_bot_blocker.config_manager import ConfigManager

def test_metrics_collection(config, clean_data_dirs):
    """Test that metrics are being collected correctly"""
    # Initialize monitoring system
    monitoring = MonitoringSystem(config)
    
    # Record some test data
    monitoring.record_api_call(success=True, response_time=0.5)
    monitoring.record_api_call(success=False, response_time=1.0)
    monitoring.record_block(is_false_positive=False)
    monitoring.record_block(is_false_positive=True)
    monitoring.record_error("Test error message")
    
    # Update metrics
    monitoring.update_metrics()
    
    # Verify metrics
    assert monitoring.metrics['api_calls'] == 2
    assert monitoring.metrics['failed_requests'] == 1
    assert monitoring.metrics['blocks_count'] == 2
    assert monitoring.metrics['false_positives'] == 1
    assert len(monitoring.metrics['errors']) == 1
    
    # Verify resource usage metrics
    assert monitoring.metrics['resource_usage']['cpu'] >= 0
    assert monitoring.metrics['resource_usage']['memory'] >= 0
    assert monitoring.metrics['resource_usage']['disk'] >= 0

def test_metrics_export(config, clean_data_dirs):
    """Test that metrics are being exported correctly"""
    # Initialize monitoring system
    monitoring = MonitoringSystem(config)
    
    # Force metrics export
    monitoring._export_metrics()
    
    # Check metrics directory
    metrics_dir = config.get('monitoring.metrics.export.directory', 'metrics')
    files = os.listdir(metrics_dir)
    
    # Verify export files exist
    assert len(files) > 0, "No metric files were exported"
    
    # Check most recent file
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(metrics_dir, x)))
    file_path = os.path.join(metrics_dir, latest_file)
    
    # Verify file format
    assert latest_file.endswith('.csv'), "Metrics file should be in CSV format"
    
    # Verify file content
    with open(file_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) > 1, "Metrics file should contain header and data"
        
        # Verify header contains expected fields
        header = lines[0].strip().split(',')
        expected_fields = ['timestamp', 'blocks_count', 'api_calls', 'detection_accuracy']
        for field in expected_fields:
            assert field in header, f"Missing expected field {field}"

def test_alert_generation(config, clean_data_dirs):
    """Test alert generation"""
    # Initialize monitoring system
    monitoring = MonitoringSystem(config)
    
    # Set up test data
    monitoring.metrics['resource_usage']['cpu'] = 85  # Critical CPU usage
    monitoring.metrics['error_rate'] = 20  # High error rate
    
    # Generate alerts
    alerts = monitoring._check_alerts()
    
    # Verify alerts
    assert len(alerts) == 2, "Expected 2 alerts"
    
    # Verify alert structure
    for alert in alerts:
        assert 'level' in alert
        assert 'message' in alert
        assert 'timestamp' in alert
    
    # Verify alert levels
    alert_levels = [alert['level'] for alert in alerts]
    assert 'critical' in alert_levels
    assert 'warning' in alert_levels

def test_health_check(config, clean_data_dirs):
    """Test health check functionality"""
    # Initialize monitoring system
    monitoring = MonitoringSystem(config)
    
    # Perform health check
    health_status = monitoring.check_health()
    
    # Verify health check structure
    assert 'status' in health_status
    assert 'checks' in health_status
    assert 'timestamp' in health_status
    
    # Verify individual checks
    checks = health_status['checks']
    assert 'api_health' in checks
    assert 'resource_usage' in checks
    assert 'error_rate' in checks
    
    # Verify check structure
    for check in checks.values():
        assert 'status' in check
        assert 'message' in check 
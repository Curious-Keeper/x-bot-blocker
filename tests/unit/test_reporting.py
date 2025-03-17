import pytest
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from x_bot_blocker.config_manager import ConfigManager
from x_bot_blocker.reporting import ReportingSystem

def test_weekly_report_generation(config, metrics_data, clean_data_dirs):
    """Test weekly report generation"""
    # Initialize reporting system
    reporting = ReportingSystem(config)
    
    # Generate report
    report = reporting.generate_weekly_report()
    
    # Verify report structure
    assert 'period' in report
    assert 'summary' in report
    assert 'trends' in report
    assert 'resource_usage' in report
    assert 'top_issues' in report
    
    # Verify summary metrics
    summary = report['summary']
    assert int(summary['total_blocks']) == 700  # 100 blocks per day * 7 days
    assert int(summary['false_positives']) == 35  # 5 false positives per day * 7 days
    assert float(summary['detection_accuracy']) > 0.9
    assert int(summary['total_api_calls']) == 7000  # 1000 calls per day * 7 days
    assert float(summary['error_rate']) > 0
    assert float(summary['avg_response_time']) > 0

def test_monthly_report_generation(config, metrics_data, clean_data_dirs):
    """Test monthly report generation"""
    # Initialize reporting system
    reporting = ReportingSystem(config)
    
    # Generate report
    report = reporting.generate_monthly_report()
    
    # Verify report structure
    assert 'period' in report
    assert 'summary' in report
    assert 'trends' in report
    assert 'resource_usage' in report
    assert 'top_issues' in report
    assert 'monthly_comparison' in report
    
    # Verify summary metrics
    summary = report['summary']
    assert int(summary['total_blocks']) == 3000  # 100 blocks per day * 30 days
    assert int(summary['false_positives']) == 150  # 5 false positives per day * 30 days
    assert float(summary['detection_accuracy']) > 0.9
    assert int(summary['total_api_calls']) == 30000  # 1000 calls per day * 30 days
    assert float(summary['error_rate']) > 0
    assert float(summary['avg_response_time']) > 0

def test_trend_calculation(config, metrics_data, clean_data_dirs):
    """Test trend calculation"""
    # Initialize reporting system
    reporting = ReportingSystem(config)
    
    # Load test data
    df = reporting._load_metrics_data(days=30)
    
    # Calculate trend for blocks
    trend = reporting._calculate_trend(df, 'blocks_count')
    
    # Verify trend structure
    assert 'direction' in trend
    assert 'change' in trend
    assert 'significance' in trend
    
    # Since our test data is constant, trend should be stable
    assert trend['direction'] == 'stable'
    assert float(trend['change']) == 0
    assert trend['significance'] == 'low'

def test_error_analysis(config, metrics_data, clean_data_dirs):
    """Test error analysis"""
    # Initialize reporting system
    reporting = ReportingSystem(config)
    
    # Load test data
    df = reporting._load_metrics_data(days=30)
    
    # Analyze errors
    errors = reporting._analyze_errors(df)
    
    # Verify error analysis
    assert len(errors) == 2  # We created 2 types of test errors
    assert int(errors[0]['count']) == 30  # Each error occurs once per day for 30 days
    
    # Verify error structure
    for error in errors:
        assert 'error' in error
        assert 'count' in error

def test_monthly_comparison(config, metrics_data, clean_data_dirs):
    """Test monthly comparison"""
    # Initialize reporting system
    reporting = ReportingSystem(config)
    
    # Load test data
    df = reporting._load_metrics_data(days=60)
    
    # Compare months
    comparison = reporting._compare_with_previous_month(df)
    
    # Verify comparison structure
    assert 'current_month' in comparison
    assert 'previous_month' in comparison
    assert 'changes' in comparison
    
    # Since our test data is constant, changes should be 0
    for change in comparison['changes'].values():
        assert float(change) == 0

def test_report_saving_and_loading(config, metrics_data, clean_data_dirs):
    """Test report saving and loading"""
    # Initialize reporting system
    reporting = ReportingSystem(config)
    
    # Generate a test report
    report = reporting.generate_weekly_report()
    
    # Get the latest report
    loaded_report = reporting.get_latest_report('weekly')
    
    # Verify report was saved and loaded correctly
    assert loaded_report is not None
    assert int(report['summary']['total_blocks']) == int(loaded_report['summary']['total_blocks'])
    assert int(report['summary']['false_positives']) == int(loaded_report['summary']['false_positives'])

if __name__ == '__main__':
    pytest.main(verbosity=2) 
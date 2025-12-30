# backend/tests/test_ec2_analyzer.py
import pytest
from analyzers.ec2_analyzer import EC2Analyzer

def test_ec2_analyzer_initialization():
    """Test that analyzer initializes correctly"""
    analyzer = EC2Analyzer('test_key', 'test_secret')
    assert analyzer.region == 'us-east-1'
    assert analyzer.instance_prices['t2.micro'] == 0.0116

def test_downsize_mapping():
    """Test instance downsize recommendations"""
    analyzer = EC2Analyzer('test_key', 'test_secret')
    
    assert analyzer._get_downsized_type('m5.xlarge') == 'm5.large'
    assert analyzer._get_downsized_type('t3.medium') == 't3.small'

# Note: Full integration tests require real AWS credentials
# For now, test with mock data
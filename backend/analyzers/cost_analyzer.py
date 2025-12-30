# backend/analyzers/cost_analyzer.py
from datetime import datetime
from .ec2_analyzer import EC2Analyzer
from .storage_analyzer import StorageAnalyzer
from typing import Dict

class ComprehensiveCostAnalyzer:
    def __init__(self, aws_access_key: str, aws_secret_key: str, region: str = 'us-east-1'):
        self.ec2 = EC2Analyzer(aws_access_key, aws_secret_key, region)
        self.storage = StorageAnalyzer(aws_access_key, aws_secret_key, region)
        self.region = region
    
    def analyze_all(self) -> Dict:
        """Run complete cost analysis"""
        return {
            'ec2': self.ec2.get_underutilized_instances(),
            'storage': self.storage.analyze_s3_buckets(),
            'cost_summary': self.ec2.get_cost_summary(),
            'total_potential_savings': self._calculate_total_savings(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_total_savings(self) -> float:
        """Calculate total potential annual savings"""
        ec2_savings = sum([
            item['potential_savings'] 
            for item in self.ec2.get_underutilized_instances()
        ])
        
        storage_savings = sum([
            item['potential_savings']
            for item in self.storage.analyze_s3_buckets()
        ])
        
        return ec2_savings + storage_savings
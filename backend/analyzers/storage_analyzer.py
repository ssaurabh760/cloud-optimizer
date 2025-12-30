# backend/analyzers/storage_analyzer.py
import boto3
from datetime import datetime, timedelta

class StorageAnalyzer:
    def __init__(self, aws_access_key: str, aws_secret_key: str, region: str = 'us-east-1'):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.cloudwatch = boto3.client(
            'cloudwatch',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    
    def analyze_s3_buckets(self) -> list:
        """Find expensive S3 buckets and optimization opportunities"""
        buckets = self.s3.list_buckets()['Buckets']
        recommendations = []
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            
            # Get bucket size
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'StorageType', 'Value': 'StandardStorage'}
                    ],
                    StartTime=datetime.now() - timedelta(days=1),
                    EndTime=datetime.now(),
                    Period=86400,
                    Statistics=['Average']
                )
                
                if response['Datapoints']:
                    size_bytes = response['Datapoints'][0]['Average']
                    size_gb = size_bytes / (1024**3)
                    monthly_cost = (size_gb / 1024) * 23  # $23 per TB/month
                    
                    # Check for old objects
                    old_objects = self._find_old_objects(bucket_name)
                    
                    if old_objects['count'] > 0:
                        recommendations.append({
                            'bucket': bucket_name,
                            'size_gb': round(size_gb, 2),
                            'monthly_cost': round(monthly_cost, 2),
                            'issue': f'{old_objects["count"]} objects older than 90 days',
                            'recommendation': 'Move to Glacier or delete old objects',
                            'potential_savings': old_objects['estimated_savings']
                        })
            except Exception as e:
                print(f"Error analyzing bucket {bucket_name}: {str(e)}")
        
        return recommendations
    
    def _find_old_objects(self, bucket_name: str) -> dict:
        """Find objects older than 90 days"""
        try:
            paginator = self.s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name)
            
            now = datetime.now(pages.__next__()['Contents'][0]['LastModified'].tzinfo)
            ninety_days_ago = now - timedelta(days=90)
            
            old_count = 0
            old_size = 0
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    if obj['LastModified'] < ninety_days_ago:
                        old_count += 1
                        old_size += obj['Size']
            
            # Glacier costs ~$4 per TB/month
            glacier_cost = (old_size / (1024**3) / 1024) * 4
            standard_cost = (old_size / (1024**3) / 1024) * 23
            savings = standard_cost - glacier_cost
            
            return {
                'count': old_count,
                'size_bytes': old_size,
                'estimated_savings': savings * 12  # Annual
            }
        except Exception as e:
            return {'count': 0, 'size_bytes': 0, 'estimated_savings': 0}
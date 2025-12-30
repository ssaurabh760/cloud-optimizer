# backend/analyzers/ec2_analyzer.py
import boto3
from datetime import datetime, timedelta
from typing import List, Dict

class EC2Analyzer:
    def __init__(self, aws_access_key: str, aws_secret_key: str, region: str = 'us-east-1'):
        self.ec2 = boto3.client(
            'ec2',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.cloudwatch = boto3.client(
            'cloudwatch',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.region = region
        
        # Pricing reference (update quarterly)
        self.instance_prices = {
            't2.micro': 0.0116,
            't2.small': 0.023,
            't2.medium': 0.0464,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            # Add more as needed
        }
    
    def get_underutilized_instances(self, cpu_threshold: int = 10) -> List[Dict]:
        """
        Find EC2 instances with low CPU usage
        
        Returns instances with:
        - Average CPU < threshold% over last 7 days
        - Specific recommendations for cost savings
        """
        try:
            instances = self.ec2.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
        except Exception as e:
            return {'error': f'Failed to get instances: {str(e)}'}
        
        underutilized = []
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                
                # Get CPU metrics
                try:
                    metrics = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=seven_days_ago,
                        EndTime=now,
                        Period=3600,  # Hourly
                        Statistics=['Average']
                    )
                    
                    if not metrics['Datapoints']:
                        continue
                    
                    # Calculate average CPU
                    datapoints = metrics['Datapoints']
                    avg_cpu = sum([d['Average'] for d in datapoints]) / len(datapoints)
                    
                    if avg_cpu < cpu_threshold:
                        # Calculate cost
                        hourly_cost = self.instance_prices.get(instance_type, 0.1)
                        monthly_cost = hourly_cost * 730  # 730 hours in month
                        annual_cost = monthly_cost * 12
                        
                        # Generate recommendations
                        recommendations = self._generate_recommendations(instance_type, avg_cpu)
                        
                        underutilized.append({
                            'instance_id': instance_id,
                            'instance_type': instance_type,
                            'avg_cpu_7d': round(avg_cpu, 2),
                            'monthly_cost': round(monthly_cost, 2),
                            'annual_cost': round(annual_cost, 2),
                            'recommendation': recommendations['recommendation'],
                            'potential_savings': recommendations['savings'],
                            'launch_time': instance['LaunchTime'].isoformat(),
                            'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                        })
                
                except Exception as e:
                    print(f"Error analyzing instance {instance_id}: {str(e)}")
                    continue
        
        return sorted(underutilized, key=lambda x: x['annual_cost'], reverse=True)
    
    def _generate_recommendations(self, instance_type: str, avg_cpu: float) -> Dict:
        """Generate specific recommendations based on usage"""
        current_cost = self.instance_prices.get(instance_type, 0.1)
        
        if avg_cpu < 5:
            # Recommendation: Terminate
            return {
                'recommendation': 'Terminate instance',
                'reasoning': 'Instance is essentially idle (<5% CPU)',
                'savings': current_cost * 730 * 12  # Annual savings
            }
        elif avg_cpu < 15:
            # Recommendation: Downsize
            downsized_type = self._get_downsized_type(instance_type)
            if downsized_type:
                downsize_cost = self.instance_prices.get(downsized_type, current_cost * 0.5)
                savings = (current_cost - downsize_cost) * 730 * 12
                return {
                    'recommendation': f'Downsize to {downsized_type}',
                    'reasoning': f'Current usage ({avg_cpu:.1f}% CPU) can be handled by smaller instance',
                    'savings': savings
                }
        
        return {
            'recommendation': 'Monitor',
            'reasoning': 'Instance usage is normal',
            'savings': 0
        }
    
    def _get_downsized_type(self, current_type: str) -> str:
        """Get next smaller instance type"""
        downsizing_map = {
            'm5.xlarge': 'm5.large',
            'm5.large': 'm5.large',
            't3.medium': 't3.small',
            't3.small': 't3.micro',
            't2.large': 't2.medium',
            't2.medium': 't2.small',
        }
        return downsizing_map.get(current_type)
    
    def get_cost_summary(self) -> Dict:
        """Get cost breakdown by service"""
        ce = boto3.client('ce', region_name=self.region)
        
        try:
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            costs_by_service = {}
            for item in response['ResultsByTime'][0]['Groups']:
                service = item['Keys'][0]
                cost = float(item['Metrics']['UnblendedCost']['Amount'])
                costs_by_service[service] = cost
            
            return {
                'total_30day_cost': sum(costs_by_service.values()),
                'costs_by_service': costs_by_service,
                'period_days': 30
            }
        except Exception as e:
            return {'error': str(e)}
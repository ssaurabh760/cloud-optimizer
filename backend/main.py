# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from analyzers.cost_analyzer import ComprehensiveCostAnalyzer
import json

app = FastAPI(title="CloudOptimizer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AnalysisRequest(BaseModel):
    aws_access_key: str
    aws_secret_key: str
    aws_region: str = 'us-east-1'

class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    total_potential_savings: float
    ec2_recommendations: list
    storage_recommendations: list
    cost_summary: dict

# In-memory storage (replace with database)
analyses = {}

@app.post("/api/analyze")
async def analyze_aws_account(request: AnalysisRequest):
    """
    Analyze AWS account for cost optimization opportunities
    
    Request:
        {
            "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
            "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "aws_region": "us-east-1"
        }
    """
    try:
        analyzer = ComprehensiveCostAnalyzer(
            request.aws_access_key,
            request.aws_secret_key,
            request.aws_region
        )
        
        result = analyzer.analyze_all()
        
        # Store analysis
        analysis_id = f"analysis_{int(datetime.now().timestamp())}"
        analyses[analysis_id] = result
        
        return {
            'analysis_id': analysis_id,
            'timestamp': result['timestamp'],
            'total_potential_savings': result['total_potential_savings'],
            'ec2_recommendations': result['ec2'],
            'storage_recommendations': result['storage'],
            'cost_summary': result['cost_summary']
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve previous analysis"""
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analyses[analysis_id]

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}

@app.post("/api/implement/{analysis_id}/{recommendation_id}")
async def implement_recommendation(analysis_id: str, recommendation_id: str):
    """
    Mark recommendation as implemented
    (In real app: actually implement the change)
    """
    return {
        'status': 'success',
        'message': f'Recommendation {recommendation_id} marked as implemented',
        'savings': 'To be calculated'
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
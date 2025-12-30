# backend/database.py
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://user:password@localhost/cloudoptimizer"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_potential_savings = Column(Float)
    ec2_recommendations = Column(JSON)
    storage_recommendations = Column(JSON)
    cost_summary = Column(JSON)

# Add to main.py
from database import SessionLocal, Analysis

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/analyze")
async def analyze_aws_account(request: AnalysisRequest, db = Depends(get_db)):
    # ... existing code ...
    
    # Save to database
    analysis_record = Analysis(
        id=analysis_id,
        user_id="user_123",  # Get from auth
        timestamp=datetime.now(),
        total_potential_savings=result['total_potential_savings'],
        ec2_recommendations=result['ec2'],
        storage_recommendations=result['storage'],
        cost_summary=result['cost_summary']
    )
    db.add(analysis_record)
    db.commit()
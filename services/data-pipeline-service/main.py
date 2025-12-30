"""Data Pipeline Service - Handles data collection, chunking, and vector DB ingestion"""
import sys
import os
from pathlib import Path
from typing import Optional
import uuid

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from shared.common import setup_logger, get_config, HealthResponse, PipelineJobRequest, PipelineJobResponse
from shared.common.config import DataPipelineConfig
from shared.common.redis_client import RedisClient
from shared.common.db_client import get_db_client
from shared.common.metrics import get_metrics, http_requests_total, http_request_duration_seconds
from pipeline import DataPipeline
import os
import time

# Setup logger
logger = setup_logger(__name__)

# Get configuration
config: DataPipelineConfig = get_config("data-pipeline")
logger.info(f"Starting Data Pipeline Service")

# Initialize FastAPI app
app = FastAPI(
    title="Data Pipeline Service",
    description="Data collection, chunking, and vector DB ingestion service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = None
redis_client = RedisClient(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
db_client = get_db_client()


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track metrics"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    global pipeline
    try:
        logger.info("Initializing data pipeline...")
        pipeline = DataPipeline(config)
        await pipeline.initialize()
        logger.info("Data pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize data pipeline: {e}", exc_info=True)
        # Don't raise - allow service to start even if pipeline init fails
        # Pipeline will be initialized on first /ingest call
        logger.warning("Service will start but pipeline initialization will be deferred")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if pipeline is None:
        return HealthResponse(
            status="initializing",
            service="data-pipeline-service",
            version="1.0.0"
        )
    return HealthResponse(
        status="healthy",
        service="data-pipeline-service",
        version="1.0.0"
    )


async def run_pipeline_job(job_id: str, sources: Optional[list] = None, force_refresh: bool = False):
    """Background task to run pipeline job"""
    try:
        # Update job status in database
        db_client.update_pipeline_job(job_id, "running", "Starting pipeline...")
        logger.info(f"Starting pipeline job {job_id}")
        
        result = await pipeline.run(sources=sources, force_refresh=force_refresh)
        
        # Update job status in database
        db_client.update_pipeline_job(
            job_id,
            "completed",
            f"Pipeline completed successfully. Processed {result.get('documents', 0)} documents.",
            result=result
        )
        logger.info(f"Pipeline job {job_id} completed successfully")
    except Exception as e:
        logger.error(f"Pipeline job {job_id} failed: {e}", exc_info=True)
        db_client.update_pipeline_job(job_id, "failed", str(e), error=str(e))


@app.post("/ingest", response_model=PipelineJobResponse)
async def ingest_data(
    request: PipelineJobRequest = Body(default={}),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Trigger data ingestion pipeline.
    
    Can be called with:
    - Empty JSON body: curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{}'
    - With options: curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{"force_refresh": true}'
    
    Args:
        request: Pipeline job request (optional, defaults to all sources, no refresh)
        background_tasks: FastAPI background tasks
        
    Returns:
        Pipeline job response with job ID
    """
    
    global pipeline
    if pipeline is None:
        # Try to initialize pipeline if not already initialized
        try:
            logger.info("Pipeline not initialized, initializing now...")
            pipeline = DataPipeline(config)
            await pipeline.initialize()
            logger.info("Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"Pipeline initialization failed: {str(e)}")
    
    try:
        job_id = str(uuid.uuid4())
        
        # Create job record in database
        db_client.create_pipeline_job(job_id, "queued", "Job queued")
        
        # Add job to Redis queue
        redis_client.enqueue("pipeline_jobs", {
            "job_id": job_id,
            "sources": request.sources,
            "force_refresh": request.force_refresh
        })
        
        # Start background job
        background_tasks.add_task(
            run_pipeline_job,
            job_id,
            request.sources,
            request.force_refresh
        )
        
        return PipelineJobResponse(
            job_id=job_id,
            status="queued",
            message="Pipeline job queued successfully"
        )
    except Exception as e:
        logger.error(f"Error queuing pipeline job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a pipeline job"""
    job = db_client.get_pipeline_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")


@app.post("/schedule")
async def schedule_pipeline(cron_expression: str):
    """
    Schedule periodic pipeline runs (placeholder - implement with Celery in production).
    
    Args:
        cron_expression: Cron expression for scheduling
    """
    # TODO: Implement with Celery or similar
    return {"message": "Scheduling not yet implemented. Use Celery for production."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)


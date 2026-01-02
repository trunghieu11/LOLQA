"""Data Pipeline Service - Handles data collection, chunking, and vector DB ingestion"""
import os
import sys
import time
import uuid
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi import Request
from shared.common import (
    setup_logger,
    get_config,
    HealthResponse,
    PipelineJobRequest,
    PipelineJobResponse
)
from shared.common.config import DataPipelineConfig
from shared.common.redis_client import RedisClient
from shared.common.db_client import get_db_client
from shared.common.metrics import (
    get_metrics,
    http_requests_total,
    http_request_duration_seconds
)
from pipeline import DataPipeline

# Setup logger
logger = setup_logger(__name__)

# Get configuration
config: DataPipelineConfig = get_config("data-pipeline")
logger.info("Starting Data Pipeline Service")

# Constants
SERVICE_NAME = "data-pipeline-service"
SERVICE_VERSION = "1.0.0"

# Initialize pipeline
pipeline = None
redis_client = RedisClient(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
db_client = get_db_client()


async def initialize_pipeline(raise_on_error: bool = False) -> bool:
    """
    Initialize data pipeline.
    
    Args:
        raise_on_error: If True, raise exception on failure. If False, log and continue.
    
    Returns:
        True if successful, False otherwise
    """
    global pipeline
    try:
        logger.info("Initializing data pipeline...")
        pipeline = DataPipeline(config)
        await pipeline.initialize()
        logger.info("Data pipeline initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize data pipeline: {e}", exc_info=True)
        if raise_on_error:
            raise HTTPException(
                status_code=503,
                detail=f"Pipeline initialization failed: {str(e)}"
            )
        logger.warning("Service will start but pipeline initialization will be deferred")
        return False


def check_pipeline_initialized() -> None:
    """Check if pipeline is initialized, raise if not"""
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    await initialize_pipeline(raise_on_error=False)
    
    # Start worker process as background task
    worker_task = asyncio.create_task(worker_process())
    logger.info("Pipeline worker process started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down worker process...")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        logger.info("Worker process cancelled")
    
    if pipeline is not None:
        logger.info("Shutting down data pipeline...")


# Initialize FastAPI app
app = FastAPI(
    title="Data Pipeline Service",
    description="Data collection, chunking, and vector DB ingestion service",
    version=SERVICE_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="initializing" if pipeline is None else "healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION
    )


async def run_pipeline_job(
    job_id: str,
    sources: Optional[list] = None,
    force_refresh: bool = False
):
    """
    Run pipeline job.
    
    Args:
        job_id: Job ID
        sources: Optional list of source names
        force_refresh: Force refresh flag
    """
    global pipeline
    
    # Ensure pipeline is initialized
    if pipeline is None:
        await initialize_pipeline(raise_on_error=True)
    
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
        db_client.update_pipeline_job(
            job_id,
            "failed",
            str(e),
            error=str(e)
        )


async def worker_process():
    """
    Worker process that consumes jobs from Redis queue.
    Runs continuously, polling for new jobs.
    """
    logger.info("Starting pipeline worker process...")
    
    while True:
        try:
            # Dequeue job from Redis (blocking, waits up to 5 seconds)
            job = redis_client.dequeue("pipeline_jobs", timeout=5)
            
            if job:
                logger.info(f"Worker picked up job: {job.get('job_id')}")
                
                # Process the job
                await run_pipeline_job(
                    job_id=job.get("job_id"),
                    sources=job.get("sources"),
                    force_refresh=job.get("force_refresh", False)
                )
            else:
                # No job available, continue polling
                await asyncio.sleep(1)  # Small delay to avoid busy waiting
                
        except Exception as e:
            logger.error(f"Error in worker process: {e}", exc_info=True)
            # Wait a bit before retrying to avoid tight error loop
            await asyncio.sleep(5)


@app.post("/ingest", response_model=PipelineJobResponse)
async def ingest_data(
    request: PipelineJobRequest = Body(default={})
):
    """
    Trigger data ingestion pipeline.
    
    Jobs are added to Redis queue and processed by background worker.
    
    Can be called with:
    - Empty JSON body: curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{}'
    - With options: curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{"force_refresh": true}'
    
    Args:
        request: Pipeline job request (optional, defaults to all sources, no refresh)
        
    Returns:
        Pipeline job response with job ID
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Create job record in database
        db_client.create_pipeline_job(job_id, "queued", "Job queued")
        
        # Add job to Redis queue (worker will process it)
        success = redis_client.enqueue("pipeline_jobs", {
            "job_id": job_id,
            "sources": request.sources,
            "force_refresh": request.force_refresh or False
        })
        
        if not success:
            # If Redis enqueue fails, mark job as failed
            db_client.update_pipeline_job(
                job_id,
                "failed",
                "Failed to enqueue job to Redis",
                error="Redis enqueue failed"
            )
            raise HTTPException(
                status_code=503,
                detail="Failed to queue job. Redis may be unavailable."
            )
        
        logger.info(f"Job {job_id} queued successfully in Redis")
        
        return PipelineJobResponse(
            job_id=job_id,
            status="queued",
            message="Pipeline job queued successfully"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
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
from fastapi import FastAPI
from app.api.routes import router
from app.core.logger import logger

app = FastAPI(
    title="Local RAG System",
    version="1.0"
)

app.include_router(router)


@app.get("/")
def health_check():

    logger.info("Health check endpoint called")
    
    return {
        "status": "running"
    }
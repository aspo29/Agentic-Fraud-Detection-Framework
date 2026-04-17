from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import logging
import structlog

from app.config.settings import settings
from app.api.routes import router
from app.services.kafka_service import KafkaService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    logger.info("Shutting down application")
    KafkaService.close()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for transaction fraud detection using agentic framework",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Add routes
app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Agentic Fraud Detection REST API",
        routes=app.routes,
    )
    
    # Add custom security scheme documentation
    openapi_schema["components"]["securitySchemes"] = {
        "api_key": {
            "type": "apiKey",
            "in": "header",
            "name": settings.API_KEY_HEADER,
            "description": "API key for authentication"
        }
    }
    
    # Add security to all endpoints
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if isinstance(operation, dict) and "tags" in operation:
                if "health" not in operation.get("tags", []):
                    operation["security"] = [{"api_key": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"API running on {settings.HOST}:{settings.PORT}")
    logger.info(f"Swagger UI available at http://{settings.HOST}:{settings.PORT}/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

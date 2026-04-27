from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Callable
from app.config.settings import settings


api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


class APIKeyMiddleware:
    """Middleware for API key authentication."""
    
    @staticmethod
    async def verify_api_key(api_key_header_value: str = None) -> str:
        """Verify API key from request header.
        
        Args:
            api_key_header_value: API key from request header
            
        Returns:
            str: API key if valid
            
        Raises:
            HTTPException: 401 if API key is missing or invalid
        """
        if api_key_header_value is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key header is missing",
                headers={settings.API_KEY_HEADER: ""},
            )
        
        if api_key_header_value != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={settings.API_KEY_HEADER: ""},
            )
        
        return api_key_header_value

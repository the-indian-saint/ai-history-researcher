#!/usr/bin/env python
"""
Minimal test server to verify the setup works.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set minimal environment variables
os.environ.update({
    "ENVIRONMENT": "development",
    "DATABASE_URL": "sqlite+aiosqlite:///./test.db",
    "REDIS_URL": "",  # Empty to use fallback
    "LOG_LEVEL": "DEBUG",
})

print("Starting minimal test server...")

try:
    from fastapi import FastAPI
    import uvicorn
    
    # Create a minimal FastAPI app
    app = FastAPI(title="Test Server")
    
    @app.get("/")
    async def root():
        return {"message": "Test server is running!"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "test"}
    
    # Test if we can import our modules
    try:
        from src.ai_research_framework.config import settings
        print(f"[OK] Config loaded: {settings.environment}")
        
        @app.get("/config")
        async def config():
            return {
                "environment": settings.environment,
                "database_url": settings.database_url[:20] + "...",
                "debug": settings.debug
            }
    except ImportError as e:
        print(f"[WARNING] Could not import config: {e}")
    
    # Try to import main app routes
    try:
        from src.ai_research_framework.api.routes import health, research
        app.include_router(health.router, prefix="/api/health", tags=["health"])
        app.include_router(research.router, prefix="/api/v1/research", tags=["research"])
        print("[OK] Routes imported successfully")
    except ImportError as e:
        print(f"[WARNING] Could not import routes: {e}")
    
    print("\nStarting server on http://127.0.0.1:8000")
    print("Press Ctrl+C to stop\n")
    
    # Run server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    print("\nInstall with: uv add fastapi uvicorn")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

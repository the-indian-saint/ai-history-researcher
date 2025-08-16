#!/usr/bin/env python
"""
Local development server with proper initialization.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables for local development
os.environ.update({
    "ENVIRONMENT": "development",
    "DEBUG": "true",
    "HOST": "127.0.0.1",
    "PORT": "8000",
    
    # Database - using SQLite for local testing
    "DATABASE_URL": "sqlite+aiosqlite:///./local_dev.db",
    
    # Redis - optional for local testing (will use in-memory fallback)
    "REDIS_URL": "",  # Empty to trigger fallback
    
    # ChromaDB - local directory mode
    "CHROMADB_HOST": "localhost",
    "CHROMADB_PORT": "8001",
    
    # AI Services (will use fallback if not set)
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    
    # Paths
    "STORAGE_PATH": "./data",
    "BACKUP_PATH": "./backups",
    "TEMP_PATH": "./temp",
    
    # Logging
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "text",
})

async def initialize_app():
    """Initialize the application components."""
    print("Initializing application components...")
    
    # Import modules
    from src.ai_research_framework.storage.database import init_database
    from src.ai_research_framework.storage.cache import init_cache
    from src.ai_research_framework.config import settings
    
    # Initialize database
    print(f"  Initializing database: {settings.database_url}")
    await init_database()
    print("  [OK] Database initialized")
    
    # Initialize cache (will use in-memory fallback)
    print("  Initializing cache...")
    await init_cache()
    print("  [OK] Cache initialized")
    
    # Initialize vector storage (optional for local testing)
    try:
        from src.ai_research_framework.storage.vector_storage import init_vector_storage
        print("  Initializing vector storage...")
        await init_vector_storage()
        print("  [OK] Vector storage initialized")
    except Exception as e:
        print(f"  [INFO] Vector storage not available (optional): {e}")
    
    print("\nInitialization complete!")
    return True

async def run_server():
    """Run the FastAPI server."""
    import uvicorn
    from src.ai_research_framework.api.main import app
    
    config = uvicorn.Config(
        app,
        host=os.environ["HOST"],
        port=int(os.environ["PORT"]),
        reload=True,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Main entry point."""
    print("=" * 60)
    print("AI Research Framework - Local Development Server")
    print("=" * 60)
    print(f"Environment: {os.environ['ENVIRONMENT']}")
    print(f"Database: {os.environ['DATABASE_URL']}")
    print(f"Server: http://{os.environ['HOST']}:{os.environ['PORT']}")
    print("=" * 60)
    
    try:
        # Initialize components
        success = await initialize_app()
        if not success:
            print("Failed to initialize application")
            sys.exit(1)
        
        print("\nStarting server...")
        print("Press Ctrl+C to stop\n")
        
        # Run server
        await run_server()
        
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except ImportError as e:
        print(f"\nError: Missing dependency - {e}")
        print("Install with: uv add <package_name>")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python
"""
Local development server for testing without Docker.
This script sets up environment variables and runs the app locally.
"""

import os
import sys
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
    "DATABASE_URL": "sqlite+aiosqlite:///./local_test.db",
    
    # Redis - optional for local testing (will use in-memory fallback)
    "REDIS_URL": "",  # Empty to trigger fallback
    
    # ChromaDB - local persistent directory
    "CHROMADB_HOST": "localhost",
    "CHROMADB_PORT": "8001",
    
    # AI Services (use your actual keys or mock for testing)
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    
    # Paths
    "STORAGE_PATH": "./data",
    "BACKUP_PATH": "./backups",
    "TEMP_PATH": "./temp",
    
    # Logging
    "LOG_LEVEL": "DEBUG",
    "LOG_FORMAT": "text",
})

def main():
    """Run the application locally."""
    print("Starting local development server...")
    print(f"Project root: {project_root}")
    print(f"Database: {os.environ['DATABASE_URL']}")
    print(f"Environment: {os.environ['ENVIRONMENT']}")
    print("-" * 50)
    
    try:
        # Import and run the application
        import uvicorn
        from src.ai_research_framework.api.main import app
        
        # Run the server
        uvicorn.run(
            app,
            host=os.environ["HOST"],
            port=int(os.environ["PORT"]),
            reload=True,  # Enable auto-reload for development
            log_level="debug"
        )
        
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("\nPlease install required packages:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

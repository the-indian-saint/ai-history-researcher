#!/usr/bin/env python3
"""
Database Initialization Script for AI Research Framework

This script initializes the database with the required tables and schema.
Run this script before starting the application for the first time.

Usage:
    python init_db.py [--reset] [--sample-data]
    
Options:
    --reset       Drop existing tables and recreate them
    --sample-data Insert sample data for testing
    --help        Show this help message
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_research_framework.config import Settings
from ai_research_framework.storage.database import init_database, get_database
from sqlalchemy import text
from ai_research_framework.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


async def create_sample_data():
    """Create sample data for testing purposes."""
    logger.info("Inserting sample data...")
    
    async with get_database() as db:
        # Sample research documents
        sample_documents = [
            {
                "title": "The Maurya Empire: Administrative System",
                "content": """The Maurya Empire (c. 321-185 BCE) was one of the largest empires in ancient India. 
                Founded by Chandragupta Maurya, it had a sophisticated administrative system with a centralized government. 
                The empire was divided into provinces, each governed by a prince or a high official appointed by the emperor.""",
                "source_url": "https://example.com/maurya-admin",
                "source_type": "academic",
                "author": "Dr. Ancient History",
                "publication_date": "2023-01-15",
                "credibility_score": 0.9,
                "bias_score": 0.1,
                "metadata": '{"peer_reviewed": true, "journal": "Journal of Ancient Indian History"}',
            },
            {
                "title": "Ashoka's Edicts and Buddhist Philosophy",
                "content": """Emperor Ashoka's rock and pillar edicts provide valuable insights into his governance 
                and the spread of Buddhism. After the Kalinga War, Ashoka embraced Buddhism and promoted 
                non-violence (ahimsa) throughout his empire. His edicts were written in local languages 
                including Prakrit, Greek, and Aramaic.""",
                "source_url": "https://example.com/ashoka-edicts",
                "source_type": "primary",
                "author": "Emperor Ashoka",
                "publication_date": "250-01-01",
                "credibility_score": 0.95,
                "bias_score": 0.05,
                "metadata": '{"type": "primary_source", "language": "prakrit"}',
            },
            {
                "title": "Gupta Empire: Golden Age of India",
                "content": """The Gupta Empire (c. 320-550 CE) is often referred to as the Golden Age of India. 
                Under rulers like Chandragupta II and Samudragupta, the empire saw significant developments 
                in science, mathematics, astronomy, religion, and philosophy. The decimal system and 
                the concept of zero were developed during this period.""",
                "source_url": "https://example.com/gupta-golden-age",
                "source_type": "academic",
                "author": "Prof. Indian Studies",
                "publication_date": "2022-08-20",
                "credibility_score": 0.88,
                "bias_score": 0.12,
                "metadata": '{"peer_reviewed": true, "university": "Delhi University"}',
            },
        ]
        
        # Insert sample documents
        for doc in sample_documents:
            query = """
            INSERT INTO research_documents 
            (title, content, source_url, source_type, author, publication_date, 
             credibility_score, bias_score, metadata, created_at, updated_at)
            VALUES (:title, :content, :source_url, :source_type, :author, 
                    :publication_date, :credibility_score, :bias_score, :metadata, 
                    :created_at, :updated_at)
            """
            values = {**doc, "created_at": datetime.now(), "updated_at": datetime.now()}
            await db.execute(query, values)
        
        # Sample analysis results
        sample_analyses = [
            {
                "document_id": 1,
                "analysis_type": "credibility",
                "result": '{"score": 0.9, "factors": ["peer_reviewed", "academic_source", "recent_publication"]}',
                "confidence": 0.95,
            },
            {
                "document_id": 2,
                "analysis_type": "bias",
                "result": '{"score": 0.05, "types": ["minimal_bias"], "reasoning": "Primary source with historical context"}',
                "confidence": 0.98,
            },
            {
                "document_id": 3,
                "analysis_type": "entity_extraction",
                "result": '{"people": ["Chandragupta II", "Samudragupta"], "places": ["India"], "concepts": ["Golden Age", "decimal system", "zero"]}',
                "confidence": 0.92,
            },
        ]
        
        # Insert sample analyses
        for analysis in sample_analyses:
            query = """
            INSERT INTO analysis_results 
            (document_id, analysis_type, result, confidence, created_at)
            VALUES (:document_id, :analysis_type, :result, :confidence, :created_at)
            """
            values = {**analysis, "created_at": datetime.now()}
            await db.execute(query, values)
        
        # Sample processing jobs
        sample_jobs = [
            {
                "job_type": "document_processing",
                "status": "completed",
                "input_data": '{"file_path": "/data/maurya_empire.pdf", "format": "pdf"}',
                "result": '{"pages_processed": 25, "text_extracted": true, "ocr_confidence": 0.95}',
                "progress": 100,
            },
            {
                "job_type": "web_scraping",
                "status": "completed", 
                "input_data": '{"urls": ["https://example.com/ancient-india"], "depth": 2}',
                "result": '{"pages_scraped": 15, "documents_found": 8, "success_rate": 0.87}',
                "progress": 100,
            },
        ]
        
        # Insert sample jobs
        for job in sample_jobs:
            query = """
            INSERT INTO processing_jobs 
            (job_type, status, input_data, result, progress, created_at, updated_at)
            VALUES (:job_type, :status, :input_data, :result, :progress, 
                    :created_at, :updated_at)
            """
            values = {**job, "created_at": datetime.now(), "updated_at": datetime.now()}
            await db.execute(query, values)
        
        await db.commit()
        logger.info("Sample data inserted successfully")


async def reset_database():
    """Drop all existing tables."""
    logger.warning("Resetting database - dropping all tables...")
    
    async with get_database() as db:
        tables = [
            "user_sessions",
            "processing_jobs", 
            "analysis_results",
            "research_documents"
        ]
        
        for table in tables:
            try:
                await db.execute(f"DROP TABLE IF EXISTS {table}")
                logger.info(f"Dropped table: {table}")
            except Exception as e:
                logger.warning(f"Could not drop table {table}: {e}")
        
        await db.commit()
        logger.info("Database reset completed")


async def verify_database():
    """Verify that all tables exist and are accessible."""
    logger.info("Verifying database structure...")
    
    async with get_database() as db:
        # Check if tables exist - this query works for both SQLite and PostgreSQL
        if "sqlite" in str(db.bind.url):
            tables_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        else:
            # PostgreSQL
            tables_query = """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        
        result = await db.execute(text(tables_query))
        tables = [row[0] for row in result.fetchall()]
        
        expected_tables = [
            "research_documents",
            "analysis_results", 
            "processing_jobs",
            "user_sessions"
        ]
        
        logger.info(f"Found tables: {tables}")
        
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            return False
        
        # Check table row counts
        for table in expected_tables:
            try:
                count_query = text(f"SELECT COUNT(*) FROM {table}")
                result = await db.execute(count_query)
                count = result.scalar() or 0
                logger.info(f"Table {table}: {count} rows")
            except Exception as e:
                logger.warning(f"Could not count rows in {table}: {e}")
        
        logger.info("Database verification completed successfully")
        return True


async def main():
    """Main initialization function."""
    parser = argparse.ArgumentParser(
        description="Initialize the AI Research Framework database"
    )
    parser.add_argument(
        "--reset", 
        action="store_true",
        help="Drop existing tables and recreate them"
    )
    parser.add_argument(
        "--sample-data",
        action="store_true", 
        help="Insert sample data for testing"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify database structure without making changes"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger.info("Starting database initialization...")
    
    try:
        # Load settings
        settings = Settings()
        logger.info(f"Using database: {settings.database_url}")
        
        # Ensure data directory exists for SQLite
        if "sqlite" in settings.database_url:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
        
        if args.verify_only:
            # Only verify database
            success = await verify_database()
            if success:
                logger.info("Database verification passed")
                return 0
            else:
                logger.error("Database verification failed")
                return 1
        
        if args.reset:
            # Reset database
            await reset_database()
        
        # Initialize database schema
        logger.info("Initializing database schema...")
        await init_database()
        logger.info("Database schema initialized")
        
        # Verify database structure
        success = await verify_database()
        if not success:
            logger.error("Database verification failed after initialization")
            return 1
        
        if args.sample_data:
            # Insert sample data
            await create_sample_data()
        
        logger.info("Database initialization completed successfully!")
        
        # Show next steps
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*50)
        print("\nNext steps:")
        print("1. Review the .env file and update configuration as needed")
        print("2. Start the application:")
        print("   - With UV: uv run uvicorn ai_research_framework.api.main:app --reload")
        print("   - With Docker: docker-compose up --build")
        print("3. Visit http://localhost:8000/docs for API documentation")
        print("4. Run tests: make test")
        
        if args.sample_data:
            print("\nSample data has been inserted for testing.")
            print("You can view it through the API endpoints.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
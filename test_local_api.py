#!/usr/bin/env python
"""
Test script for the AI Research Framework API.
Run this after starting the local server with run_local.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import httpx
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

async def test_health_endpoints():
    """Test health check endpoints."""
    print("\n🔍 Testing Health Endpoints...")
    
    async with httpx.AsyncClient() as client:
        # Test main health endpoint
        response = await client.get(f"{BASE_URL}/health/")
        print(f"  ✓ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Status: {data.get('status')}")
            print(f"    Environment: {data.get('environment')}")
        
        # Test readiness
        response = await client.get(f"{BASE_URL}/health/ready")
        print(f"  ✓ Readiness check: {response.status_code}")
        
        # Test liveness
        response = await client.get(f"{BASE_URL}/health/live")
        print(f"  ✓ Liveness check: {response.status_code}")

async def test_document_endpoints():
    """Test document management endpoints."""
    print("\n📄 Testing Document Endpoints...")
    
    async with httpx.AsyncClient() as client:
        # Test get supported formats
        response = await client.get(f"{BASE_URL}/api/documents/formats/supported")
        print(f"  ✓ Get supported formats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Formats: {data.get('formats', [])}")
        
        # Test list documents
        response = await client.get(f"{BASE_URL}/api/documents/")
        print(f"  ✓ List documents: {response.status_code}")
        
        # Test process URL (with a test URL)
        test_doc = {
            "url": "https://example.com/test-document",
            "metadata": {
                "title": "Test Document",
                "author": "Test Author",
                "source_type": "web",
                "language": "english",
                "tags": ["test", "demo"]
            }
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/documents/url",
                json=test_doc
            )
            print(f"  ✓ Process URL: {response.status_code}")
            if response.status_code == 200:
                doc_id = response.json().get("id")
                print(f"    Document ID: {doc_id}")
                return doc_id
        except Exception as e:
            print(f"  ⚠ Process URL failed: {e}")
            
    return None

async def test_search_endpoints():
    """Test search endpoints."""
    print("\n🔎 Testing Search Endpoints...")
    
    async with httpx.AsyncClient() as client:
        # Test quick search
        response = await client.get(
            f"{BASE_URL}/api/search/quick",
            params={"q": "ancient history", "limit": 5}
        )
        print(f"  ✓ Quick search: {response.status_code}")
        
        # Test search suggestions
        response = await client.get(
            f"{BASE_URL}/api/search/suggest",
            params={"q": "anc", "limit": 3}
        )
        print(f"  ✓ Search suggestions: {response.status_code}")
        
        # Test advanced search
        response = await client.get(
            f"{BASE_URL}/api/search/advanced",
            params={
                "q": "history",
                "source_type": "academic",
                "limit": 10
            }
        )
        print(f"  ✓ Advanced search: {response.status_code}")
        
        # Test semantic search
        search_request = {
            "query": "ancient civilizations",
            "search_type": "keyword",  # Use keyword for testing without vector DB
            "limit": 5,
            "include_snippets": True
        }
        
        response = await client.post(
            f"{BASE_URL}/api/search/",
            json=search_request
        )
        print(f"  ✓ Semantic search: {response.status_code}")

async def test_analysis_endpoints(document_id=None):
    """Test analysis endpoints."""
    print("\n🧪 Testing Analysis Endpoints...")
    
    if not document_id:
        print("  ⚠ No document ID available for analysis testing")
        return
    
    async with httpx.AsyncClient() as client:
        # Test document analysis
        analysis_request = {
            "document_id": document_id,
            "analysis_types": ["credibility", "bias", "entities"],
            "options": {}
        }
        
        response = await client.post(
            f"{BASE_URL}/api/analysis/analyze",
            json=analysis_request
        )
        print(f"  ✓ Document analysis: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Analyses performed: {list(data.get('analyses', {}).keys())}")
        
        # Test analysis history
        response = await client.get(
            f"{BASE_URL}/api/analysis/history/{document_id}"
        )
        print(f"  ✓ Analysis history: {response.status_code}")

async def test_research_endpoints():
    """Test research endpoints."""
    print("\n🔬 Testing Research Endpoints...")
    
    async with httpx.AsyncClient() as client:
        # Submit research query
        research_request = {
            "query": "Test research about ancient Indian dynasties",
            "time_period_start": "300 BCE",
            "time_period_end": "600 CE",
            "geographical_region": "India",
            "source_types": ["academic", "primary"],
            "max_sources": 3,
            "languages": ["english"],
            "generate_script": False
        }
        
        response = await client.post(
            f"{BASE_URL}/api/v1/research/",
            json=research_request
        )
        print(f"  ✓ Submit research: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            research_id = data.get("research_id")
            print(f"    Research ID: {research_id}")
            
            # Wait a bit for processing
            await asyncio.sleep(2)
            
            # Check status
            response = await client.get(
                f"{BASE_URL}/api/v1/research/{research_id}/status"
            )
            print(f"  ✓ Research status: {response.status_code}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"    Status: {status_data.get('status')}")
                print(f"    Progress: {status_data.get('progress')}")
            
            # Get results if completed
            if status_data.get("status") == "completed":
                response = await client.get(
                    f"{BASE_URL}/api/v1/research/{research_id}/results"
                )
                print(f"  ✓ Research results: {response.status_code}")
                if response.status_code == 200:
                    results = response.json()
                    print(f"    Sources found: {results.get('total_sources')}")
        
        # List research queries
        response = await client.get(
            f"{BASE_URL}/api/v1/research/",
            params={"limit": 5}
        )
        print(f"  ✓ List research queries: {response.status_code}")

async def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Research Framework - Local API Test Suite")
    print("=" * 60)
    print(f"Testing server at: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    try:
        # Run tests
        await test_health_endpoints()
        doc_id = await test_document_endpoints()
        await test_search_endpoints()
        await test_analysis_endpoints(doc_id)
        await test_research_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except httpx.ConnectError:
        print("\n❌ Error: Cannot connect to server!")
        print("Please ensure the local server is running:")
        print("  python run_local.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

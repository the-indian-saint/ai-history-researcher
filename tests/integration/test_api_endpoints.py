"""Integration tests for API endpoints."""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from ai_research_framework.api.main import app


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert data["status"] == "healthy"
    
    def test_health_endpoint_detailed(self):
        """Test detailed health check."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check service statuses
        services = data["services"]
        assert "database" in services
        assert "cache" in services
        assert "ai_analyzer" in services
        
        # Each service should have status
        for service_name, service_info in services.items():
            assert "status" in service_info
            assert service_info["status"] in ["healthy", "unhealthy", "unknown"]


class TestResearchEndpoints:
    """Test research API endpoints."""
    
    def test_research_endpoint_basic(self):
        """Test basic research endpoint."""
        client = TestClient(app)
        
        payload = {
            "query": "Maurya Empire administration",
            "max_results": 5
        }
        
        response = client.post("/api/v1/research/", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert "total_results" in data
        assert data["query"] == payload["query"]
    
    def test_research_endpoint_with_filters(self):
        """Test research endpoint with filters."""
        client = TestClient(app)
        
        payload = {
            "query": "Ancient Indian history",
            "max_results": 10,
            "source_types": ["academic", "primary"],
            "time_period": "ancient"
        }
        
        response = client.post("/api/v1/research/", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) <= 10
    
    def test_research_endpoint_empty_query(self):
        """Test research endpoint with empty query."""
        client = TestClient(app)
        
        payload = {"query": ""}
        
        response = client.post("/api/v1/research/", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_research_endpoint_invalid_payload(self):
        """Test research endpoint with invalid payload."""
        client = TestClient(app)
        
        # Missing required query field
        payload = {"max_results": 5}
        
        response = client.post("/api/v1/research/", json=payload)
        
        assert response.status_code == 422


class TestAnalysisEndpoints:
    """Test analysis API endpoints."""
    
    def test_credibility_analysis_endpoint(self):
        """Test credibility analysis endpoint."""
        client = TestClient(app)
        
        payload = {
            "text": "The Maurya Empire was founded by Chandragupta Maurya in 321 BCE.",
            "metadata": {
                "source_type": "academic",
                "author": "Dr. Test Historian"
            }
        }
        
        response = client.post("/api/v1/analyze/credibility", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis_type" in data
        assert "success" in data
        assert "result" in data
        assert "confidence" in data
        assert data["analysis_type"] == "credibility"
        assert data["success"] is True
    
    def test_bias_detection_endpoint(self):
        """Test bias detection endpoint."""
        client = TestClient(app)
        
        payload = {
            "text": "The British civilized the primitive Indian society.",
            "context": {"period": "colonial"}
        }
        
        response = client.post("/api/v1/analyze/bias", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis_type" in data
        assert "success" in data
        assert data["analysis_type"] == "bias_detection"
    
    def test_entity_extraction_endpoint(self):
        """Test entity extraction endpoint."""
        client = TestClient(app)
        
        payload = {
            "text": "Chandragupta Maurya founded the Maurya Empire at Pataliputra in 321 BCE.",
            "entity_types": ["people", "places", "dynasties", "dates"]
        }
        
        response = client.post("/api/v1/extract/entities", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis_type" in data
        assert "success" in data
        assert data["analysis_type"] == "entity_extraction"
    
    def test_analysis_endpoint_empty_text(self):
        """Test analysis endpoint with empty text."""
        client = TestClient(app)
        
        payload = {"text": ""}
        
        response = client.post("/api/v1/analyze/credibility", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_analysis_endpoint_large_text(self):
        """Test analysis endpoint with large text."""
        client = TestClient(app)
        
        # Create large text (but within reasonable limits)
        large_text = "Ancient Indian history. " * 1000
        
        payload = {
            "text": large_text,
            "metadata": {"source_type": "academic"}
        }
        
        response = client.post("/api/v1/analyze/credibility", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestScriptGenerationEndpoints:
    """Test script generation endpoints."""
    
    def test_script_generation_endpoint(self):
        """Test YouTube script generation endpoint."""
        client = TestClient(app)
        
        payload = {
            "topic": "Maurya Empire Administration",
            "research_data": [
                {
                    "title": "Administrative System",
                    "content": "The Maurya Empire had sophisticated administrative systems...",
                    "author": "Dr. Ancient History",
                    "source_url": "https://example.com/maurya"
                }
            ],
            "target_length": 10,
            "style": "educational"
        }
        
        response = client.post("/api/v1/generate/script", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis_type" in data
        assert "success" in data
        assert data["analysis_type"] == "script_generation"
        
        if data["success"]:
            result = data["result"]
            assert "script" in result
            assert "estimated_duration" in result
            assert "key_points" in result
    
    def test_script_generation_minimal_data(self):
        """Test script generation with minimal data."""
        client = TestClient(app)
        
        payload = {
            "topic": "Ancient India",
            "research_data": [],
            "target_length": 5
        }
        
        response = client.post("/api/v1/generate/script", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_script_generation_invalid_length(self):
        """Test script generation with invalid length."""
        client = TestClient(app)
        
        payload = {
            "topic": "Ancient India",
            "research_data": [],
            "target_length": -5  # Invalid negative length
        }
        
        response = client.post("/api/v1/generate/script", json=payload)
        
        assert response.status_code == 422  # Validation error


class TestDocumentProcessingEndpoints:
    """Test document processing endpoints."""
    
    def test_document_upload_endpoint(self, sample_txt_file):
        """Test document upload and processing."""
        client = TestClient(app)
        
        with open(sample_txt_file, 'rb') as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = client.post("/api/v1/documents/upload", files=files)
        
        # Should accept file upload
        assert response.status_code in [200, 201]
    
    def test_document_processing_status(self):
        """Test document processing status endpoint."""
        client = TestClient(app)
        
        # Test with dummy document ID
        response = client.get("/api/v1/documents/test-doc-id/status")
        
        # Should return status (even if document doesn't exist)
        assert response.status_code in [200, 404]


class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint."""
        client = TestClient(app)
        
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test method not allowed."""
        client = TestClient(app)
        
        # Try GET on POST endpoint
        response = client.get("/api/v1/research/")
        
        assert response.status_code == 405
    
    def test_invalid_json(self):
        """Test invalid JSON payload."""
        client = TestClient(app)
        
        # Send invalid JSON
        response = client.post(
            "/api/v1/analyze/credibility",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_large_payload(self):
        """Test handling of large payloads."""
        client = TestClient(app)
        
        # Create very large text
        large_text = "x" * 1000000  # 1MB of text
        
        payload = {
            "text": large_text,
            "metadata": {}
        }
        
        response = client.post("/api/v1/analyze/credibility", json=payload)
        
        # Should either process or reject gracefully
        assert response.status_code in [200, 413, 422]


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint."""
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint."""
        client = TestClient(app)
        
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self):
        """Test ReDoc endpoint."""
        client = TestClient(app)
        
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API workflows."""
    
    def test_research_to_analysis_workflow(self):
        """Test complete research to analysis workflow."""
        client = TestClient(app)
        
        # Step 1: Perform research
        research_payload = {
            "query": "Maurya Empire administration",
            "max_results": 3
        }
        
        research_response = client.post("/api/v1/research/", json=research_payload)
        assert research_response.status_code == 200
        
        research_data = research_response.json()
        
        # Step 2: Analyze first result if available
        if research_data["results"]:
            first_result = research_data["results"][0]
            
            analysis_payload = {
                "text": first_result.get("content", "Sample content"),
                "metadata": {
                    "source_type": "academic",
                    "title": first_result.get("title", "Sample title")
                }
            }
            
            # Test credibility analysis
            credibility_response = client.post(
                "/api/v1/analyze/credibility", 
                json=analysis_payload
            )
            assert credibility_response.status_code == 200
            
            # Test bias detection
            bias_response = client.post(
                "/api/v1/analyze/bias", 
                json=analysis_payload
            )
            assert bias_response.status_code == 200
    
    def test_research_to_script_workflow(self):
        """Test research to script generation workflow."""
        client = TestClient(app)
        
        # Step 1: Perform research
        research_payload = {
            "query": "Ancient Indian administrative systems",
            "max_results": 5
        }
        
        research_response = client.post("/api/v1/research/", json=research_payload)
        assert research_response.status_code == 200
        
        research_data = research_response.json()
        
        # Step 2: Generate script from research
        script_payload = {
            "topic": "Ancient Indian Administrative Systems",
            "research_data": research_data["results"][:3],  # Use first 3 results
            "target_length": 8,
            "style": "educational"
        }
        
        script_response = client.post("/api/v1/generate/script", json=script_payload)
        assert script_response.status_code == 200
        
        script_data = script_response.json()
        assert script_data["success"] is True
    
    def test_concurrent_api_requests(self):
        """Test concurrent API requests."""
        import asyncio
        import httpx
        
        async def make_request(endpoint, payload):
            async with httpx.AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(endpoint, json=payload)
                return response
        
        async def test_concurrent():
            # Create multiple concurrent requests
            tasks = []
            
            for i in range(5):
                payload = {
                    "text": f"Test content {i} about ancient Indian history.",
                    "metadata": {"source_type": "test"}
                }
                task = make_request("/api/v1/analyze/credibility", payload)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 200
        
        # Run the concurrent test
        asyncio.run(test_concurrent())
    
    def test_api_performance(self):
        """Test API performance with timing."""
        import time
        
        client = TestClient(app)
        
        payload = {
            "text": "Performance test content about Maurya Empire administration systems.",
            "metadata": {"source_type": "performance_test"}
        }
        
        # Measure response time
        start_time = time.time()
        response = client.post("/api/v1/analyze/credibility", json=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 10.0  # Should respond within 10 seconds
        
        # Check if processing time is included in response
        data = response.json()
        if "processing_time" in data:
            assert data["processing_time"] > 0


class TestAPIValidation:
    """Test API input validation."""
    
    def test_research_query_validation(self):
        """Test research query validation."""
        client = TestClient(app)
        
        # Test various invalid queries
        invalid_payloads = [
            {},  # Missing query
            {"query": ""},  # Empty query
            {"query": "x" * 10000},  # Too long query
            {"max_results": -1},  # Invalid max_results
            {"max_results": 1000},  # Too many results
        ]
        
        for payload in invalid_payloads:
            response = client.post("/api/v1/research/", json=payload)
            assert response.status_code == 422
    
    def test_analysis_text_validation(self):
        """Test analysis text validation."""
        client = TestClient(app)
        
        # Test various invalid text inputs
        invalid_payloads = [
            {},  # Missing text
            {"text": ""},  # Empty text
            {"text": None},  # Null text
        ]
        
        for payload in invalid_payloads:
            response = client.post("/api/v1/analyze/credibility", json=payload)
            assert response.status_code == 422
    
    def test_script_generation_validation(self):
        """Test script generation validation."""
        client = TestClient(app)
        
        # Test various invalid inputs
        invalid_payloads = [
            {},  # Missing topic
            {"topic": ""},  # Empty topic
            {"topic": "Test", "target_length": 0},  # Invalid length
            {"topic": "Test", "target_length": 1000},  # Too long
        ]
        
        for payload in invalid_payloads:
            response = client.post("/api/v1/generate/script", json=payload)
            assert response.status_code == 422


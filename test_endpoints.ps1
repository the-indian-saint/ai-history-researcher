# Test API Endpoints Script
$baseUrl = "http://localhost:8000"

Write-Host "Testing AI History Researcher API Endpoints" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Function to test endpoint
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Description,
        [hashtable]$Body = @{},
        [hashtable]$Headers = @{"Content-Type" = "application/json"}
    )
    
    Write-Host "`n$Description" -ForegroundColor Yellow
    Write-Host "Endpoint: $Method $Endpoint" -ForegroundColor Cyan
    
    try {
        $uri = "$baseUrl$Endpoint"
        
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $uri -Method $Method -Headers $Headers -UseBasicParsing
        } else {
            $jsonBody = $Body | ConvertTo-Json -Depth 5
            $response = Invoke-WebRequest -Uri $uri -Method $Method -Body $jsonBody -Headers $Headers -UseBasicParsing
        }
        
        Write-Host "Status: $($response.StatusCode) - Success" -ForegroundColor Green
        
        # Parse and display response
        $content = $response.Content | ConvertFrom-Json
        $content | ConvertTo-Json -Depth 3 | Write-Host
        
        return $true
    }
    catch {
        Write-Host "Status: Error - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test Health Endpoint
Test-Endpoint -Method "GET" -Endpoint "/health" -Description "1. Health Check"

# Test Metrics Endpoint
Test-Endpoint -Method "GET" -Endpoint "/metrics" -Description "2. Metrics"

# Test Document Upload (with sample data)
$documentBody = @{
    title = "Ancient Indian History Test Document"
    content = "The Mauryan Empire was established by Chandragupta Maurya in 322 BCE. It was one of the largest empires in ancient India."
    source_url = "https://example.com/test"
    source_type = "academic"
    author = "Test Author"
    metadata = @{
        language = "english"
        dynasty = "Maurya"
    }
}
Test-Endpoint -Method "POST" -Endpoint "/api/v1/documents/upload" -Description "3. Upload Document" -Body $documentBody

# Test Search Endpoints
$searchBody = @{
    query = "Mauryan Empire"
    search_type = "hybrid"
    limit = 5
    include_facets = $true
}
Test-Endpoint -Method "POST" -Endpoint "/api/v1/search/" -Description "4. Hybrid Search" -Body $searchBody

# Test Quick Search
Test-Endpoint -Method "GET" -Endpoint "/api/v1/search/quick?q=Maurya&limit=5" -Description "5. Quick Search"

# Test Advanced Search
Test-Endpoint -Method "GET" -Endpoint "/api/v1/search/advanced?q=Empire&source_type=academic&limit=5" -Description "6. Advanced Search"

# Test Search Suggestions
Test-Endpoint -Method "GET" -Endpoint "/api/v1/search/suggest?q=Maur&limit=5" -Description "7. Search Suggestions"

# Test Document List
Test-Endpoint -Method "GET" -Endpoint "/api/v1/documents/?limit=5" -Description "8. List Documents"

# Test Research Query
$researchBody = @{
    query = "What was the administrative structure of the Mauryan Empire?"
    time_period_start = "400 BCE"
    time_period_end = "200 BCE"
    source_types = @("academic", "primary")
    max_sources = 10
}
Test-Endpoint -Method "POST" -Endpoint "/api/v1/research/query" -Description "9. Research Query" -Body $researchBody

# Test Analysis Endpoint
$analysisBody = @{
    document_id = "test-doc-123"
    analysis_type = "credibility"
    content = "The Mauryan Empire was established by Chandragupta Maurya."
}
Test-Endpoint -Method "POST" -Endpoint "/api/v1/analysis/analyze" -Description "10. Document Analysis" -Body $analysisBody

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "API Endpoint Testing Complete!" -ForegroundColor Green

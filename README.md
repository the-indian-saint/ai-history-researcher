# AI Research Framework for Ancient Indian History

A comprehensive AI-powered research framework designed specifically for creating YouTube content about ancient Indian history. This system automates source discovery, document processing, and content analysis to help researchers and content creators access lesser-known historical information.

## 🚀 Features

- **Automated Source Discovery**: Scrape academic databases, digital archives, and institutional repositories
- **Multi-Language OCR**: Process documents in English, Hindi, Sanskrit, and other Indian languages
- **AI-Powered Analysis**: Credibility assessment, bias detection, and thematic analysis
- **Semantic Search**: Vector-based search across historical documents and sources
- **Citation Management**: Automatic citation generation and source tracking
- **YouTube Script Generation**: AI-assisted script creation with proper attributions
- **Local Model Support**: Run completely offline using local LLMs (Ollama)
- **Real-Time Web Browsing**: Search and scrape live web content for up-to-date research

## 🏗️ Architecture

The framework follows a modular microservices architecture:

- **Collectors**: Web scraping and data collection from external sources
- **Processors**: Document processing, OCR, and text extraction
- **Storage**: Vector databases and document storage systems
- **Analyzers**: AI-powered content analysis and insights
- **API**: REST endpoints for external access and integration

## 📋 Prerequisites

- Python 3.11 or higher
- UV package manager
- PostgreSQL 15+
- Redis 7+
- Tesseract OCR with language packs
- At least 4GB RAM and 10GB disk space
- Docker & Docker Compose (for local model support)

## 🛠️ Installation

### Using UV (Recommended)

1. **Install UV package manager**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/ai-research-framework.git
   cd ai-research-framework
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**:
   ```bash
   uv run python scripts/init_db.py
   ```

6. **Start the application**:
   ```bash
   uv run python -m ai_research_framework.api.main
   ```

### Using Docker

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

The application will be available at `http://localhost:8000`.

### Local Model Setup (Offline Mode)

This framework supports running completely offline using [Ollama](https://ollama.com).

1. **Start the stack with Ollama**:
   ```bash
   docker-compose up -d
   ```

2. **Auto-Pull Model**:
   The stack includes an initializer that will automatically pull `phi3:mini`. Wait a few moments for the model to benefit ready.
   
   If you wish to use a different model:
   ```bash
   docker compose exec ollama ollama pull your-model
   ```

3. **Enable Local Mode**:
   Set text `USE_LOCAL_MODEL=true` in your `.env` file (see Configuration).

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/research_db

# Redis
REDIS_URL=redis://localhost:6379

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8001

# AI Services
OPENAI_API_KEY=your_openai_api_key

ANTHROPIC_API_KEY=your_anthropic_api_key

# Local AI (Ollama)
USE_LOCAL_MODEL=false          # Set to true to use local model
LOCAL_MODEL_BASE_URL=http://ollama:11434/v1
LOCAL_MODEL_NAME=phi3:mini

# OCR Configuration
TESSERACT_CMD=/usr/bin/tesseract
OCR_CONFIDENCE_THRESHOLD=80

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### OCR Language Support

Install Tesseract language packs:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-hin tesseract-ocr-san tesseract-ocr-tam

# macOS
brew install tesseract-lang

# Verify installation
tesseract --list-langs
```

## 📖 Usage

### Basic Research Query

```python
import asyncio
from ai_research_framework.api.client import ResearchClient

async def main():
    client = ResearchClient("http://localhost:8000")
    
    # Authenticate
    await client.authenticate("username", "password")
    
    # Submit research query
    result = await client.research(
        query="Gupta Empire administrative system",
        time_period={"start": "320 CE", "end": "550 CE"},
        max_sources=10,
        source_types=["academic", "primary"]
    )
    
    print(f"Found {len(result.sources)} sources")
    print(f"Analysis: {result.analysis_summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

### REST API Usage

```bash
# Authenticate
curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "pass"}'

# Submit research query
curl -X POST "http://localhost:8000/api/v1/research" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Mauryan Empire taxation system",
       "max_sources": 5,
       "source_types": ["academic"]
     }'
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests
```

## 🚀 Deployment

### Production Deployment

1. **Build Docker image**:
   ```bash
   docker build -t ai-research-framework:latest .
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Or deploy to Kubernetes**:
   ```bash
   kubectl apply -f k8s/
   ```

### Environment-Specific Configurations

- **Development**: Use SQLite and local Redis
- **Staging**: Use managed databases with reduced resources
- **Production**: Use managed services with high availability

## 📚 Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `uv sync --group dev`
4. Make your changes
5. Run tests and linting: `uv run pytest && uv run black . && uv run flake8`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Archaeological Survey of India for historical data access
- Internet Archive for digital document preservation
- Academic institutions providing open access to research
- Open source community for foundational tools and libraries

## 📞 Support

- **Documentation**: [https://ai-research-framework.readthedocs.io](https://ai-research-framework.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/your-org/ai-research-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/ai-research-framework/discussions)
- **Email**: research-support@example.com

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**Note**: This framework is designed for educational and research purposes. Always verify historical claims with multiple sources and maintain proper academic standards when using the generated content.


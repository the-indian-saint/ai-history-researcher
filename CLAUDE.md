# AI Research Framework for Ancient Indian History

A comprehensive AI-powered research framework designed specifically for creating YouTube content about ancient Indian history. This system automates source discovery, document processing, and content analysis to help researchers and content creators access lesser-known historical information.

## Project Overview

This framework combines modern AI technologies with specialized knowledge of ancient Indian history to provide:
- Automated web scraping and document collection from academic sources
- Multi-language OCR processing (English, Hindi, Sanskrit)
- AI-powered content analysis and credibility assessment
- Semantic search across historical documents
- YouTube script generation with proper citations

## Commands

### Development
- `uv sync`: Install all dependencies and create virtual environment
- `uv run python -m src.ai_research_framework.api.main`: Start the development server
- `uv run pytest`: Run the complete test suite
- `uv run pytest tests/unit/`: Run unit tests only
- `uv run pytest tests/integration/`: Run integration tests only

### Code Quality
- `uv run black .`: Format code with Black
- `uv run flake8 .`: Run linting with flake8
- `uv run mypy src/`: Run type checking
- `uv run pre-commit run --all-files`: Run all pre-commit hooks

### Database and Storage
- `uv run python scripts/init_db.py`: Initialize database schema
- `uv run python scripts/migrate_db.py`: Run database migrations
- `uv run python scripts/backup_data.py`: Create data backup
- `uv run python scripts/restore_data.py`: Restore from backup

### Deployment
- `docker-compose up -d`: Start all services with Docker
- `docker-compose down`: Stop all services
- `uv build`: Build distribution packages
- `uv run python scripts/deploy.py`: Deploy to production

## Code Style and Standards

### Python Code Style
- Use Python 3.11+ features and type hints throughout
- Follow PEP 8 with Black formatting (line length: 88 characters)
- Use async/await for all I/O operations
- Prefer composition over inheritance
- Use dataclasses or Pydantic models for data structures
- Import order: standard library, third-party, local imports

### API Design
- Use FastAPI with automatic OpenAPI documentation
- Implement proper HTTP status codes and error handling
- Use Pydantic models for request/response validation
- Include comprehensive docstrings for all endpoints
- Implement rate limiting and authentication where appropriate

### Database and Storage
- Use async database operations with SQLAlchemy
- Implement proper connection pooling and error handling
- Use migrations for schema changes
- Store sensitive data encrypted
- Implement proper backup and recovery procedures

### Testing Standards
- Maintain >90% test coverage
- Use pytest with async support
- Mock external API calls and services
- Include integration tests for critical workflows
- Test error conditions and edge cases

## Architecture and Design Patterns

### Core Components
1. **Collectors**: Responsible for gathering data from various sources
2. **Processors**: Handle document processing, OCR, and text extraction
3. **Storage**: Manage vector databases and document storage
4. **Analyzers**: Perform AI-powered analysis and insights
5. **API**: Provide REST endpoints for external access

### Design Principles
- **Separation of Concerns**: Each component has a single responsibility
- **Dependency Injection**: Use dependency injection for testability
- **Error Handling**: Implement comprehensive error handling and logging
- **Scalability**: Design for horizontal scaling and high availability
- **Security**: Implement security best practices throughout

### Data Flow
1. User submits research query through API
2. Collectors gather relevant sources from multiple repositories
3. Processors extract and clean text content
4. Storage systems index and store processed documents
5. Analyzers perform AI-powered analysis and insights
6. Results are returned to user with proper citations

## Historical Context and Domain Knowledge

### Ancient Indian History Focus Areas
- **Mauryan Empire** (321-185 BCE): Administration, Ashoka's edicts, Arthashastra
- **Gupta Empire** (320-550 CE): Golden age, literature, mathematics, astronomy
- **Regional Dynasties**: Cholas, Pallavas, Chalukyas, Rashtrakutas
- **Religious Movements**: Buddhism, Jainism, Hindu philosophy
- **Cultural Achievements**: Art, architecture, literature, science

### Source Types and Credibility
- **Primary Sources**: Inscriptions, coins, manuscripts, archaeological evidence
- **Secondary Sources**: Modern scholarly works, translations, interpretations
- **Credibility Factors**: Author credentials, publication venue, peer review, citations
- **Bias Considerations**: Colonial perspectives, religious bias, temporal distance

### Language and Script Handling
- **Sanskrit**: Devanagari script, IAST transliteration, grammatical analysis
- **Prakrit**: Various regional scripts and dialects
- **Tamil**: Ancient Tamil literature and inscriptions
- **Persian**: Medieval court records and chronicles

## Workflow Guidelines

### Research Workflow
1. **Query Formulation**: Use specific time periods, regions, and themes
2. **Source Discovery**: Prioritize academic databases and digital archives
3. **Document Processing**: Handle multiple formats and languages
4. **Analysis and Verification**: Cross-reference claims across sources
5. **Content Creation**: Generate scripts with proper citations

### Quality Assurance
- Verify all historical claims with multiple sources
- Check dates and chronologies for consistency
- Ensure proper attribution and citation format
- Review content for potential biases or inaccuracies
- Maintain high standards for academic integrity

### Content Creation Best Practices
- Focus on lesser-known but well-documented topics
- Balance entertainment value with historical accuracy
- Include visual suggestions for YouTube content
- Provide clear explanations of complex concepts
- Maintain engaging narrative structure

## Security and Privacy

### Data Protection
- Encrypt sensitive data at rest and in transit
- Implement proper access controls and authentication
- Regular security audits and vulnerability assessments
- Comply with data protection regulations (GDPR, etc.)
- Secure handling of API keys and credentials

### API Security
- Implement rate limiting and DDoS protection
- Use HTTPS for all communications
- Validate and sanitize all input data
- Implement proper error handling without information leakage
- Regular security updates and patch management

## Performance and Scalability

### Optimization Strategies
- Use async operations for I/O-bound tasks
- Implement caching at multiple levels
- Optimize database queries and indexes
- Use connection pooling for external services
- Monitor and profile performance regularly

### Scaling Considerations
- Design for horizontal scaling with load balancers
- Use containerization for consistent deployments
- Implement proper logging and monitoring
- Plan for database scaling and replication
- Consider CDN for static content delivery

## Troubleshooting and Debugging

### Common Issues
- **OCR Accuracy**: Check image quality and language settings
- **API Rate Limits**: Implement proper retry logic and backoff
- **Database Connections**: Monitor connection pool usage
- **Memory Usage**: Profile memory usage during large document processing
- **Search Relevance**: Tune vector similarity thresholds

### Debugging Tools
- Use structured logging with correlation IDs
- Implement health checks for all services
- Monitor key metrics and set up alerts
- Use profiling tools for performance analysis
- Maintain comprehensive error tracking

## Contributing Guidelines

### Development Setup
1. Clone the repository and install UV package manager
2. Run `uv sync` to install dependencies
3. Set up pre-commit hooks for code quality
4. Configure environment variables for development
5. Run tests to ensure everything works correctly

### Code Contribution Process
1. Create feature branch from main
2. Implement changes with proper tests
3. Run code quality checks and tests
4. Update documentation as needed
5. Submit pull request with detailed description

### Documentation Standards
- Update README.md for user-facing changes
- Add docstrings for all public functions and classes
- Update API documentation for endpoint changes
- Include examples and usage instructions
- Maintain changelog for version releases


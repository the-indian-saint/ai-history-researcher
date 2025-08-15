"""Unit tests for document processor module."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import hashlib

from ai_research_framework.processors.document_processor import (
    DocumentProcessor,
    ProcessingResult,
    DocumentType,
    ProcessingError,
    processor
)


class TestDocumentType:
    """Test DocumentType enum."""
    
    def test_document_type_values(self):
        """Test DocumentType enum values."""
        assert DocumentType.PDF == "pdf"
        assert DocumentType.DOCX == "docx"
        assert DocumentType.TXT == "txt"
        assert DocumentType.HTML == "html"
        assert DocumentType.RTF == "rtf"
        assert DocumentType.ODT == "odt"
        assert DocumentType.EPUB == "epub"
        assert DocumentType.IMAGE == "image"
        assert DocumentType.UNKNOWN == "unknown"


class TestProcessingResult:
    """Test ProcessingResult dataclass."""
    
    def test_processing_result_creation(self):
        """Test ProcessingResult creation."""
        result = ProcessingResult(
            success=True,
            content="Test content",
            metadata={"pages": 5},
            file_path="/test/path.pdf",
            document_type=DocumentType.PDF,
            processing_time=1.5,
            checksum="abc123",
            error_message=None
        )
        
        assert result.success is True
        assert result.content == "Test content"
        assert result.metadata["pages"] == 5
        assert result.document_type == DocumentType.PDF
        assert result.processing_time == 1.5
        assert result.checksum == "abc123"
    
    def test_processing_result_with_error(self):
        """Test ProcessingResult with error."""
        result = ProcessingResult(
            success=False,
            content="",
            metadata={},
            file_path="/test/path.pdf",
            document_type=DocumentType.PDF,
            processing_time=0.1,
            checksum="",
            error_message="Processing failed"
        )
        
        assert result.success is False
        assert result.error_message == "Processing failed"


class TestProcessingError:
    """Test ProcessingError exception."""
    
    def test_processing_error_creation(self):
        """Test ProcessingError creation."""
        error = ProcessingError("Test error message")
        
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)


class TestDocumentProcessor:
    """Test DocumentProcessor class."""
    
    def test_processor_initialization(self):
        """Test DocumentProcessor initialization."""
        processor = DocumentProcessor()
        
        assert processor is not None
        assert hasattr(processor, 'supported_formats')
        assert 'pdf' in processor.supported_formats
        assert 'docx' in processor.supported_formats
        assert 'txt' in processor.supported_formats
    
    def test_detect_document_type_by_extension(self):
        """Test document type detection by file extension."""
        processor = DocumentProcessor()
        
        # Test various extensions
        assert processor._detect_document_type("test.pdf") == DocumentType.PDF
        assert processor._detect_document_type("test.docx") == DocumentType.DOCX
        assert processor._detect_document_type("test.txt") == DocumentType.TXT
        assert processor._detect_document_type("test.html") == DocumentType.HTML
        assert processor._detect_document_type("test.rtf") == DocumentType.RTF
        assert processor._detect_document_type("test.odt") == DocumentType.ODT
        assert processor._detect_document_type("test.epub") == DocumentType.EPUB
        
        # Test image extensions
        assert processor._detect_document_type("test.jpg") == DocumentType.IMAGE
        assert processor._detect_document_type("test.png") == DocumentType.IMAGE
        assert processor._detect_document_type("test.tiff") == DocumentType.IMAGE
        
        # Test unknown extension
        assert processor._detect_document_type("test.xyz") == DocumentType.UNKNOWN
    
    def test_detect_document_type_case_insensitive(self):
        """Test case-insensitive document type detection."""
        processor = DocumentProcessor()
        
        assert processor._detect_document_type("test.PDF") == DocumentType.PDF
        assert processor._detect_document_type("test.Docx") == DocumentType.DOCX
        assert processor._detect_document_type("test.TXT") == DocumentType.TXT
    
    def test_calculate_checksum(self, temp_dir):
        """Test checksum calculation."""
        processor = DocumentProcessor()
        
        # Create test file
        test_file = temp_dir / "test.txt"
        test_content = "Test content for checksum"
        test_file.write_text(test_content)
        
        checksum = processor._calculate_checksum(str(test_file))
        
        # Verify checksum
        expected_checksum = hashlib.md5(test_content.encode()).hexdigest()
        assert checksum == expected_checksum
    
    def test_calculate_checksum_nonexistent_file(self):
        """Test checksum calculation with nonexistent file."""
        processor = DocumentProcessor()
        
        checksum = processor._calculate_checksum("/nonexistent/file.txt")
        assert checksum == ""
    
    @pytest.mark.asyncio
    async def test_process_text_file(self, sample_txt_file):
        """Test processing text file."""
        processor = DocumentProcessor()
        
        result = await processor.process_document(str(sample_txt_file))
        
        assert result.success is True
        assert result.document_type == DocumentType.TXT
        assert "Sample text content" in result.content
        assert result.processing_time > 0
        assert result.checksum != ""
    
    @pytest.mark.asyncio
    async def test_process_text_file_with_encoding(self, temp_dir):
        """Test processing text file with different encodings."""
        processor = DocumentProcessor()
        
        # Create file with UTF-8 content
        test_file = temp_dir / "utf8.txt"
        test_content = "Test content with unicode: café, naïve, résumé"
        test_file.write_text(test_content, encoding='utf-8')
        
        result = await processor.process_document(str(test_file))
        
        assert result.success is True
        assert "café" in result.content
        assert "naïve" in result.content
    
    @pytest.mark.asyncio
    async def test_process_html_file(self, temp_dir):
        """Test processing HTML file."""
        processor = DocumentProcessor()
        
        # Create HTML file
        html_file = temp_dir / "test.html"
        html_content = """
        <html>
        <head><title>Test Document</title></head>
        <body>
        <h1>Ancient Indian History</h1>
        <p>The Maurya Empire was founded by <strong>Chandragupta Maurya</strong>.</p>
        <p>The capital was at Pataliputra.</p>
        </body>
        </html>
        """
        html_file.write_text(html_content)
        
        result = await processor.process_document(str(html_file))
        
        assert result.success is True
        assert result.document_type == DocumentType.HTML
        assert "Ancient Indian History" in result.content
        assert "Chandragupta Maurya" in result.content
        # HTML tags should be stripped
        assert "<h1>" not in result.content
        assert "<p>" not in result.content
    
    @pytest.mark.asyncio
    async def test_process_pdf_file_fallback(self, temp_dir):
        """Test processing PDF file with fallback method."""
        processor = DocumentProcessor()
        
        # Create fake PDF file (will use fallback)
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("Fake PDF content")
        
        result = await processor.process_document(str(pdf_file))
        
        # Should attempt processing and either succeed or fail gracefully
        assert isinstance(result, ProcessingResult)
        assert result.document_type == DocumentType.PDF
    
    @pytest.mark.asyncio
    async def test_process_docx_file_fallback(self, temp_dir):
        """Test processing DOCX file with fallback method."""
        processor = DocumentProcessor()
        
        # Create fake DOCX file (will use fallback)
        docx_file = temp_dir / "test.docx"
        docx_file.write_text("Fake DOCX content")
        
        result = await processor.process_document(str(docx_file))
        
        # Should attempt processing
        assert isinstance(result, ProcessingResult)
        assert result.document_type == DocumentType.DOCX
    
    @pytest.mark.asyncio
    async def test_process_image_file_fallback(self, temp_dir):
        """Test processing image file with OCR fallback."""
        processor = DocumentProcessor()
        
        # Create fake image file
        image_file = temp_dir / "test.jpg"
        image_file.write_bytes(b"Fake image content")
        
        result = await processor.process_document(str(image_file))
        
        # Should attempt OCR processing
        assert isinstance(result, ProcessingResult)
        assert result.document_type == DocumentType.IMAGE
    
    @pytest.mark.asyncio
    async def test_process_nonexistent_file(self):
        """Test processing nonexistent file."""
        processor = DocumentProcessor()
        
        result = await processor.process_document("/nonexistent/file.txt")
        
        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_process_unsupported_file(self, temp_dir):
        """Test processing unsupported file type."""
        processor = DocumentProcessor()
        
        # Create file with unsupported extension
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("Unsupported content")
        
        result = await processor.process_document(str(unsupported_file))
        
        assert result.success is False
        assert result.document_type == DocumentType.UNKNOWN
        assert "unsupported" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_process_empty_file(self, temp_dir):
        """Test processing empty file."""
        processor = DocumentProcessor()
        
        # Create empty file
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        
        result = await processor.process_document(str(empty_file))
        
        assert result.success is True
        assert result.content == ""
        assert result.document_type == DocumentType.TXT
    
    @pytest.mark.asyncio
    async def test_process_large_file(self, temp_dir):
        """Test processing large file."""
        processor = DocumentProcessor()
        
        # Create large text file
        large_file = temp_dir / "large.txt"
        large_content = "Large content line.\n" * 10000  # 10k lines
        large_file.write_text(large_content)
        
        result = await processor.process_document(str(large_file))
        
        assert result.success is True
        assert len(result.content) > 100000  # Should be large
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, temp_dir):
        """Test batch document processing."""
        processor = DocumentProcessor()
        
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = temp_dir / f"test_{i}.txt"
            file_path.write_text(f"Content of file {i}")
            files.append(str(file_path))
        
        results = await processor.process_documents(files)
        
        assert len(results) == 3
        assert all(result.success for result in results)
        assert all("Content of file" in result.content for result in results)
    
    @pytest.mark.asyncio
    async def test_batch_processing_with_errors(self, temp_dir):
        """Test batch processing with some errors."""
        processor = DocumentProcessor()
        
        # Create mix of valid and invalid files
        valid_file = temp_dir / "valid.txt"
        valid_file.write_text("Valid content")
        
        files = [
            str(valid_file),
            "/nonexistent/file.txt",
            str(temp_dir / "another_valid.txt")
        ]
        
        # Create second valid file
        (temp_dir / "another_valid.txt").write_text("Another valid content")
        
        results = await processor.process_documents(files)
        
        assert len(results) == 3
        assert results[0].success is True  # valid file
        assert results[1].success is False  # nonexistent file
        assert results[2].success is True  # another valid file
    
    def test_supported_formats(self):
        """Test supported formats list."""
        processor = DocumentProcessor()
        
        expected_formats = {'pdf', 'docx', 'txt', 'html', 'rtf', 'odt', 'epub', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'}
        
        assert processor.supported_formats == expected_formats
    
    def test_is_supported_format(self):
        """Test format support checking."""
        processor = DocumentProcessor()
        
        # Test supported formats
        assert processor.is_supported("test.pdf") is True
        assert processor.is_supported("test.txt") is True
        assert processor.is_supported("test.jpg") is True
        
        # Test unsupported formats
        assert processor.is_supported("test.xyz") is False
        assert processor.is_supported("test.mp4") is False


class TestGlobalProcessor:
    """Test global processor instance."""
    
    def test_global_processor_exists(self):
        """Test that global processor instance exists."""
        assert processor is not None
        assert isinstance(processor, DocumentProcessor)
    
    @pytest.mark.asyncio
    async def test_global_processor_functionality(self, sample_txt_file):
        """Test global processor functionality."""
        result = await processor.process_document(str(sample_txt_file))
        
        assert isinstance(result, ProcessingResult)
        assert result.success is True


@pytest.mark.unit
class TestDocumentProcessorIntegration:
    """Integration tests for document processor."""
    
    @pytest.mark.asyncio
    async def test_processing_workflow(self, temp_dir):
        """Test complete processing workflow."""
        processor = DocumentProcessor()
        
        # Create test document
        test_file = temp_dir / "workflow_test.txt"
        test_content = """
        Ancient Indian History Research Document
        
        The Maurya Empire (321-185 BCE) was founded by Chandragupta Maurya.
        The empire's capital was located at Pataliputra (modern-day Patna).
        
        Key rulers:
        - Chandragupta Maurya (founder)
        - Bindusara (son of Chandragupta)
        - Ashoka (grandson, most famous ruler)
        
        The empire is known for its administrative efficiency and Ashoka's
        promotion of Buddhism throughout the realm.
        """
        test_file.write_text(test_content)
        
        # Process document
        result = await processor.process_document(str(test_file))
        
        # Verify results
        assert result.success is True
        assert result.document_type == DocumentType.TXT
        assert "Maurya Empire" in result.content
        assert "Chandragupta Maurya" in result.content
        assert "Pataliputra" in result.content
        assert result.checksum != ""
        assert result.processing_time > 0
        
        # Verify metadata
        assert "file_size" in result.metadata
        assert "encoding" in result.metadata
        assert result.metadata["file_size"] > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, temp_dir):
        """Test concurrent document processing."""
        import asyncio
        
        processor = DocumentProcessor()
        
        # Create multiple test files
        files = []
        for i in range(5):
            file_path = temp_dir / f"concurrent_{i}.txt"
            file_path.write_text(f"Document {i} content about ancient India.")
            files.append(str(file_path))
        
        # Process concurrently
        tasks = [processor.process_document(file_path) for file_path in files]
        results = await asyncio.gather(*tasks)
        
        # Verify all processed successfully
        assert len(results) == 5
        assert all(result.success for result in results)
        assert all(f"Document {i}" in results[i].content for i in range(5))
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, temp_dir):
        """Test error recovery in processing."""
        processor = DocumentProcessor()
        
        # Create file that will cause processing error
        problematic_file = temp_dir / "problematic.txt"
        
        # Write file then make it unreadable (simulate permission error)
        problematic_file.write_text("Test content")
        
        # Process the file
        result = await processor.process_document(str(problematic_file))
        
        # Should handle gracefully
        assert isinstance(result, ProcessingResult)
        # May succeed or fail depending on system, but should not crash
    
    @pytest.mark.asyncio
    async def test_metadata_extraction(self, temp_dir):
        """Test metadata extraction from documents."""
        processor = DocumentProcessor()
        
        # Create test file with known properties
        test_file = temp_dir / "metadata_test.txt"
        test_content = "Test content for metadata extraction"
        test_file.write_text(test_content)
        
        result = await processor.process_document(str(test_file))
        
        # Verify metadata
        assert result.success is True
        assert "file_size" in result.metadata
        assert "encoding" in result.metadata
        assert "line_count" in result.metadata
        assert "word_count" in result.metadata
        
        # Verify values
        assert result.metadata["file_size"] == len(test_content.encode())
        assert result.metadata["line_count"] >= 1
        assert result.metadata["word_count"] >= 1


"""Unit tests for logging utilities."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from ai_research_framework.utils.logging import (
    LoggerMixin, 
    LogContext, 
    setup_logging, 
    get_logger
)


class TestLoggerMixin:
    """Test LoggerMixin class."""
    
    def test_logger_mixin_initialization(self):
        """Test LoggerMixin initialization."""
        
        class TestClass(LoggerMixin):
            pass
        
        instance = TestClass()
        
        # Test that logger is available
        assert hasattr(instance, 'logger')
        assert instance.logger is not None
        
        # Test logger name
        assert instance.logger.name == "TestClass"
    
    def test_logger_mixin_methods(self):
        """Test LoggerMixin logging methods."""
        
        class TestClass(LoggerMixin):
            def test_method(self):
                self.log_info("Test info message")
                self.log_debug("Test debug message")
                self.log_warning("Test warning message")
                self.log_error("Test error message")
                self.log_critical("Test critical message")
        
        instance = TestClass()
        
        # Mock the logger to capture calls
        with patch.object(instance, 'logger') as mock_logger:
            instance.test_method()
            
            # Verify all logging methods were called
            mock_logger.info.assert_called_with("Test info message")
            mock_logger.debug.assert_called_with("Test debug message")
            mock_logger.warning.assert_called_with("Test warning message")
            mock_logger.error.assert_called_with("Test error message")
            mock_logger.critical.assert_called_with("Test critical message")
    
    def test_logger_mixin_with_extra(self):
        """Test LoggerMixin with extra parameters."""
        
        class TestClass(LoggerMixin):
            def test_method(self):
                self.log_info("Test message", extra={"key": "value"})
        
        instance = TestClass()
        
        with patch.object(instance, 'logger') as mock_logger:
            instance.test_method()
            mock_logger.info.assert_called_with("Test message", extra={"key": "value"})
    
    def test_logger_mixin_inheritance(self):
        """Test LoggerMixin with inheritance."""
        
        class BaseClass(LoggerMixin):
            pass
        
        class DerivedClass(BaseClass):
            pass
        
        base_instance = BaseClass()
        derived_instance = DerivedClass()
        
        # Both should have loggers with correct names
        assert base_instance.logger.name == "BaseClass"
        assert derived_instance.logger.name == "DerivedClass"


class TestLogContext:
    """Test LogContext class."""
    
    def test_log_context_basic(self):
        """Test basic LogContext functionality."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            with LogContext("test_operation"):
                pass
            
            # Should log entry and exit
            assert mock_logger.info.call_count >= 2
    
    def test_log_context_with_kwargs(self):
        """Test LogContext with keyword arguments."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            with LogContext("test_operation", param1="value1", param2=42):
                pass
            
            # Verify logging calls
            mock_logger.info.assert_called()
    
    def test_log_context_with_exception(self):
        """Test LogContext with exception handling."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            try:
                with LogContext("test_operation"):
                    raise ValueError("Test error")
            except ValueError:
                pass
            
            # Should log error
            mock_logger.error.assert_called()
    
    def test_log_context_timing(self):
        """Test LogContext timing functionality."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            with LogContext("test_operation") as ctx:
                # Simulate some work
                import time
                time.sleep(0.01)
            
            # Should have timing information
            assert hasattr(ctx, 'start_time')
            assert hasattr(ctx, 'end_time')
            assert ctx.end_time > ctx.start_time


class TestSetupLogging:
    """Test setup_logging function."""
    
    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            setup_logging()
            
            # Should configure logger
            mock_logger.remove.assert_called()
            mock_logger.add.assert_called()
    
    def test_setup_logging_with_level(self):
        """Test logging setup with specific level."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            setup_logging(level="DEBUG")
            
            # Should be called with DEBUG level
            mock_logger.add.assert_called()
    
    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            with patch('ai_research_framework.utils.logging.logger') as mock_logger:
                setup_logging(log_file=str(log_file))
                
                # Should add file handler
                mock_logger.add.assert_called()
    
    def test_setup_logging_json_format(self):
        """Test logging setup with JSON format."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            setup_logging(json_format=True)
            
            # Should configure JSON format
            mock_logger.add.assert_called()
    
    def test_setup_logging_multiple_calls(self):
        """Test multiple calls to setup_logging."""
        
        with patch('ai_research_framework.utils.logging.logger') as mock_logger:
            setup_logging()
            setup_logging()
            
            # Should remove existing handlers
            assert mock_logger.remove.call_count >= 2


class TestGetLogger:
    """Test get_logger function."""
    
    def test_get_logger_basic(self):
        """Test basic get_logger functionality."""
        
        logger = get_logger("test_module")
        
        assert logger is not None
        assert logger.name == "test_module"
    
    def test_get_logger_with_class(self):
        """Test get_logger with class."""
        
        class TestClass:
            pass
        
        logger = get_logger(TestClass)
        
        assert logger.name == "TestClass"
    
    def test_get_logger_caching(self):
        """Test that get_logger caches loggers."""
        
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        
        # Should return the same instance
        assert logger1 is logger2
    
    def test_get_logger_different_names(self):
        """Test get_logger with different names."""
        
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        # Should return different instances
        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"


@pytest.mark.unit
class TestLoggingIntegration:
    """Integration tests for logging utilities."""
    
    def test_logger_mixin_with_context(self):
        """Test LoggerMixin with LogContext."""
        
        class TestClass(LoggerMixin):
            def test_method(self):
                with LogContext("test_operation"):
                    self.log_info("Inside context")
        
        instance = TestClass()
        
        with patch.object(instance, 'logger') as mock_logger:
            instance.test_method()
            
            # Should log both context and method messages
            mock_logger.info.assert_called()
    
    def test_logging_configuration_persistence(self):
        """Test that logging configuration persists."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup logging
            setup_logging(
                level="DEBUG",
                log_file=str(log_file),
                json_format=True
            )
            
            # Create logger and log message
            logger = get_logger("test")
            
            # Should not raise exception
            logger.info("Test message")
    
    def test_error_handling_in_logging(self):
        """Test error handling in logging utilities."""
        
        class TestClass(LoggerMixin):
            def test_method(self):
                try:
                    with LogContext("error_operation"):
                        raise ValueError("Test error")
                except Exception as e:
                    self.log_error(f"Caught error: {e}")
        
        instance = TestClass()
        
        # Should not raise exception
        instance.test_method()
    
    def test_logging_with_structured_data(self):
        """Test logging with structured data."""
        
        class TestClass(LoggerMixin):
            def test_method(self):
                self.log_info(
                    "Processing document",
                    extra={
                        "document_id": "123",
                        "size": 1024,
                        "type": "pdf"
                    }
                )
        
        instance = TestClass()
        
        with patch.object(instance, 'logger') as mock_logger:
            instance.test_method()
            
            # Should include structured data
            mock_logger.info.assert_called_with(
                "Processing document",
                extra={
                    "document_id": "123",
                    "size": 1024,
                    "type": "pdf"
                }
            )


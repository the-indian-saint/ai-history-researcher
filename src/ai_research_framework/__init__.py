"""
AI Research Framework for Ancient Indian History

A comprehensive AI-powered research framework designed specifically for creating
YouTube content about ancient Indian history. This system automates source discovery,
document processing, and content analysis to help researchers and content creators
access lesser-known historical information.
"""

__version__ = "0.1.0"
__author__ = "Rohan Matkar"
__email__ = "rohan.matkar489@gmail.com"
__license__ = "MIT"

from .api.main import app
from .config import settings

__all__ = ["app", "settings", "__version__"]


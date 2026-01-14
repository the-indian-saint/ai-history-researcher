"""Web scraping and data collection module."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import aiohttp
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScrapingResult:
    """Result of web scraping operation."""
    success: bool
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    links: List[str]
    error_message: Optional[str] = None
    processing_time: Optional[float] = None


@dataclass
class ArchiveResult:
    """Result of Internet Archive search."""
    success: bool
    items: List[Dict[str, Any]]
    total_found: int
    error_message: Optional[str] = None


class WebScraper:
    """Web scraper for historical sources."""
    
    def __init__(self):
        self.visited_urls = set()
    
    async def scrape_url(self, url: str) -> ScrapingResult:
        """Scrape content from a single URL."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers={"User-Agent": settings.user_agent},
                    timeout=settings.scraping_timeout
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove scripts and styles
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text = soup.get_text(separator='\n')
                    
                    # Extract lines and drop blank ones
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    title = soup.title.string if soup.title else url
                    
                    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ScrapingResult(
                success=True,
                url=url,
                title=title or "No Title",
                content=text[:10000],  # Limit content length
                metadata={"source": "web_scraper", "length": len(text)},
                links=links[:50],  # Limit links
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Error scraping {url}: {e}")
            
            return ScrapingResult(
                success=False,
                url=url,
                title="",
                content="",
                metadata={},
                links=[],
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def search_academic_sources(
        self, 
        query: str, 
        max_results: int = 10
    ) -> List[ScrapingResult]:
        """Search academic sources for historical content using DuckDuckGo."""
        results = []
        
        try:
            # Use run_in_executor for synchronous DDGS
            loop = asyncio.get_event_loop()
            
            def run_search():
                with DDGS() as ddgs:
                    # Enforce academic focus in query
                    search_query = f"{query} academic history research filetype:html"
                    return list(ddgs.text(search_query, max_results=max_results))
            
            search_results = await loop.run_in_executor(None, run_search)
            
            for res in search_results:
                result = ScrapingResult(
                    success=True,
                    url=res['href'],
                    title=res['title'],
                    content=res['body'],
                    metadata={"source": "duckduckgo_academic", "query": query},
                    links=[]
                )
                results.append(result)
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return results


class InternetArchiveCollector:
    """Collector for Internet Archive historical documents."""
    
    def __init__(self):
        self.base_url = "https://archive.org/advancedsearch.php"
    
    async def search_documents(
        self, 
        query: str, 
        max_results: int = 20
    ) -> ArchiveResult:
        """Search Internet Archive for historical documents."""
        try:
            params = {
                'q': f'{query} AND mediatype:(texts) AND year:[-2000 TO 1900]',
                'fl[]': 'identifier,title,creator,date,description,subject,language',
                'sort[]': 'downloads desc',
                'rows': max_results,
                'page': 1,
                'output': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        raise Exception(f"Internet Archive API returned {response.status}")
                    
                    data = await response.json()
                    docs = data.get('response', {}).get('docs', [])
                    
                    items = []
                    for doc in docs:
                        identifier = doc.get('identifier')
                        items.append({
                            'identifier': identifier,
                            'title': doc.get('title'),
                            'creator': doc.get('creator'),
                            'date': doc.get('date'),
                            'description': doc.get('description', 'No description'),
                            'subject': doc.get('subject'),
                            'language': doc.get('language'),
                            'url': f"https://archive.org/details/{identifier}",
                            'download_url': f"https://archive.org/download/{identifier}/{identifier}.pdf"
                        })
                    
                    return ArchiveResult(
                        success=True,
                        items=items,
                        total_found=data.get('response', {}).get('numFound', 0)
                    )
            
        except Exception as e:
            logger.error(f"Internet Archive search failed: {e}")
            return ArchiveResult(
                success=False,
                items=[],
                total_found=0,
                error_message=str(e)
            )


# Global instances
web_scraper = WebScraper()
archive_collector = InternetArchiveCollector()


# Convenience functions
async def scrape_historical_sources(urls: List[str]) -> List[ScrapingResult]:
    """Scrape multiple historical sources."""
    tasks = [web_scraper.scrape_url(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)


async def search_academic_content(query: str, max_results: int = 10) -> List[ScrapingResult]:
    """Search academic sources for historical content."""
    return await web_scraper.search_academic_sources(query, max_results)


async def search_internet_archive(query: str, max_results: int = 20) -> ArchiveResult:
    """Search Internet Archive for historical documents."""
    return await archive_collector.search_documents(query, max_results=max_results)


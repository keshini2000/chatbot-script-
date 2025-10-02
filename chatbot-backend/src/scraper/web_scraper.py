import requests
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict, Optional
from dataclasses import dataclass
import logging
try:
    from ..config.settings import settings
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedPage:
    url: str
    title: str
    content: str
    meta_description: str
    headers: List[str]
    links: List[str]
    timestamp: str

class CoreDNAScraper:
    def __init__(self, base_url: str = None, max_pages: int = None, delay: float = None):
        self.base_url = base_url or settings.coredna_base_url
        self.max_pages = max_pages or settings.max_pages
        self.delay = delay or settings.scraping_delay
        self.visited_urls: Set[str] = set()
        self.to_visit: Set[str] = set()
        self.scraped_data: List[ScrapedPage] = []
        self.session = requests.Session()
        
        # Common headers to appear more like a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to Core DNA domain and should be scraped"""
        parsed = urlparse(url)
        base_domain = urlparse(self.base_url).netloc
        
        # Must be same domain
        if parsed.netloc != base_domain:
            return False
            
        # Skip non-content URLs
        skip_patterns = [
            '/cdn-cgi/', '/wp-admin/', '/wp-content/', '/wp-includes/',
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js',
            '.xml', '.txt', '.zip', '/feed/', '/rss/', '/atom/',
            '#', 'mailto:', 'tel:', 'javascript:', '/search?'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
                
        return True

    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a single page"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check if it's HTML content
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url}")
                return None
                
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all valid links from a page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if not href:
                continue
                
            # Convert relative URLs to absolute
            absolute_url = urljoin(current_url, href)
            
            # Remove fragment
            if '#' in absolute_url:
                absolute_url = absolute_url.split('#')[0]
                
            if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                links.append(absolute_url)
                
        return links

    def extract_content(self, soup: BeautifulSoup, url: str) -> ScrapedPage:
        """Extract structured content from a page"""
        # Title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""
        
        # Meta description
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '').strip()
            
        # Headers
        headers = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            header_text = tag.get_text().strip()
            if header_text:
                headers.append(header_text)
        
        # Main content - remove navigation, footer, scripts, etc.
        for element in soup(['nav', 'footer', 'script', 'style', 'aside', 'header']):
            element.decompose()
            
        # Try to find main content areas
        main_content = ""
        content_selectors = [
            'main', 'article', '.content', '.main-content', 
            '#content', '#main', '.post-content', '.entry-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(separator=' ', strip=True)
                break
                
        # Fallback to body content if no main content found
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator=' ', strip=True)
        
        # Extract links for further crawling
        page_links = self.extract_links(soup, url)
        
        return ScrapedPage(
            url=url,
            title=title,
            content=main_content,
            meta_description=meta_desc,
            headers=headers,
            links=page_links,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    def discover_initial_urls(self) -> Set[str]:
        """Discover initial URLs to start crawling"""
        initial_urls = set()
        
        # Start with homepage
        initial_urls.add(self.base_url)
        
        # Try common pages
        common_pages = [
            '/sitemap.xml', '/sitemap', '/blog', '/blogs', '/news',
            '/products', '/services', '/solutions', '/about',
            '/contact', '/pricing', '/platform', '/resources'
        ]
        
        for page in common_pages:
            initial_urls.add(urljoin(self.base_url, page))
            
        # Get sitemap URLs if available
        try:
            sitemap_url = urljoin(self.base_url, '/sitemap.xml')
            response = self.session.get(sitemap_url, timeout=5)
            if response.status_code == 200:
                sitemap_soup = BeautifulSoup(response.content, 'xml')
                for loc in sitemap_soup.find_all('loc'):
                    url = loc.get_text().strip()
                    if self.is_valid_url(url):
                        initial_urls.add(url)
                        
        except Exception as e:
            logger.info(f"No sitemap found or error reading sitemap: {e}")
            
        return initial_urls

    def scrape_all_pages(self) -> List[ScrapedPage]:
        """Main scraping method to crawl all Core DNA pages"""
        logger.info(f"Starting to scrape Core DNA website. Max pages: {self.max_pages}")
        
        # Discover initial URLs
        self.to_visit = self.discover_initial_urls()
        
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            current_url = self.to_visit.pop()
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            
            # Get page content
            soup = self.get_page_content(current_url)
            if not soup:
                continue
                
            # Extract structured content
            scraped_page = self.extract_content(soup, current_url)
            self.scraped_data.append(scraped_page)
            
            # Add newly discovered links to queue
            for link in scraped_page.links:
                if link not in self.visited_urls:
                    self.to_visit.add(link)
            
            logger.info(f"Scraped: {current_url} | Total: {len(self.scraped_data)} | Queue: {len(self.to_visit)}")
            
            # Rate limiting
            time.sleep(self.delay)
            
        logger.info(f"Scraping completed. Total pages scraped: {len(self.scraped_data)}")
        return self.scraped_data

    def save_to_json(self, output_path: str = None) -> str:
        """Save scraped data to JSON file"""
        if not output_path:
            output_path = os.path.join("data", "raw", "coredna_scraped_data.json")
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert dataclasses to dict for JSON serialization
        data_dict = []
        for page in self.scraped_data:
            data_dict.append({
                'url': page.url,
                'title': page.title,
                'content': page.content,
                'meta_description': page.meta_description,
                'headers': page.headers,
                'links': page.links,
                'timestamp': page.timestamp
            })
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Scraped data saved to: {output_path}")
        return output_path

if __name__ == "__main__":
    scraper = CoreDNAScraper()
    pages = scraper.scrape_all_pages()
    scraper.save_to_json()
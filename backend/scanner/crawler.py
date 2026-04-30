import asyncio
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, start_url: str, max_depth: int = 1):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()
        self.endpoints = set()
        self.domain = urlparse(start_url).netloc

    async def crawl(self) -> list[str]:
        self.visited.clear()
        self.endpoints.clear()
        
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            await self._crawl_recursive(client, self.start_url, 0)
            
        return list(self.endpoints)

    async def _crawl_recursive(self, client: httpx.AsyncClient, current_url: str, current_depth: int):
        if current_depth > self.max_depth or current_url in self.visited:
            return
            
        self.visited.add(current_url)
        self.endpoints.add(current_url)
        
        try:
            response = await client.get(current_url)
            if response.status_code != 200:
                return
                
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(current_url, href)
                if urlparse(full_url).netloc == self.domain:
                    links.append(full_url)
                    
            tasks = [self._crawl_recursive(client, link, current_depth + 1) for link in set(links)]
            if tasks:
                await asyncio.gather(*tasks)
                
        except Exception:
            pass

import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import re
import os
from pathlib import Path


class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.timeout = 30
    
    def scrape_url(self, url: str, max_length: int = 8000) -> Dict[str, Any]:
        """Scrape content from a URL"""
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme:
                return {"error": "Invalid URL. Please include http:// or https://"}
            
            if parsed.scheme not in ['http', 'https']:
                return {"error": "Only HTTP and HTTPS URLs are supported"}
            
            # Make request
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            
            # Get title
            title = soup.title.string if soup.title else ""
            
            # Get main content
            main_content = soup.get_text(separator='\n', strip=True)
            
            # Truncate if too long
            if len(main_content) > max_length:
                main_content = main_content[:max_length] + "\n... (truncated)"
            
            # Extract links
            links = []
            for a in soup.find_all('a', href=True)[:20]:
                href = a['href']
                if href.startswith('http'):
                    links.append(href)
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True)[:10]:
                src = img['src']
                if src.startswith('http'):
                    images.append(src)
            
            return {
                "url": url,
                "title": title,
                "content": main_content,
                "links": links,
                "images": images,
                "status_code": response.status_code,
                "content_length": len(main_content)
            }
            
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. The page took too long to load."}
        except requests.exceptions.ConnectionError:
            return {"error": "Could not connect to the URL. Please check if it's valid."}
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP Error: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
    
    def get_summary(self, url: str) -> str:
        """Get a quick summary of a URL"""
        result = self.scrape_url(url, max_length=1000)
        
        if "error" in result:
            return f"❌ {result['error']}"
        
        summary = f"📄 {result.get('title', 'No title')}\n"
        summary += f"🔗 {result['url']}\n\n"
        summary += f"📝 Content Preview:\n{result['content'][:500]}...\n"
        
        if result.get('links'):
            summary += f"\n🔗 Found {len(result['links'])} links"
        
        return summary
    
    def extract_text_only(self, url: str) -> str:
        """Extract only text content from URL"""
        result = self.scrape_url(url)
        
        if "error" in result:
            return f"❌ {result['error']}"
        
        return result.get("content", "No content found")


class LocalFileReader:
    def __init__(self):
        self.allowed_extensions = {
            '.txt', '.md', '.json', '.yaml', '.yml', '.xml', '.csv',
            '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
            '.go', '.rs', '.swift', '.kt', '.rb', '.php', '.html',
            '.css', '.scss', '.sql', '.sh', '.bash', '.zsh', '.log',
            '.env', '.gitignore', '.dockerignore', 'README', 'LICENSE'
        }
    
    def read_file(self, file_path: str, max_lines: int = 500) -> Dict[str, Any]:
        """Read content from a local file"""
        try:
            path = Path(file_path).expanduser().resolve()
            
            # Security check
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not path.is_file():
                return {"error": f"Not a file: {file_path}"}
            
            # Check extension
            ext = path.suffix.lower()
            if ext not in self.allowed_extensions and path.name not in self.allowed_extensions:
                return {"error": f"File type not allowed: {ext}"}
            
            # Read content
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            content = ''.join(lines[:max_lines])
            
            return {
                "file": str(path),
                "content": content,
                "lines": total_lines,
                "truncated": total_lines > max_lines,
                "size": path.stat().st_size
            }
            
        except PermissionError:
            return {"error": "Permission denied to read this file"}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}
    
    def read_multiple_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Read multiple files"""
        results = {}
        
        for path in file_paths:
            result = self.read_file(path)
            results[path] = result
        
        return results
    
    def get_file_tree(self, directory: str, max_depth: int = 2) -> Dict[str, Any]:
        """Get a tree view of a directory"""
        try:
            path = Path(directory).expanduser().resolve()
            
            if not path.exists():
                return {"error": f"Directory not found: {directory}"}
            
            if not path.is_dir():
                return {"error": f"Not a directory: {directory}"}
            
            tree = self._build_tree(path, 0, max_depth)
            
            return {
                "directory": str(path),
                "tree": tree
            }
            
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
    
    def _build_tree(self, path: Path, depth: int, max_depth: int) -> List[Dict]:
        """Helper to build directory tree"""
        if depth > max_depth:
            return []
        
        items = []
        
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                item_info = {
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file"
                }
                
                if item.is_dir() and depth < max_depth:
                    item_info["children"] = self._build_tree(item, depth + 1, max_depth)
                
                items.append(item_info)
                
        except PermissionError:
            pass
        
        return items

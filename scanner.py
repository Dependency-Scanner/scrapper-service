"""
Dependency Scanner - Extracts dependency names and versions from web pages
"""

import re
import json
import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import sys
import os
import logging
import traceback
from datetime import datetime

DEFAULT_URL = "https://github.com/expressjs/express/blob/master/package.json"
LOG_FILE = "scanner.log"

def setup_logger(log_file: str = LOG_FILE, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration with both file and console handlers
    
    Args:
        log_file: Path to log file
        log_level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('DependencyScanner')
    logger.setLevel(log_level)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class DependencyScanner:
    """Scans web pages for dependency declarations using regex patterns"""
    
    def __init__(self, timeout: int = 30, logger: Optional[logging.Logger] = None):
        """
        Initialize the dependency scanner
        
        Args:
            timeout: Request timeout in seconds
            logger: Optional logger instance (creates new one if not provided)
        """
        self.timeout = timeout
        self.logger = logger or setup_logger()
        self.session = requests.Session()
        
        try:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        except Exception as e:
            self.logger.error(f"Failed to set session headers: {e}", exc_info=True)
            raise
        
        self.patterns = {
            'npm': [
                r'["\']([a-zA-Z0-9@/_-]+)["\']\s*:\s*["\']([^"\']+)["\']',
                r'["\']([a-zA-Z0-9@/_-]+)["\']\s*:\s*["\'][\^~]?([\d.]+[^"\']*)["\']',
                r'npm\s+install\s+([a-zA-Z0-9@/_-]+)(?:@([^\s]+))?',
                r'yarn\s+add\s+([a-zA-Z0-9@/_-]+)(?:@([^\s]+))?',
                r'(?:dependencies|devDependencies)\s*:\s*\{([^}]+)\}',
            ],
            'pip': [
                r'^([a-zA-Z0-9_-]+)\s*==\s*([^\s#]+)',
                r'^([a-zA-Z0-9_-]+)\s*>=\s*([^\s#]+)',
                r'^([a-zA-Z0-9_-]+)\s*~=\s*([^\s#]+)',
                r'pip\s+install\s+(?:--[^\s]+\s+)*(?:[^\s]+\s+)*[^\n]+',
                r'conda\s+create\s+[^\n]+',
                r'conda\s+install\s+[^\n]+',
                r'install_requires\s*=\s*\[(.*?)\]',
                r'([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']',
            ],
            'maven': [
                r'<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?<version>([^<]+)</version>',
                r'<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?<version>([^<]+)</version>.*?</dependency>',
            ],
            'gradle': [
                r"implementation\s+['\"]([^:]+):([^:]+):([^'\"]+)['\"]",
                r"compile\s+['\"]([^:]+):([^:]+):([^'\"]+)['\"]",
            ],
            'go': [
                r'require\s+([^\s]+)\s+([^\s]+)',
                r'go\s+get\s+([^\s@]+)(?:@([^\s]+))?',
            ],
            'ruby': [
                r"gem\s+['\"]([^'\"]+)['\"][\s,]*['\"]([^'\"]+)['\"]",
                r"gem\s+['\"]([^'\"]+)['\"][\s,]*['\"]~>\s*([^'\"]+)['\"]",
            ],
            'composer': [
                r'["\']([^"\']+)["\']\s*:\s*["\']([^"\']+)["\']',
                r'composer\s+require\s+([^\s]+)(?:\s+([^\s]+))?',
            ],
            'generic': []
        }
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch the content of a web page
        
        Args:
            url: URL to fetch
            
        Returns:
            Page content as string, or None if failed
        """
        if not url or not isinstance(url, str):
            self.logger.error(f"Invalid URL provided: {url}")
            return None
        
        original_url = url
        if 'github.com' in url and '/blob/' in url:
            try:
                raw_url = url.replace('/blob/', '/').replace('github.com', 'raw.githubusercontent.com')
                self.logger.info(f"Converting GitHub blob URL to raw URL: {raw_url}")
                url = raw_url
            except Exception as e:
                self.logger.warning(f"Failed to convert GitHub URL: {e}, using original URL")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            self.logger.info(f"Making request to: {url}")
            response = self.session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = len(response.text)
            self.logger.debug(f"Response received: Content-Type={content_type}, Length={content_length}")
            
            if 'json' in content_type:
                self.logger.info("Content type detected as JSON")
                return response.text
            elif 'html' in content_type or 'text' in content_type:
                self.logger.info("Content type detected as HTML/Text")
                return response.text
            else:
                self.logger.warning(f"Unsupported content type: {content_type}, attempting to parse anyway")
                return response.text
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout for URL {url} (timeout={self.timeout}s)")
            return None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 'Unknown'
            if status_code == 403:
                self.logger.error(f"Access forbidden (403) for URL {url}. The page may require authentication or block scrapers.")
            elif status_code == 404:
                self.logger.error(f"Page not found (404) for URL {url}")
            elif status_code == 429:
                self.logger.error(f"Rate limited (429) for URL {url}. Too many requests.")
            else:
                self.logger.error(f"HTTP error {status_code} fetching URL {url}: {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error fetching URL {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request exception fetching URL {url}: {e}", exc_info=True)
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching URL {url}: {e}", exc_info=True)
            return None
    
    def extract_text_from_html(self, html: str) -> str:
        """
        Extract text content from HTML, preserving code blocks
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text content
        """
        if not html or not isinstance(html, str):
            self.logger.warning("Invalid HTML content provided to extract_text_from_html")
            return ""
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            code_blocks = []
            
            try:
                github_code = soup.find('div', class_=re.compile(r'blob-wrapper|highlight', re.I))
                if github_code:
                    code_elem = github_code.find('code') or github_code.find('pre')
                    if code_elem:
                        code_blocks.append(code_elem.get_text())
            except Exception as e:
                self.logger.debug(f"Error extracting GitHub code blocks: {e}")
            
            try:
                for code in soup.find_all(['code', 'pre', 'textarea']):
                    code_text = code.get_text()
                    if code_text.strip() and code_text not in code_blocks:
                        code_blocks.append(code_text)
            except Exception as e:
                self.logger.debug(f"Error extracting code blocks: {e}")
            
            try:
                for div in soup.find_all('div', class_=re.compile(r'highlight|code|source|syntax|hljs', re.I)):
                    div_text = div.get_text()
                    if div_text.strip() and div_text not in code_blocks:
                        code_blocks.append(div_text)
            except Exception as e:
                self.logger.debug(f"Error extracting div code blocks: {e}")
            
            try:
                for pre in soup.find_all('pre', class_=re.compile(r'code|source', re.I)):
                    pre_text = pre.get_text()
                    if pre_text.strip() and pre_text not in code_blocks:
                        code_blocks.append(pre_text)
            except Exception as e:
                self.logger.debug(f"Error extracting pre code blocks: {e}")
            
            text_content = soup.get_text()
            combined = '\n'.join(code_blocks) + '\n' + text_content
            self.logger.debug(f"Extracted {len(code_blocks)} code blocks, total text length: {len(combined)}")
            return combined
            
        except Exception as e:
            self.logger.error(f"Error extracting text from HTML: {e}", exc_info=True)
            return html
    
    def extract_dependencies(self, content: str, url: str = "") -> List[Dict]:
        """
        Extract dependencies from page content using regex patterns
        
        Args:
            content: Page content to scan
            url: Source URL (for context)
            
        Returns:
            List of dependency dictionaries
        """
        if not content or not isinstance(content, str):
            self.logger.warning("Invalid content provided to extract_dependencies")
            return []
        
        dependencies = []
        seen = set()
        
        try:
            for dep_type, patterns in self.patterns.items():
                if not patterns:
                    continue
                    
                for pattern in patterns:
                    try:
                        matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                    except re.error as e:
                        self.logger.error(f"Invalid regex pattern for {dep_type}: {pattern}. Error: {e}")
                        continue
                    
                    for match in matches:
                        try:
                            groups = match.groups()
                            
                            if dep_type == 'npm':
                                if len(groups) >= 2:
                                    if len(groups) == 1 and '{' in match.group(0):
                                        deps_block = groups[0]
                                        nested_matches = re.finditer(
                                            r'["\']([a-zA-Z0-9@/_-]+)["\']\s*:\s*["\']([^"\']+)["\']',
                                            deps_block
                                        )
                                        for nested_match in nested_matches:
                                            name = nested_match.group(1).strip()
                                            version = nested_match.group(2).strip()
                                            if name and version and (name, version, dep_type) not in seen:
                                                seen.add((name, version, dep_type))
                                                dependencies.append({
                                                    'name': name,
                                                    'version': version,
                                                    'type': dep_type,
                                                    'line': nested_match.group(0)
                                                })
                                    else:
                                        name = groups[0].strip() if groups[0] else ""
                                        version = groups[1].strip() if len(groups) > 1 and groups[1] else ""
                                        if name and version and (name, version, dep_type) not in seen:
                                            seen.add((name, version, dep_type))
                                            dependencies.append({
                                                'name': name,
                                                'version': version,
                                                'type': dep_type,
                                                'line': match.group(0)
                                            })
                            
                            elif dep_type == 'pip':
                                match_text = match.group(0)
                                
                                if len(match_text) > 500 or 'http' in match_text.lower() or '://' in match_text:
                                    continue
                                
                                if match_text.strip().startswith('conda'):
                                    command_type = 'conda'
                                else:
                                    command_type = 'pip'
                                
                                full_command = match_text
                                match_start = match.start()
                                remaining_content = content[match_start:]
                                lines = remaining_content.split('\n')
                                if len(lines) > 1:
                                    first_line = lines[0].rstrip()
                                    if first_line.endswith('\\'):
                                        full_command = first_line[:-1].strip()
                                        for line in lines[1:10]:
                                            line = line.strip()
                                            if not line:
                                                break
                                            if line.endswith('\\'):
                                                full_command += ' ' + line[:-1].strip()
                                            else:
                                                full_command += ' ' + line
                                                break
                                
                                packages = self.extract_packages_from_command(full_command, command_type)
                                
                                invalid_names = {
                                    'CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'CC', 'CXX', 'export', 'echo', 
                                    'sudo', 'apt-get', 'yum', 'pkg', 'brew', 'conda', 'pip', 'python',
                                    'python3', 'pip3', 'make', 'git', 'cd', 'source', 'activate', 'install',
                                    'build', 'test', 'run', 'check', 'version', 'name', 'wheel',
                                    'http', 'https', 'ftp', 'git', 'ssh',
                                    'checkout', 'platform', 'command', 'once', 'environment', 'env',
                                    'sklearn-env', 'sklearn-dev', 'Please', 'refer', 'Developer', 'Guide',
                                    'Useful', 'pytest', 'Note', 'Building', 'Installing',
                                    'editable', 'verbose', 'config', 'settings', 'no-build', 'isolation',
                                    'extra-index', 'pre', 'simple', 'scikit-learn', 'n', 'c', 'for',
                                    'with', 'from', 'the', 'and', 'or', 'to', 'a', 'an', 'is', 'are',
                                    'pypi', 'anaconda', 'org', 'scientific', 'nightly', 'wheels',
                                    'index', 'registry', 'channel', 'forge', 'meta', 'package',
                                    'conda-forge', 'It', 'python'
                                }
                                
                                for package in packages:
                                    name = package.strip()
                                    if (name and 
                                        name.lower() not in [n.lower() for n in invalid_names] and
                                        len(name) >= 2 and len(name) < 50 and
                                        re.match(r'^[a-zA-Z0-9_-]+$', name) and
                                        not name.startswith('$') and
                                        not name.startswith('-') and
                                        not name.startswith('http') and
                                        not name.startswith('/') and
                                        not name.startswith('.') and
                                        (name, '', dep_type) not in seen):
                                        seen.add((name, '', dep_type))
                                        dependencies.append({
                                            'name': name,
                                            'version': '',
                                            'type': dep_type,
                                            'line': full_command[:200]
                                        })
                            
                            elif dep_type == 'maven':
                                if len(groups) >= 3:
                                    group_id = groups[0].strip()
                                    artifact_id = groups[1].strip()
                                    version = groups[2].strip()
                                    name = f"{group_id}:{artifact_id}"
                                    if name and version and (name, version, dep_type) not in seen:
                                        seen.add((name, version, dep_type))
                                        dependencies.append({
                                            'name': name,
                                            'version': version,
                                            'type': dep_type,
                                            'line': match.group(0)
                                        })
                            
                            elif dep_type == 'gradle':
                                if len(groups) >= 3:
                                    if len(groups) == 4:
                                        group_id = groups[1].strip()
                                        artifact_id = groups[2].strip()
                                        version = groups[3].strip()
                                    else:
                                        group_id = groups[0].strip()
                                        artifact_id = groups[1].strip()
                                        version = groups[2].strip()
                                    name = f"{group_id}:{artifact_id}"
                                    if name and version and (name, version, dep_type) not in seen:
                                        seen.add((name, version, dep_type))
                                        dependencies.append({
                                            'name': name,
                                            'version': version,
                                            'type': dep_type,
                                            'line': match.group(0)
                                        })
                            
                            elif dep_type == 'go':
                                if len(groups) >= 2:
                                    name = groups[0].strip() if groups[0] else ""
                                    version = groups[1].strip() if groups[1] else ""
                                    if name and version and (name, version, dep_type) not in seen:
                                        seen.add((name, version, dep_type))
                                        dependencies.append({
                                            'name': name,
                                            'version': version,
                                            'type': dep_type,
                                            'line': match.group(0)
                                        })
                            
                            elif dep_type in ['ruby', 'composer']:
                                if len(groups) >= 2:
                                    name = groups[0].strip() if groups[0] else ""
                                    version = groups[1].strip() if groups[1] else ""
                                    if name and version and (name, version, dep_type) not in seen:
                                        seen.add((name, version, dep_type))
                                        dependencies.append({
                                            'name': name,
                                            'version': version,
                                            'type': dep_type,
                                            'line': match.group(0)
                                        })
                            
                            elif dep_type == 'generic':
                                if len(groups) >= 2:
                                    name = groups[0].strip() if groups[0] else ""
                                    version = groups[1].strip() if groups[1] else ""
                                    
                                    invalid_names = {'CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'export', 'echo', 'sudo', 
                                                   'apt-get', 'yum', 'pkg', 'brew', 'conda', 'pip', 'python',
                                                   'python3', 'pip3', 'make', 'git', 'cd', 'source', 'activate',
                                                   'install', 'build', 'test', 'run', 'check', 'version', 'name',
                                                   'wheel', 'CC', 'CXX', 'PATH', 'HOME', 'USER', 'SKLEARN',
                                                   'Please', 'refer', 'Developer', 'Guide', 'Useful', 'pytest'}
                                    
                                    line_text = match.group(0)
                                    if (name and version and 
                                        len(name) > 2 and len(name) < 50 and
                                        len(version) < 50 and
                                        len(line_text) < 500 and
                                        name not in invalid_names and
                                        not name.startswith('$') and
                                        not version.startswith('$') and
                                        not name.startswith('http') and
                                        not name.startswith('/') and
                                        not '\n' in name and
                                        not '\n' in version and
                                        re.match(r'^[a-zA-Z0-9_-]+$', name) and
                                        re.match(r'[\d.]+', version) and
                                        (name, version, dep_type) not in seen):
                                        seen.add((name, version, dep_type))
                                        dependencies.append({
                                            'name': name,
                                            'version': version,
                                            'type': dep_type,
                                            'line': match.group(0)[:200]
                                        })
                        except Exception as e:
                            self.logger.debug(f"Error processing match for {dep_type} pattern: {e}")
                            continue
                        
        except Exception as e:
            self.logger.error(f"Error in extract_dependencies: {e}", exc_info=True)
        
        self.logger.info(f"Extracted {len(dependencies)} dependencies from content (URL: {url})")
        return dependencies
    
    def extract_packages_from_command(self, command_text: str, command_type: str = 'pip') -> List[str]:
        """
        Extract package names from pip/conda install commands
        
        Args:
            command_text: The command string (e.g., "pip install numpy scipy")
            command_type: 'pip' or 'conda'
            
        Returns:
            List of package names
        """
        if not command_text or not isinstance(command_text, str):
            self.logger.warning(f"Invalid command_text provided: {command_text}")
            return []
        
        packages = []
        
        try:
            if command_type == 'conda':
                parts = command_text.split()
                skip_next = False
                
                for i, part in enumerate(parts):
                    if skip_next:
                        skip_next = False
                        continue
                    
                    if part in ['-n', '--name', '-c', '--channel', '--file', '-f', '-y', '--yes']:
                        skip_next = True
                        continue
                    
                    if part in ['conda', 'create', 'install', 'update', 'env']:
                        continue
                    
                    if i > 0 and parts[i-1] in ['-c', '--channel']:
                        continue
                    
                    if i > 0 and parts[i-1] in ['-n', '--name']:
                        continue
                    
                    if part.startswith('-'):
                        continue
                    
                    if '://' in part or part.startswith('http'):
                        continue
                    
                    if part and re.match(r'^[a-zA-Z0-9_-]+$', part):
                        packages.append(part)
            
            elif command_type == 'pip':
                parts = command_text.split()
                skip_next = False
                
                for i, part in enumerate(parts):
                    if skip_next:
                        skip_next = False
                        continue
                    
                    if part.startswith('--') or part.startswith('-'):
                        if part in ['--index-url', '--extra-index-url', '--find-links', '-f']:
                            skip_next = True
                        continue
                    
                    if part in ['pip', 'install', 'uninstall', 'upgrade']:
                        continue
                    
                    if '://' in part or part.startswith('http'):
                        continue
                    
                    if part.startswith('-'):
                        continue
                    
                    if part and re.match(r'^[a-zA-Z0-9_-]+$', part):
                        packages.append(part)
            else:
                self.logger.warning(f"Unknown command_type: {command_type}")
                
        except Exception as e:
            self.logger.error(f"Error extracting packages from command: {e}", exc_info=True)
        
        return packages
    
    def parse_json_dependencies(self, json_content: str, url: str = "") -> List[Dict]:
        """
        Parse dependencies from JSON content (package.json, composer.json, etc.)
        
        Args:
            json_content: JSON string content
            url: Source URL
            
        Returns:
            List of dependency dictionaries
        """
        if not json_content or not isinstance(json_content, str):
            self.logger.warning("Invalid JSON content provided")
            return []
        
        dependencies = []
        
        try:
            data = json.loads(json_content)
            
            if isinstance(data, dict):
                for dep_type_key in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies', 'overrides']:
                    if dep_type_key in data and isinstance(data[dep_type_key], dict):
                        try:
                            for name, version in data[dep_type_key].items():
                                if name and version:
                                    dependencies.append({
                                        'name': str(name),
                                        'version': str(version),
                                        'type': 'npm',
                                        'line': f'"{name}": "{version}"'
                                    })
                        except Exception as e:
                            self.logger.warning(f"Error parsing {dep_type_key}: {e}")
                
                if 'require' in data and isinstance(data['require'], dict):
                    try:
                        for name, version in data['require'].items():
                            if name and version:
                                dependencies.append({
                                    'name': str(name),
                                    'version': str(version),
                                    'type': 'composer',
                                    'line': f'"{name}": "{version}"'
                                })
                    except Exception as e:
                        self.logger.warning(f"Error parsing require: {e}")
                
                if 'require-dev' in data and isinstance(data['require-dev'], dict):
                    try:
                        for name, version in data['require-dev'].items():
                            if name and version:
                                dependencies.append({
                                    'name': str(name),
                                    'version': str(version),
                                    'type': 'composer',
                                    'line': f'"{name}": "{version}"'
                                })
                    except Exception as e:
                        self.logger.warning(f"Error parsing require-dev: {e}")
            else:
                self.logger.debug("JSON data is not a dictionary")
        
        except json.JSONDecodeError as e:
            self.logger.debug(f"JSON decode error: {e}")
        except Exception as e:
            self.logger.error(f"Error parsing JSON dependencies: {e}", exc_info=True)
        
        return dependencies
    
    def scan(self, url: str) -> Dict:
        """
        Scan a URL for dependencies
        
        Args:
            url: URL to scan
            
        Returns:
            Dictionary with scan results in JSON format
        """
        if not url or not isinstance(url, str):
            self.logger.error("Invalid URL provided to scan method")
            return {
                'url': str(url) if url else '',
                'error': 'Invalid URL provided',
                'dependencies': [],
                'summary': {'total': 0, 'by_type': {}}
            }
        
        self.logger.info(f"Starting scan for URL: {url}")
        
        try:
            content = self.fetch_page(url)
            if not content:
                self.logger.error(f"Failed to fetch content from URL: {url}")
                return {
                    'url': url,
                    'error': 'Failed to fetch page',
                    'dependencies': [],
                    'summary': {'total': 0, 'by_type': {}}
                }
            
            self.logger.info(f"Content fetched successfully, length: {len(content)} characters")
            dependencies = []
            
            try:
                json.loads(content)
                self.logger.info("Detected raw JSON content")
                dependencies = self.parse_json_dependencies(content, url)
                self.logger.info(f"Found {len(dependencies)} dependencies from JSON parsing")
            except (json.JSONDecodeError, ValueError):
                self.logger.info("Content is not raw JSON, parsing as HTML")
                try:
                    text_content = self.extract_text_from_html(content)
                    soup = BeautifulSoup(content, 'lxml')
                    
                    github_code_containers = [
                        soup.find('div', class_=re.compile(r'blob-wrapper', re.I)),
                        soup.find('table', class_=re.compile(r'highlight', re.I)),
                        soup.find('div', {'data-tagsearch-path': True}),
                    ]
                    
                    for container in github_code_containers:
                        if container:
                            try:
                                code_elem = container.find('code') or container.find('pre')
                                if code_elem:
                                    code_text = code_elem.get_text().strip()
                                    if code_text and len(code_text) > 20:
                                        try:
                                            json.loads(code_text)
                                            json_deps = self.parse_json_dependencies(code_text, url)
                                            if json_deps:
                                                dependencies.extend(json_deps)
                                                self.logger.info(f"Found {len(json_deps)} dependencies from GitHub code container")
                                                break
                                        except (json.JSONDecodeError, ValueError):
                                            pass
                            except Exception as e:
                                self.logger.debug(f"Error processing GitHub container: {e}")
                                continue
                    
                    if not dependencies:
                        try:
                            code_blocks = soup.find_all(['pre', 'code'])
                            for code_block in code_blocks:
                                try:
                                    code_text = code_block.get_text().strip()
                                    if not code_text or len(code_text) < 20:
                                        continue
                                    json.loads(code_text)
                                    json_deps = self.parse_json_dependencies(code_text, url)
                                    if json_deps:
                                        dependencies.extend(json_deps)
                                        self.logger.info(f"Found {len(json_deps)} dependencies from code block")
                                        break
                                except (json.JSONDecodeError, ValueError):
                                    continue
                                except Exception as e:
                                    self.logger.debug(f"Error processing code block: {e}")
                                    continue
                        except Exception as e:
                            self.logger.warning(f"Error processing code blocks: {e}")
                    
                    if not dependencies:
                        try:
                            json_scripts = soup.find_all('script', type=re.compile(r'application/json', re.I))
                            for script in json_scripts:
                                try:
                                    if script.string:
                                        json.loads(script.string)
                                        json_deps = self.parse_json_dependencies(script.string, url)
                                        if json_deps:
                                            dependencies.extend(json_deps)
                                            self.logger.info(f"Found {len(json_deps)} dependencies from script tag")
                                            break
                                except (json.JSONDecodeError, ValueError, AttributeError):
                                    continue
                                except Exception as e:
                                    self.logger.debug(f"Error processing script tag: {e}")
                                    continue
                        except Exception as e:
                            self.logger.warning(f"Error processing script tags: {e}")
                    
                    if not dependencies:
                        self.logger.info("No JSON found in HTML, trying regex patterns")
                        regex_deps = self.extract_dependencies(text_content, url)
                        dependencies.extend(regex_deps)
                        self.logger.info(f"Found {len(regex_deps)} dependencies from regex patterns")
                        
                except Exception as e:
                    self.logger.error(f"Error parsing HTML content: {e}", exc_info=True)
                    return {
                        'url': url,
                        'error': f'Error parsing content: {str(e)}',
                        'dependencies': [],
                        'summary': {'total': 0, 'by_type': {}}
                    }
            
            summary = {
                'total': len(dependencies),
                'by_type': {}
            }
            
            for dep in dependencies:
                try:
                    dep_type = dep.get('type', 'unknown')
                    summary['by_type'][dep_type] = summary['by_type'].get(dep_type, 0) + 1
                except Exception as e:
                    self.logger.debug(f"Error processing dependency for summary: {e}")
                    continue
            
            self.logger.info(f"Scan completed. Total dependencies found: {summary['total']}")
            return {
                'url': url,
                'dependencies': dependencies,
                'summary': summary
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in scan method: {e}", exc_info=True)
            return {
                'url': url,
                'error': f'Unexpected error: {str(e)}',
                'dependencies': [],
                'summary': {'total': 0, 'by_type': {}}
            }


def save_to_csv(results: Dict, filename: str = None, logger: Optional[logging.Logger] = None):
    """
    Save scan results to a CSV file
    
    Args:
        results: Dictionary containing scan results
        filename: Output CSV filename (optional)
        logger: Optional logger instance
    """
    if logger is None:
        logger = setup_logger()
    
    if filename is None:
        filename = "dependencies_output.csv"
    
    dependencies = results.get('dependencies', [])
    
    if not dependencies:
        logger.info("No dependencies found. CSV file not created.")
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'version', 'type', 'source_url', 'line']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for dep in dependencies:
                try:
                    writer.writerow({
                        'name': dep.get('name', ''),
                        'version': dep.get('version', ''),
                        'type': dep.get('type', ''),
                        'source_url': results.get('url', ''),
                        'line': dep.get('line', '').replace('\n', ' ').replace('\r', ' ')[:200]
                    })
                except Exception as e:
                    logger.warning(f"Error writing dependency row: {e}")
                    continue
        
        logger.info(f"Results saved to CSV file: {filename} (Total dependencies: {len(dependencies)})")
        
    except PermissionError:
        logger.error(f"Permission denied: Cannot write to CSV file {filename}")
    except OSError as e:
        logger.error(f"OS error saving to CSV file {filename}: {e}")
    except Exception as e:
        logger.error(f"Error saving to CSV file {filename}: {e}", exc_info=True)


def main():
    """Command-line interface for the dependency scanner"""
    logger = setup_logger()
    
    try:
        csv_filename = None
        
        if len(sys.argv) >= 2:
            url = sys.argv[1]
            if len(sys.argv) >= 3:
                csv_filename = sys.argv[2]
        elif DEFAULT_URL:
            url = DEFAULT_URL
            logger.info(f"Using default URL from configuration: {url}")
        else:
            logger.error("No URL provided and no default URL set")
            print("Usage: python scanner.py <url> [csv_filename]")
            print("Example: python scanner.py https://github.com/user/repo/wiki/Dependencies")
            print("Example: python scanner.py <url> output.csv")
            print("\nOr set DEFAULT_URL variable in scanner.py")
            sys.exit(1)
        
        logger.info("=" * 60)
        logger.info("Dependency Scanner Started")
        logger.info(f"URL: {url}")
        logger.info("=" * 60)
        
        scanner = DependencyScanner(logger=logger)
        results = scanner.scan(url)
        
        if 'error' in results:
            logger.error(f"Scan failed with error: {results['error']}")
        else:
            logger.info("Scan completed successfully")
        
        try:
            output = json.dumps(results, indent=2)
            print(output)
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Error serializing results to JSON: {e}", exc_info=True)
            print(json.dumps({
                'url': url,
                'error': 'Failed to serialize results',
                'dependencies': [],
                'summary': {'total': 0, 'by_type': {}}
            }, indent=2))
        
        if csv_filename:
            try:
                save_to_csv(results, csv_filename, logger)
            except Exception as e:
                logger.error(f"Error saving to CSV: {e}", exc_info=True)
        
    except KeyboardInterrupt:
        logger.warning("Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("=" * 60)
        logger.info("Dependency Scanner Finished")
        logger.info("=" * 60)


if __name__ == '__main__':
    main()


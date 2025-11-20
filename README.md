# Dependency Scanner

A comprehensive web scraping tool that extracts dependency names and versions from web pages (GitHub docs, wikis, Confluence, documentation sites) using regex patterns and intelligent parsing. The scanner supports multiple package managers and provides detailed error handling and logging.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Requirements](#requirements)
- [Installation](#installation)
- [Implementation Details](#implementation-details)
- [Workflow](#workflow)
- [Usage](#usage)
- [Error Handling & Logging](#error-handling--logging)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## Overview

The Dependency Scanner is designed to automatically extract dependency information from various web sources including:
- GitHub repositories (blob pages, raw files)
- Documentation websites
- Wiki pages
- Confluence pages
- Package manager configuration files

It supports multiple package managers and formats:
- **npm/yarn**: package.json, npm install commands
- **Python**: requirements.txt, setup.py, pyproject.toml, pip/conda commands
- **Maven**: pom.xml
- **Gradle**: build.gradle
- **Go**: go.mod, go get commands
- **Ruby**: Gemfile
- **Composer**: composer.json

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python Version**: Python 3.8 or higher (Python 3.12 recommended)
- **Internet Connection**: Required for fetching web pages
- **Disk Space**: ~50 MB for installation and logs

### Software Prerequisites

1. **Python Installation**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure Python is added to system PATH (see [ADD_PYTHON_TO_PATH.md](ADD_PYTHON_TO_PATH.md))
   - Verify installation: `python --version` or `py --version`

2. **pip Package Manager**
   - Usually included with Python
   - Verify: `pip --version` or `py -m pip --version`

3. **Text Editor or IDE** (optional)
   - VS Code, PyCharm, or any text editor for viewing code

## Requirements

### Python Package Dependencies

The project requires the following Python packages (specified in `requirements.txt`):

```
requests==2.31.0          # HTTP library for web requests
beautifulsoup4==4.12.2    # HTML parsing and extraction
lxml==4.9.3               # XML/HTML parser (backend for BeautifulSoup)
urllib3==2.0.7             # URL handling library
```

### System Dependencies

- **lxml** requires C libraries (usually pre-installed on most systems)
- **Windows**: May need Microsoft Visual C++ Redistributable
- **Linux/macOS**: Usually works out of the box

### Optional Dependencies

- **Virtual Environment**: Recommended for isolated installations
- **Git**: For cloning the repository (if applicable)

## Installation

### Method 1: Automated Setup (Recommended)

#### Windows
```bash
setup.bat
```

#### macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Installation

#### Step 1: Navigate to Project Directory
```bash
cd "C:\Users\priya\OneDrive\Desktop\Scalable project"
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
# If Python is in PATH
pip install -r requirements.txt

# If Python is not in PATH (Windows)
py -m pip install -r requirements.txt

# Or use full path
"C:\Users\priya\AppData\Local\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```

#### Step 4: Verify Installation
```bash
python check_requirements.py
```

For detailed installation instructions, see [INSTALL.md](INSTALL.md)

## Implementation Details

### Architecture

The Dependency Scanner follows a modular architecture:

```
┌─────────────────────────────────────────┐
│         DependencyScanner Class          │
├─────────────────────────────────────────┤
│  - fetch_page()      : HTTP requests    │
│  - extract_text_from_html() : HTML parse│
│  - extract_dependencies() : Regex match │
│  - parse_json_dependencies() : JSON     │
│  - extract_packages_from_command() : CLI │
│  - scan()            : Main orchestrator│
└─────────────────────────────────────────┘
```

### Core Components

#### 1. **DependencyScanner Class**

The main class that orchestrates the scanning process:

- **Initialization**: Sets up HTTP session, configures timeout, initializes regex patterns
- **Pattern Matching**: Predefined regex patterns for each package manager
- **Error Handling**: Comprehensive try-except blocks with logging
- **Content Parsing**: Multi-stage parsing (JSON → HTML → Regex)

#### 2. **Pattern System**

Regex patterns organized by package manager type:

```python
patterns = {
    'npm': [...],      # package.json, npm install
    'pip': [...],      # requirements.txt, pip install, conda
    'maven': [...],    # pom.xml
    'gradle': [...],   # build.gradle
    'go': [...],       # go.mod
    'ruby': [...],     # Gemfile
    'composer': [...]  # composer.json
}
```

#### 3. **Multi-Stage Parsing Strategy**

The scanner uses a priority-based parsing approach:

1. **Priority 1**: Raw JSON files (package.json, composer.json)
2. **Priority 2**: JSON embedded in HTML (GitHub blob pages)
3. **Priority 3**: JSON in script tags
4. **Priority 4**: Regex pattern matching on extracted text

#### 4. **GitHub URL Conversion**

Automatically converts GitHub blob URLs to raw URLs:
```
github.com/user/repo/blob/branch/file.json
→
raw.githubusercontent.com/user/repo/branch/file.json
```

#### 5. **Command Parsing**

Intelligent extraction from CLI commands:
- Skips flags (`-n`, `-c`, `--index-url`, etc.)
- Handles multi-line commands (backslash continuation)
- Filters invalid package names
- Extracts all packages from a single command

#### 6. **Error Handling System**

- **Network Errors**: Timeout, connection errors, HTTP errors
- **Parsing Errors**: JSON decode errors, HTML parsing errors
- **Validation**: Input validation for URLs, content, parameters
- **Graceful Degradation**: Continues processing when possible

#### 7. **Logging System**

- **File Logging**: All events logged to `scanner.log`
- **Console Logging**: Errors and warnings to stderr
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Structured Format**: Timestamps, log levels, detailed messages

### Key Features

1. **Intelligent Content Detection**
   - Automatically detects JSON vs HTML content
   - Prioritizes structured data over text parsing
   - Handles various content types gracefully

2. **False Positive Filtering**
   - Blacklist of invalid package names
   - Length and format validation
   - URL and path detection
   - Command word filtering

3. **Multi-format Support**
   - Handles raw files, HTML pages, documentation
   - Supports GitHub, Confluence, generic wikis
   - Works with code blocks and inline code

4. **Robust Error Recovery**
   - Continues processing after errors
   - Logs all errors for debugging
   - Returns partial results when possible

## Workflow

### High-Level Workflow

```
┌─────────────┐
│  User Input │ (URL)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  fetch_page()   │ → HTTP Request
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Content Type    │ → JSON? HTML? Text?
│   Detection     │
└──────┬──────────┘
       │
       ├─── JSON ────► parse_json_dependencies()
       │
       ├─── HTML ────► extract_text_from_html()
       │                │
       │                ▼
       │         ┌──────────────────┐
       │         │ Extract JSON     │ → Try JSON from code blocks
       │         │ from HTML        │
       │         └────────┬─────────┘
       │                  │
       │                  ▼
       └──────────► extract_dependencies() → Regex matching
                          │
                          ▼
                   ┌──────────────┐
                   │  Filter &    │ → Remove false positives
                   │  Validate    │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Generate    │ → Summary statistics
                   │  Results     │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  JSON Output │
                   └──────────────┘
```

### Detailed Step-by-Step Process

1. **URL Input**
   - User provides URL via command line or DEFAULT_URL variable
   - URL validation and normalization

2. **GitHub URL Conversion**
   - Detects GitHub blob URLs
   - Converts to raw GitHub URLs for better access

3. **HTTP Request**
   - Sets appropriate headers (User-Agent, Accept)
   - Handles redirects
   - Manages timeouts (default: 30 seconds)
   - Error handling for network issues

4. **Content Type Detection**
   - Checks Content-Type header
   - Determines parsing strategy

5. **JSON Parsing (Priority 1)**
   - Attempts to parse as raw JSON
   - Extracts dependencies from:
     - `dependencies`, `devDependencies` (npm)
     - `require`, `require-dev` (composer)

6. **HTML Parsing (Priority 2)**
   - Parses HTML with BeautifulSoup
   - Extracts code blocks from:
     - GitHub blob containers
     - `<pre>`, `<code>` tags
     - Highlighted code divs
   - Attempts JSON extraction from code blocks

7. **Regex Pattern Matching (Priority 3)**
   - Applies regex patterns for each package manager
   - Processes all matches
   - Extracts package names and versions

8. **Command Parsing**
   - For pip/conda commands:
     - Parses command structure
     - Skips flags and options
     - Extracts package names
     - Handles multi-line commands

9. **Filtering & Validation**
   - Removes invalid package names
   - Validates format and length
   - Filters URLs, paths, commands
   - Deduplicates dependencies

10. **Result Generation**
    - Creates dependency list
    - Generates summary statistics
    - Formats JSON output

11. **Logging**
    - Logs all operations
    - Records errors with tracebacks
    - Saves to `scanner.log`

## Usage

### Command Line Interface

#### Basic Usage
```bash
python scanner.py <url>
```

#### With Default URL
Set `DEFAULT_URL` in `scanner.py`:
```python
DEFAULT_URL = "https://github.com/user/repo/blob/master/package.json"
```

Then run:
```bash
python scanner.py
```

#### Windows (Python not in PATH)
```bash
"C:\Users\priya\AppData\Local\Programs\Python\Python312\python.exe" scanner.py <url>
```

### Python API

```python
from scanner import DependencyScanner
import json

# Initialize scanner
scanner = DependencyScanner(timeout=30)

# Scan a URL
results = scanner.scan("https://github.com/user/repo/blob/master/package.json")

# Access results
print(f"Found {results['summary']['total']} dependencies")
for dep in results['dependencies']:
    print(f"{dep['name']} ({dep['type']}): {dep['version']}")

# Output as JSON
print(json.dumps(results, indent=2))
```

### Example Scripts

#### Run Example Script
```bash
python example.py
```

#### Run Test Suite
```bash
python test_error_handling.py
```

### Output Format

```json
{
  "url": "https://example.com/page",
  "dependencies": [
    {
      "name": "express",
      "version": "^4.18.0",
      "type": "npm",
      "line": "\"express\": \"^4.18.0\""
    },
    {
      "name": "numpy",
      "version": "",
      "type": "pip",
      "line": "pip install numpy scipy"
    }
  ],
  "summary": {
    "total": 2,
    "by_type": {
      "npm": 1,
      "pip": 1
    }
  }
}
```

## Error Handling & Logging

### Error Types Handled

1. **Network Errors**
   - Connection timeouts
   - Connection refused
   - DNS resolution failures
   - SSL certificate errors

2. **HTTP Errors**
   - 404 Not Found
   - 403 Forbidden
   - 429 Rate Limited
   - 500 Internal Server Error

3. **Parsing Errors**
   - JSON decode errors
   - HTML parsing errors
   - Invalid regex patterns
   - Malformed content

4. **Validation Errors**
   - Invalid URLs
   - None values
   - Empty content
   - Type mismatches

### Logging System

#### Log File Location
```
C:\Users\priya\OneDrive\Desktop\Scalable project\scanner.log
```

#### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about operations
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages with full tracebacks

#### Log Format
```
2025-11-20 09:58:43 - DependencyScanner - INFO - Fetching URL: https://...
2025-11-20 09:58:44 - DependencyScanner - ERROR - Request timeout for URL...
```

#### Viewing Logs
```bash
# Windows
type scanner.log
notepad scanner.log

# macOS/Linux
cat scanner.log
less scanner.log
```

### Error Response Format

When errors occur, the scanner returns:
```json
{
  "url": "https://example.com/page",
  "error": "Failed to fetch page",
  "dependencies": [],
  "summary": {
    "total": 0,
    "by_type": {}
  }
}
```

## Testing

### Running Test Suite

```bash
python test_error_handling.py
```

### Test Coverage

The test suite includes:
- Invalid URL handling
- HTTP error codes (404, 403, 500, 429)
- Request timeouts
- Invalid JSON content
- Empty content handling
- Invalid regex patterns
- Malformed HTML
- JSON parsing errors
- Command parsing edge cases
- None value handling
- Large content handling
- Special characters
- Valid URLs (success cases)
- Log file creation

### Test Log File
```
C:\Users\priya\OneDrive\Desktop\Scalable project\test_scanner.log
```

For detailed test documentation, see [TEST_CASES.md](TEST_CASES.md)

## Project Structure

```
Scalable project/
│
├── scanner.py                 # Main scanner module
├── example.py                 # Example usage script
├── scan_url.py                # CLI utility
├── test_error_handling.py     # Test suite
├── check_requirements.py      # Dependency checker
│
├── requirements.txt           # Python dependencies
├── setup.bat                  # Windows setup script
├── setup.sh                   # macOS/Linux setup script
│
├── README.md                  # This file
├── INSTALL.md                 # Installation guide
├── REQUIREMENTS.md            # System requirements
├── TEST_CASES.md              # Test documentation
├── ADD_PYTHON_TO_PATH.md      # PATH configuration guide
│
├── scanner.log                # Main log file
└── test_scanner.log           # Test log file
```

## Troubleshooting

### Common Issues

#### 1. Python Not Found
**Error**: `python is not recognized`

**Solution**: Use full path or add Python to PATH
```bash
"C:\Users\priya\AppData\Local\Programs\Python\Python312\python.exe" scanner.py
```

#### 2. Module Not Found
**Error**: `ModuleNotFoundError: No module named 'requests'`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Connection Timeout
**Error**: `Request timeout for URL`

**Solution**: 
- Check internet connection
- Increase timeout: `DependencyScanner(timeout=60)`
- Verify URL is accessible

#### 4. 403 Forbidden
**Error**: `Access forbidden (403)`

**Solution**:
- URL may require authentication
- Site may block scrapers
- Try accessing URL in browser first

#### 5. No Dependencies Found
**Issue**: Scanner returns empty dependencies

**Solution**:
- Check if page contains dependency information
- Verify URL is correct
- Check log file for parsing errors
- Try different URL format (raw vs blob for GitHub)

#### 6. Log File Permission Error
**Error**: `Permission denied: Cannot write to log file`

**Solution**:
- Check file permissions
- Ensure directory is writable
- Close log file if open in another program

### Getting Help

1. **Check Log Files**: Review `scanner.log` for detailed error messages
2. **Run Tests**: Execute `test_error_handling.py` to verify setup
3. **Verify Installation**: Run `check_requirements.py`
4. **Review Documentation**: See [INSTALL.md](INSTALL.md) and [REQUIREMENTS.md](REQUIREMENTS.md)

## License

This project is provided as-is for educational and development purposes.

## Contributing

When contributing:
1. Follow existing code style
2. Add error handling for new features
3. Update documentation
4. Add test cases for new functionality
5. Check logs for debugging information

---

**Last Updated**: November 2024
**Version**: 1.0.0

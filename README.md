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
- [Project Structure](#project-structure)

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

## Usage

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

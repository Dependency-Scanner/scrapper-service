# Project Requirements

## System Requirements

### Operating System
- **Windows 10/11** (or macOS, Linux)
- Any modern operating system that supports Python

### Python
- **Python 3.7 or higher** (Python 3.8+ recommended)
- Python must be installed and accessible from command line

### Internet Connection
- Active internet connection required (to scrape web pages)

---

## Python Package Dependencies

The following Python packages are required and listed in `requirements.txt`:

### Core Dependencies

1. **requests (2.31.0)**
   - Purpose: HTTP library for fetching web pages
   - Used for: Making GET requests to URLs
   - Install: `pip install requests==2.31.0`

2. **beautifulsoup4 (4.12.2)**
   - Purpose: HTML/XML parser
   - Used for: Parsing HTML content from web pages
   - Install: `pip install beautifulsoup4==4.12.2`

3. **lxml (4.9.3)**
   - Purpose: Fast XML and HTML parser
   - Used for: Backend parser for BeautifulSoup
   - Install: `pip install lxml==4.9.3`

4. **urllib3 (2.0.7)**
   - Purpose: HTTP client library
   - Used for: Underlying HTTP functionality (dependency of requests)
   - Install: `pip install urllib3==2.0.7`

---

## Standard Library Modules (Built-in, No Installation Needed)

These are included with Python and don't need to be installed:

- `re` - Regular expressions
- `json` - JSON encoding/decoding
- `sys` - System-specific parameters
- `typing` - Type hints
- `urllib.parse` - URL parsing utilities

---

## Installation Summary

### Quick Install (All packages at once)
```bash
pip install -r requirements.txt
```

### Individual Package Installation
```bash
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
pip install urllib3==2.0.7
```

### Using Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

---

## Verification

After installation, verify all packages are installed:

```bash
pip list
```

You should see:
- requests
- beautifulsoup4
- lxml
- urllib3

Or run the requirements checker:
```bash
python check_requirements.py
```

---

## Minimum System Resources

- **RAM**: 100 MB minimum (for running the scanner)
- **Disk Space**: ~50 MB (for Python packages)
- **Network**: Internet connection for web scraping

---

## Optional but Recommended

- **Git**: For version control (if you want to track changes)
- **Code Editor**: VS Code, PyCharm, or any text editor
- **Virtual Environment**: Isolated Python environment (recommended)

---

## Troubleshooting

### If Python is not found:
- Download Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

### If pip is not found:
- Try: `python -m pip install -r requirements.txt`
- Or: `py -m pip install -r requirements.txt`

### If installation fails:
- Make sure you have internet connection
- Try upgrading pip: `python -m pip install --upgrade pip`
- Check Python version: `python --version` (should be 3.7+)


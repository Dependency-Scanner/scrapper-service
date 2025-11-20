# Installation Guide

## Prerequisites

Make sure you have Python 3.7 or higher installed on your system.

To check if Python is installed, run:
```bash
python --version
```
or on Windows:
```bash
py --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

## Installation Steps

### Option 1: Using Virtual Environment (Recommended)

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
   or on Windows:
   ```bash
   py -m venv venv
   ```

2. **Activate the virtual environment:**
   
   On Windows (PowerShell):
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
   
   On Windows (Command Prompt):
   ```bash
   venv\Scripts\activate.bat
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Direct Installation (Without Virtual Environment)

Simply run:
```bash
pip install -r requirements.txt
```

or on Windows:
```bash
py -m pip install -r requirements.txt
```

## Verify Installation

After installation, verify that all packages are installed correctly:

```bash
pip list
```

You should see:
- requests
- beautifulsoup4
- lxml
- urllib3

## Test the Installation

Run a quick test:
```bash
python scanner.py https://example.com
```

If it runs without errors, you're all set!

## Troubleshooting

### If you get "pip is not recognized"
Try using:
```bash
python -m pip install -r requirements.txt
```
or
```bash
py -m pip install -r requirements.txt
```

### If you get permission errors
On Windows, you might need to run PowerShell as Administrator, or use:
```bash
pip install --user -r requirements.txt
```


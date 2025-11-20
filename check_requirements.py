"""
System Requirements Checker for Dependency Scanner
"""

import sys
import subprocess
import os

def check_python():
    """Check Python installation"""
    print("=" * 60)
    print("CHECKING PYTHON INSTALLATION")
    print("=" * 60)
    
    python_version = sys.version_info
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} is installed")
    print(f"  Location: {sys.executable}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("  ⚠ WARNING: Python 3.7 or higher is recommended")
        return False
    else:
        print("  ✓ Python version is compatible")
        return True

def check_pip():
    """Check pip installation"""
    print("\n" + "=" * 60)
    print("CHECKING PIP INSTALLATION")
    print("=" * 60)
    
    try:
        import pip
        pip_version = pip.__version__
        print(f"✓ pip {pip_version} is installed")
        return True
    except ImportError:
        print("✗ pip is not installed")
        print("  Try running: python -m ensurepip --upgrade")
        return False

def check_packages():
    """Check required packages"""
    print("\n" + "=" * 60)
    print("CHECKING REQUIRED PACKAGES")
    print("=" * 60)
    
    required_packages = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'lxml': 'lxml',
        'urllib3': 'urllib3'
    }
    
    missing_packages = []
    installed_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            installed_packages.append(package_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            missing_packages.append(package_name)
            print(f"✗ {package_name} is NOT installed")
    
    return missing_packages, installed_packages

def check_network():
    """Check network connectivity"""
    print("\n" + "=" * 60)
    print("CHECKING NETWORK CONNECTIVITY")
    print("=" * 60)
    
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✓ Internet connection is available")
        return True
    except Exception as e:
        print(f"✗ Cannot connect to internet: {e}")
        print("  Note: You need internet to scrape web pages")
        return False

def main():
    print("\n" + "=" * 60)
    print("DEPENDENCY SCANNER - SYSTEM REQUIREMENTS CHECK")
    print("=" * 60 + "\n")
    
    all_ok = True
    
    # Check Python
    if not check_python():
        all_ok = False
    
    # Check pip
    if not check_pip():
        all_ok = False
    
    # Check packages
    missing, installed = check_packages()
    if missing:
        all_ok = False
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("  Install them with: pip install -r requirements.txt")
    
    # Check network
    check_network()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all_ok:
        print("✓ All requirements are met! You can run the project.")
    else:
        print("✗ Some requirements are missing.")
        print("\nTo fix:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Or run the setup script: setup.bat")
    
    print("=" * 60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during check: {e}")
        sys.exit(1)


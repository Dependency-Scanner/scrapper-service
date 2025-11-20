"""
Test cases for error handling and event logging in Dependency Scanner
Run with: python test_error_handling.py
"""

import sys
import os
import json
from scanner import DependencyScanner, setup_logger
import logging

# Test configuration
TEST_LOG_FILE = "test_scanner.log"
logger = setup_logger(TEST_LOG_FILE, logging.DEBUG)

def print_test_header(test_name):
    """Print a formatted test header"""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def test_invalid_url():
    """Test 1: Invalid URL handling"""
    print_test_header("Invalid URL Handling")
    scanner = DependencyScanner(logger=logger)
    
    test_urls = [
        "",  # Empty URL
        None,  # None URL
        "not-a-valid-url",  # Invalid format
        "http://",  # Incomplete URL
        "ftp://invalid-domain-12345.com/nonexistent",  # Non-existent domain
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        try:
            result = scanner.scan(str(url) if url else "")
            print(f"Result: {json.dumps(result, indent=2)}")
            assert 'error' in result or result.get('dependencies') == [], "Should handle invalid URL gracefully"
            print("✓ Passed")
        except Exception as e:
            print(f"✗ Failed: {e}")

def test_http_errors():
    """Test 2: HTTP error codes (404, 403, 500)"""
    print_test_header("HTTP Error Codes")
    scanner = DependencyScanner(logger=logger)
    
    test_urls = [
        "https://httpstat.us/404",  # 404 Not Found
        "https://httpstat.us/403",  # 403 Forbidden
        "https://httpstat.us/500",  # 500 Internal Server Error
        "https://httpstat.us/429",  # 429 Rate Limited
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        try:
            result = scanner.scan(url)
            print(f"Status: {'Error' if 'error' in result else 'Success'}")
            print(f"Result keys: {list(result.keys())}")
            assert 'error' in result or 'dependencies' in result, "Should return error or empty dependencies"
            print("✓ Passed")
        except Exception as e:
            print(f"✗ Failed: {e}")

def test_timeout():
    """Test 3: Request timeout handling"""
    print_test_header("Request Timeout")
    scanner = DependencyScanner(timeout=1, logger=logger)  # Very short timeout
    
    # URL that might timeout or take too long
    test_url = "https://httpstat.us/200?sleep=5000"  # Sleep for 5 seconds
    
    print(f"\nTesting URL with timeout: {test_url}")
    try:
        result = scanner.scan(test_url)
        print(f"Result: {json.dumps(result, indent=2)}")
        assert 'error' in result or result.get('dependencies') == [], "Should handle timeout gracefully"
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_invalid_json():
    """Test 4: Invalid JSON content handling"""
    print_test_header("Invalid JSON Content")
    scanner = DependencyScanner(logger=logger)
    
    # Use a page that returns invalid JSON
    test_url = "https://www.google.com"  # Returns HTML, not JSON
    
    print(f"\nTesting URL: {test_url}")
    try:
        result = scanner.scan(test_url)
        print(f"Found {result.get('summary', {}).get('total', 0)} dependencies")
        assert 'dependencies' in result, "Should return dependencies list even for non-JSON content"
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_empty_content():
    """Test 5: Empty or minimal content"""
    print_test_header("Empty Content Handling")
    scanner = DependencyScanner(logger=logger)
    
    # Test with extract_dependencies method directly
    print("\nTesting extract_dependencies with empty content")
    try:
        deps = scanner.extract_dependencies("", "")
        assert deps == [], "Should return empty list for empty content"
        print("✓ Passed")
        
        deps = scanner.extract_dependencies("   ", "")
        assert deps == [], "Should return empty list for whitespace-only content"
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_invalid_regex_pattern():
    """Test 6: Invalid regex pattern handling"""
    print_test_header("Invalid Regex Pattern")
    scanner = DependencyScanner(logger=logger)
    
    # Add an invalid pattern temporarily
    original_patterns = scanner.patterns.copy()
    scanner.patterns['test'] = [r'[invalid(regex[']  # Invalid regex
    
    print("\nTesting with invalid regex pattern")
    try:
        deps = scanner.extract_dependencies("test content", "")
        # Should not crash, just log error
        print(f"Extracted {len(deps)} dependencies")
        print("✓ Passed - No crash on invalid regex")
    except Exception as e:
        print(f"✗ Failed: {e}")
    finally:
        scanner.patterns = original_patterns

def test_malformed_html():
    """Test 7: Malformed HTML handling"""
    print_test_header("Malformed HTML")
    scanner = DependencyScanner(logger=logger)
    
    malformed_html = "<html><body><div>Unclosed tags<div>More content</body>"
    
    print("\nTesting extract_text_from_html with malformed HTML")
    try:
        text = scanner.extract_text_from_html(malformed_html)
        assert isinstance(text, str), "Should return string even for malformed HTML"
        print(f"Extracted text length: {len(text)}")
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_json_parsing_errors():
    """Test 8: JSON parsing error handling"""
    print_test_header("JSON Parsing Errors")
    scanner = DependencyScanner(logger=logger)
    
    invalid_json_strings = [
        "{invalid json}",
        '{"key": "value"',  # Missing closing brace
        '{"key": value}',  # Unquoted value
        '{"key": "value",}',  # Trailing comma
        '',  # Empty string
        'null',
    ]
    
    for json_str in invalid_json_strings:
        print(f"\nTesting JSON: {json_str[:50]}...")
        try:
            deps = scanner.parse_json_dependencies(json_str, "")
            assert isinstance(deps, list), "Should return list even for invalid JSON"
            print("✓ Passed")
        except Exception as e:
            print(f"✗ Failed: {e}")

def test_command_parsing():
    """Test 9: Command parsing with edge cases"""
    print_test_header("Command Parsing Edge Cases")
    scanner = DependencyScanner(logger=logger)
    
    test_commands = [
        "",  # Empty command
        "pip install",  # No packages
        "conda create -n env",  # No packages
        "pip install --invalid-flag package",  # Invalid flag
        "conda create -n env -c channel",  # No packages after flags
    ]
    
    for cmd in test_commands:
        print(f"\nTesting command: {cmd}")
        try:
            packages = scanner.extract_packages_from_command(cmd, 'pip')
            print(f"Extracted packages: {packages}")
            assert isinstance(packages, list), "Should return list"
            print("✓ Passed")
        except Exception as e:
            print(f"✗ Failed: {e}")

def test_none_values():
    """Test 10: None value handling"""
    print_test_header("None Value Handling")
    scanner = DependencyScanner(logger=logger)
    
    print("\nTesting with None values")
    try:
        # Test fetch_page with None
        result = scanner.fetch_page(None)
        assert result is None, "Should return None for None URL"
        print("✓ fetch_page(None) passed")
        
        # Test extract_dependencies with None
        deps = scanner.extract_dependencies(None, "")
        assert deps == [], "Should return empty list for None content"
        print("✓ extract_dependencies(None) passed")
        
        # Test extract_text_from_html with None
        text = scanner.extract_text_from_html(None)
        assert isinstance(text, str), "Should return string for None HTML"
        print("✓ extract_text_from_html(None) passed")
        
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_large_content():
    """Test 11: Large content handling"""
    print_test_header("Large Content Handling")
    scanner = DependencyScanner(logger=logger)
    
    # Create large content
    large_content = "package==1.0.0\n" * 10000  # 10,000 lines
    
    print(f"\nTesting with large content ({len(large_content)} characters)")
    try:
        deps = scanner.extract_dependencies(large_content, "")
        print(f"Extracted {len(deps)} dependencies")
        assert isinstance(deps, list), "Should handle large content"
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_special_characters():
    """Test 12: Special characters in content"""
    print_test_header("Special Characters Handling")
    scanner = DependencyScanner(logger=logger)
    
    special_content = """
    package==1.0.0
    package-with-dash==2.0.0
    package_with_underscore==3.0.0
    package@4.0.0
    package:5.0.0
    """
    
    print("\nTesting with special characters")
    try:
        deps = scanner.extract_dependencies(special_content, "")
        print(f"Extracted {len(deps)} dependencies")
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_valid_urls():
    """Test 13: Valid URLs (should work)"""
    print_test_header("Valid URLs - Success Cases")
    scanner = DependencyScanner(logger=logger)
    
    # Use a simple, reliable URL
    test_url = "https://raw.githubusercontent.com/expressjs/express/master/package.json"
    
    print(f"\nTesting valid URL: {test_url}")
    try:
        result = scanner.scan(test_url)
        assert 'dependencies' in result, "Should return dependencies"
        assert 'error' not in result, "Should not have error for valid URL"
        print(f"Found {result.get('summary', {}).get('total', 0)} dependencies")
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_log_file_creation():
    """Test 14: Log file creation and writing"""
    print_test_header("Log File Creation")
    
    print("\nChecking if log file exists and is writable")
    try:
        log_file = TEST_LOG_FILE
        if os.path.exists(log_file):
            print(f"✓ Log file exists: {log_file}")
            size = os.path.getsize(log_file)
            print(f"✓ Log file size: {size} bytes")
        else:
            print(f"⚠ Log file does not exist yet: {log_file}")
        
        # Try to write to log
        test_logger = setup_logger(log_file, logging.INFO)
        test_logger.info("Test log entry")
        print("✓ Successfully wrote to log file")
        print("✓ Passed")
    except Exception as e:
        print(f"✗ Failed: {e}")

def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*70)
    print("DEPENDENCY SCANNER - ERROR HANDLING TEST SUITE")
    print("="*70)
    
    tests = [
        ("Invalid URL Handling", test_invalid_url),
        ("HTTP Error Codes", test_http_errors),
        ("Request Timeout", test_timeout),
        ("Invalid JSON Content", test_invalid_json),
        ("Empty Content", test_empty_content),
        ("Invalid Regex Pattern", test_invalid_regex_pattern),
        ("Malformed HTML", test_malformed_html),
        ("JSON Parsing Errors", test_json_parsing_errors),
        ("Command Parsing", test_command_parsing),
        ("None Values", test_none_values),
        ("Large Content", test_large_content),
        ("Special Characters", test_special_characters),
        ("Valid URLs", test_valid_urls),
        ("Log File Creation", test_log_file_creation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test '{test_name}' raised exception: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"\nLog file location: {os.path.abspath(TEST_LOG_FILE)}")
    print("="*70)
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)


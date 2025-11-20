# Test Cases for Error Handling and Event Logging

This document describes all test cases for verifying error handling and event logging in the Dependency Scanner.

## Test File
Run the test suite with:
```bash
python test_error_handling.py
```

## Test Cases

### 1. Invalid URL Handling
**Purpose**: Verify the scanner handles invalid URLs gracefully without crashing.

**Test Cases**:
- Empty string URL
- None URL
- Invalid URL format
- Incomplete URL (e.g., "http://")
- Non-existent domain

**Expected Behavior**:
- Should return error in result or empty dependencies list
- Should log appropriate error messages
- Should not raise unhandled exceptions

---

### 2. HTTP Error Codes
**Purpose**: Test handling of various HTTP error responses.

**Test Cases**:
- 404 Not Found
- 403 Forbidden
- 500 Internal Server Error
- 429 Rate Limited

**Expected Behavior**:
- Should catch HTTPError exceptions
- Should return error message in result
- Should log specific error codes
- Should not crash

---

### 3. Request Timeout
**Purpose**: Verify timeout handling for slow or unresponsive servers.

**Test Cases**:
- URL that takes longer than timeout period
- Server that doesn't respond

**Expected Behavior**:
- Should catch Timeout exception
- Should return error in result
- Should log timeout error
- Should use configured timeout value

---

### 4. Invalid JSON Content
**Purpose**: Test handling of non-JSON content (HTML pages).

**Test Cases**:
- HTML page instead of JSON
- Mixed content types

**Expected Behavior**:
- Should fallback to HTML parsing
- Should attempt regex extraction
- Should return dependencies list (may be empty)
- Should log content type detection

---

### 5. Empty Content Handling
**Purpose**: Verify handling of empty or minimal content.

**Test Cases**:
- Empty string
- Whitespace-only content
- Very short content

**Expected Behavior**:
- Should return empty dependencies list
- Should not crash
- Should handle gracefully

---

### 6. Invalid Regex Pattern
**Purpose**: Test handling of malformed regex patterns.

**Test Cases**:
- Invalid regex syntax in patterns
- Pattern that causes regex error

**Expected Behavior**:
- Should catch re.error exceptions
- Should log error for invalid pattern
- Should continue with other patterns
- Should not crash

---

### 7. Malformed HTML
**Purpose**: Test HTML parsing with invalid HTML structure.

**Test Cases**:
- Unclosed tags
- Invalid HTML structure
- Missing closing tags

**Expected Behavior**:
- BeautifulSoup should handle gracefully
- Should extract text if possible
- Should not crash
- Should log warnings if needed

---

### 8. JSON Parsing Errors
**Purpose**: Test JSON parsing with invalid JSON strings.

**Test Cases**:
- Invalid JSON syntax
- Missing closing braces
- Unquoted values
- Trailing commas
- Empty strings

**Expected Behavior**:
- Should catch JSONDecodeError
- Should return empty dependencies list
- Should log debug messages
- Should not crash

---

### 9. Command Parsing Edge Cases
**Purpose**: Test package extraction from various command formats.

**Test Cases**:
- Empty commands
- Commands with no packages
- Commands with only flags
- Invalid flag combinations

**Expected Behavior**:
- Should return empty package list when appropriate
- Should skip flags correctly
- Should extract valid packages
- Should handle edge cases gracefully

---

### 10. None Value Handling
**Purpose**: Verify handling of None values in method parameters.

**Test Cases**:
- None URL
- None content
- None HTML

**Expected Behavior**:
- Should validate input
- Should return None or empty list
- Should log warnings
- Should not crash

---

### 11. Large Content Handling
**Purpose**: Test performance and memory handling with large content.

**Test Cases**:
- Very large content (10,000+ lines)
- Large dependency lists

**Expected Behavior**:
- Should process without memory issues
- Should complete in reasonable time
- Should extract dependencies correctly

---

### 12. Special Characters
**Purpose**: Test handling of special characters in package names and versions.

**Test Cases**:
- Dashes in package names
- Underscores in package names
- Special version formats
- Various separators

**Expected Behavior**:
- Should extract packages correctly
- Should handle special characters
- Should validate package names

---

### 13. Valid URLs (Success Cases)
**Purpose**: Verify normal operation with valid URLs.

**Test Cases**:
- Valid GitHub raw JSON URL
- Valid package.json URL

**Expected Behavior**:
- Should successfully fetch content
- Should parse dependencies
- Should return results without errors
- Should log success messages

---

### 14. Log File Creation
**Purpose**: Verify logging infrastructure works correctly.

**Test Cases**:
- Log file creation
- Log file writing
- Log file permissions

**Expected Behavior**:
- Should create log file if it doesn't exist
- Should write log entries
- Should handle file permissions
- Should format log entries correctly

---

## Manual Test Cases

### Test 1: Network Disconnection
1. Disconnect from internet
2. Run scanner with any URL
3. **Expected**: Should log connection error, return error in result

### Test 2: Keyboard Interrupt
1. Run scanner with a slow URL
2. Press Ctrl+C during execution
3. **Expected**: Should catch KeyboardInterrupt, log warning, exit gracefully

### Test 3: File Permission Error
1. Create scanner.log with read-only permissions
2. Run scanner
3. **Expected**: Should handle permission error gracefully

### Test 4: Concurrent Execution
1. Run multiple scanner instances simultaneously
2. **Expected**: Should handle file locking, log correctly

---

## Log File Location

The test log file is saved at:
```
C:\Users\priya\OneDrive\Desktop\Scalable project\test_scanner.log
```

The main scanner log file is at:
```
C:\Users\priya\OneDrive\Desktop\Scalable project\scanner.log
```

---

## Running Tests

### Run All Tests
```bash
python test_error_handling.py
```

### Run Specific Test
Modify the `run_all_tests()` function to run only specific tests.

### Check Logs
After running tests, check the log file:
```bash
type test_scanner.log
# or
notepad test_scanner.log
```

---

## Expected Test Results

All tests should:
- ✅ Complete without crashing
- ✅ Log appropriate messages
- ✅ Return expected data structures
- ✅ Handle errors gracefully
- ✅ Not raise unhandled exceptions

---

## Troubleshooting

If tests fail:
1. Check the log file for detailed error messages
2. Verify network connectivity for URL tests
3. Check Python version compatibility
4. Ensure all dependencies are installed
5. Verify file permissions for log file


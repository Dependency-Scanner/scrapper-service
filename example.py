"""
Example usage of the Dependency Scanner
"""

from scanner import DependencyScanner
import json

# Example URLs to test
example_urls = [
    "https://github.com/facebook/react/blob/main/package.json",
    "https://github.com/python/cpython/blob/main/requirements.txt",
    # Add your own URLs here
]

def main():
    scanner = DependencyScanner()
    
    for url in example_urls:
        print(f"\n{'='*60}")
        print(f"Scanning: {url}")
        print('='*60)
        
        results = scanner.scan(url)
        
        # Pretty print results
        print(json.dumps(results, indent=2))
        
        # Print summary
        if results.get('dependencies'):
            print(f"\nFound {results['summary']['total']} dependencies:")
            for dep_type, count in results['summary']['by_type'].items():
                print(f"  - {dep_type}: {count}")
        else:
            print("\nNo dependencies found or error occurred.")

if __name__ == '__main__':
    main()


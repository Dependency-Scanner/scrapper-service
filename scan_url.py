"""
Utility script to scan a URL and save results to a file
"""

import json
import sys
from scanner import DependencyScanner
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_url.py <url> [output_file.json]")
        print("Example: python scan_url.py https://example.com/page results.json")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Scanning: {url}")
    scanner = DependencyScanner()
    results = scanner.scan(url)
    
    # Add timestamp
    results['scan_timestamp'] = datetime.now().isoformat()
    
    # Print to console
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(json.dumps(results, indent=2))
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    
    # Print summary
    if results.get('dependencies'):
        print(f"\nSummary: Found {results['summary']['total']} dependencies")
        for dep_type, count in results['summary']['by_type'].items():
            print(f"  - {dep_type}: {count}")
    elif results.get('error'):
        print(f"\nError: {results['error']}")
    else:
        print("\nNo dependencies found.")

if __name__ == '__main__':
    main()


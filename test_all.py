#!/usr/bin/env python3
"""
Run all tests for the TickTick MCP server.
"""

import subprocess
import sys
from pathlib import Path


def run_test_file(test_file):
    """Run a single test file and return success status."""
    print(f"Running {test_file}...")
    
    try:
        result = subprocess.run(
            ["/opt/homebrew/bin/uv", "run", test_file],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file} passed")
            return True
        else:
            print(f"❌ {test_file} failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False


def main():
    """Run all test files."""
    print("Running all TickTick MCP tests...\n")
    
    test_files = [
        "test_server.py",
        "test_integration.py", 
        "test_search_tasks.py",
    ]
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
        print()  # Add spacing between tests
    
    print(f"Test results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Integration test for TickTick MCP server CLI startup.
This test verifies that the server can start up properly and catches import errors.
"""

import subprocess
import sys
import os
from pathlib import Path


def test_cli_import():
    """Test that the CLI module can be imported without errors."""
    print("Testing CLI module import...")
    
    # Test importing the CLI module directly
    try:
        import ticktick_mcp.cli
        print("✅ CLI module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ CLI module import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during CLI import: {e}")
        return False


def test_server_import():
    """Test that the server module can be imported without errors."""
    print("Testing server module import...")
    
    # Test importing the server module directly
    try:
        import ticktick_mcp.src.server
        print("✅ Server module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Server module import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during server import: {e}")
        return False


def test_cli_help_command():
    """Test that the CLI help command works without errors."""
    print("Testing CLI help command...")
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    
    try:
        # Run the CLI help command
        result = subprocess.run(
            ["/opt/homebrew/bin/uv", "run", "-m", "ticktick_mcp.cli", "run", "--help"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ CLI help command executed successfully")
            return True
        else:
            print(f"❌ CLI help command failed with exit code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI help command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running CLI help command: {e}")
        return False


def test_cli_startup_simulation():
    """Test that the CLI can start up (simulate without actually running the server)."""
    print("Testing CLI startup simulation...")
    
    project_dir = Path(__file__).parent
    
    try:
        # Try to start the server but timeout quickly to just test startup
        result = subprocess.run(
            ["/opt/homebrew/bin/uv", "run", "-m", "ticktick_mcp.cli", "run"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5  # Give it 5 seconds to start up
        )
        
        # We expect this to timeout or be killed, but not crash on import
        if "Error starting server" in result.stderr:
            print(f"❌ Server startup failed: {result.stderr}")
            return False
        elif "NameError" in result.stderr or "ImportError" in result.stderr:
            print(f"❌ Import error during startup: {result.stderr}")
            return False
        else:
            print("✅ CLI startup simulation passed (no import errors)")
            return True
            
    except subprocess.TimeoutExpired:
        print("✅ CLI startup simulation passed (timed out as expected)")
        return True
    except Exception as e:
        print(f"❌ Error during CLI startup simulation: {e}")
        return False


def test_auth_command():
    """Test that the auth command can be imported and shows help."""
    print("Testing auth command...")
    
    project_dir = Path(__file__).parent
    
    try:
        # Run the auth help command
        result = subprocess.run(
            ["/opt/homebrew/bin/uv", "run", "-m", "ticktick_mcp.cli", "auth", "--help"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Auth command executed successfully")
            return True
        else:
            print(f"❌ Auth command failed with exit code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Auth command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running auth command: {e}")
        return False


def main():
    """Run all integration tests."""
    print("Running TickTick MCP integration tests...\n")
    
    tests = [
        test_cli_import,
        test_server_import,
        test_cli_help_command,
        test_cli_startup_simulation,
        test_auth_command,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}\n")
    
    print(f"Integration test results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

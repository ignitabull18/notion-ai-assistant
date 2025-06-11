#!/usr/bin/env python3
"""
Test runner for Notion AI Assistant
"""

import os
import sys
import subprocess
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def run_test(test_file, description):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        if result.returncode == 0:
            print("✅ Test passed!")
            return True
        else:
            print(f"❌ Test failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Running Notion AI Assistant Tests")
    print("="*60)
    
    tests = [
        ("tests/test_composio.py", "Testing Composio Connection"),
        ("tests/test_all_notion_actions.py", "Testing All 20 Notion Actions"),
        ("scripts/checks/check_actions.py", "Checking Available Actions"),
    ]
    
    passed = 0
    failed = 0
    
    for test_file, description in tests:
        if Path(test_file).exists():
            if run_test(test_file, description):
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Test Summary:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Total: {passed + failed}")
    print(f"{'='*60}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
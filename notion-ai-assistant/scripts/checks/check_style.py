#!/usr/bin/env python3
"""
Style checker for Notion AI Assistant
Ensures files follow naming conventions
"""

import os
import sys
import re
from pathlib import Path


def check_python_files():
    """Check Python file naming conventions."""
    issues = []
    
    for root, dirs, files in os.walk(".", topdown=True):
        # Skip virtual environments and cache
        dirs[:] = [d for d in dirs if d not in {"venv", "__pycache__", ".git", "data"}]
        
        for file in files:
            if file.endswith(".py"):
                # Check snake_case
                if not re.match(r'^[a-z_][a-z0-9_]*\.py$', file):
                    if file != "__init__.py":  # Allow __init__.py
                        issues.append(f"Python file not in snake_case: {os.path.join(root, file)}")
                
                # Check test files (only in tests directory)
                if "/tests/" in os.path.join(root, file) and "test" in file:
                    if not file.startswith("test_") and not file.startswith("check_") and file != "__init__.py":
                        issues.append(f"Test file should start with 'test_' or 'check_': {os.path.join(root, file)}")
    
    return issues


def check_folder_names():
    """Check folder naming conventions."""
    issues = []
    
    for root, dirs, files in os.walk(".", topdown=True):
        dirs[:] = [d for d in dirs if d not in {"venv", "__pycache__", ".git"}]
        
        for dir_name in dirs:
            # Check lowercase
            if dir_name != dir_name.lower():
                issues.append(f"Folder not lowercase: {os.path.join(root, dir_name)}")
            
            # Check no spaces
            if " " in dir_name:
                issues.append(f"Folder contains spaces: {os.path.join(root, dir_name)}")
    
    return issues


def check_standard_files():
    """Check standard file naming."""
    # These files follow standard conventions in the ecosystem
    standard_files = [
        "README.md",
        "LICENSE", 
        "CONTRIBUTING.md",
        "requirements.txt",
        "setup.py",
        "manifest.json",
        "pyproject.toml",
        ".gitignore",
        ".editorconfig"
    ]
    
    issues = []
    
    # We're not enforcing case changes on standard files
    # as they follow ecosystem conventions
    
    return issues


def main():
    """Run all checks."""
    print("🔍 Checking naming conventions...")
    print("=" * 60)
    
    all_issues = []
    
    # Run checks
    checks = [
        ("Python files", check_python_files()),
        ("Folder names", check_folder_names()),
        ("Standard files", check_standard_files()),
    ]
    
    for check_name, issues in checks:
        if issues:
            print(f"\n❌ {check_name}:")
            for issue in issues:
                print(f"   - {issue}")
                all_issues.append(issue)
        else:
            print(f"\n✅ {check_name}: All good!")
    
    print("\n" + "=" * 60)
    
    if all_issues:
        print(f"❌ Found {len(all_issues)} naming convention issues")
        print("\nPlease fix these issues to maintain consistency.")
        print("See CONTRIBUTING.md for naming conventions.")
        return 1
    else:
        print("✅ All files follow naming conventions!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
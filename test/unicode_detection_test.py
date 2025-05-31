"""
Power Meter Monitor - Unicode Character Detection Test

This module provides comprehensive testing to detect and report any unicode characters
present in project files. It scans all Python files, configuration files, and 
documentation to ensure ASCII-only content.

Functions:
    check_file_for_unicode: Check a single file for unicode characters
    scan_project_for_unicode: Scan entire project for unicode characters
    run_unicode_detection_test: Main function to run unicode detection
"""

import os
import sys
# import chardet
from pathlib import Path

def check_file_for_unicode(file_path):
    """
    Check a single file for unicode characters
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        dict: Results containing unicode character information
    """
    results = {
        'file': file_path,
        'has_unicode': False,
        'unicode_chars': [],
        'encoding': None,
        'error': None
    }
    
    try:
        # First, detect the file encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            
        # Detect encoding
        encoding_result = chardet.detect(raw_data)
        results['encoding'] = encoding_result.get('encoding', 'unknown')
        
        # Try to read the file as text
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                results['error'] = f"Could not read file: {e}"
                return results
        
        # Check each character
        unicode_positions = []
        for i, char in enumerate(content):
            if ord(char) > 127:  # Non-ASCII character
                unicode_positions.append({
                    'position': i,
                    'char': char,
                    'ord': ord(char),
                    'line': content[:i].count('\n') + 1,
                    'column': i - content.rfind('\n', 0, i)
                })
        
        if unicode_positions:
            results['has_unicode'] = True
            results['unicode_chars'] = unicode_positions
            
    except Exception as e:
        results['error'] = str(e)
    
    return results

def scan_project_for_unicode(project_root):
    """
    Scan entire project for unicode characters
    
    Args:
        project_root (str): Root directory of the project
        
    Returns:
        dict: Complete scan results
    """
    project_path = Path(project_root)
    
    # File extensions to check
    text_extensions = {
        '.py', '.txt', '.md', '.rst', '.yaml', '.yml', 
        '.json', '.cfg', '.ini', '.conf', '.sh', '.bat'
    }
    
    # Directories to skip
    skip_dirs = {
        'venv', '__pycache__', '.git', 'node_modules', 
        '.pytest_cache', 'build', 'dist', '.vscode',
        'site-packages'
    }
    
    scan_results = {
        'total_files_scanned': 0,
        'files_with_unicode': [],
        'clean_files': [],
        'errors': []
    }
    
    print(f"Scanning project directory: {project_root}")
    print("Checking for unicode characters in text files...")
    print("=" * 60)
    
    for root, dirs, files in os.walk(project_path):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = Path(file).suffix.lower()
            
            # Only check text files
            if file_ext in text_extensions:
                scan_results['total_files_scanned'] += 1
                relative_path = os.path.relpath(file_path, project_root)
                
                print(f"Checking: {relative_path}")
                
                result = check_file_for_unicode(file_path)
                
                if result['error']:
                    scan_results['errors'].append(result)
                elif result['has_unicode']:
                    scan_results['files_with_unicode'].append(result)
                else:
                    scan_results['clean_files'].append(relative_path)
    
    return scan_results

def run_unicode_detection_test():
    """
    Main function to run unicode character detection test
    
    This function scans all relevant files in the project to detect
    any unicode characters that should be removed for ASCII compliance.
    
    Returns:
        int: Exit code (0 if no unicode found, 1 if unicode detected or errors)
    """
    print("Power Meter Monitor - Unicode Character Detection Test")
    print("=" * 70)
    print("This test scans all project files for unicode characters")
    print("to ensure ASCII-only content compliance.\n")
    
    # Get project root (parent of test directory)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)
    
    # Run the scan
    results = scan_project_for_unicode(project_root)
    
    print(f"\nScan Results:")
    print(f"Total files scanned: {results['total_files_scanned']}")
    print(f"Clean files (ASCII only): {len(results['clean_files'])}")
    print(f"Files with unicode: {len(results['files_with_unicode'])}")
    print(f"Files with errors: {len(results['errors'])}")
    
    # Report unicode findings
    if results['files_with_unicode']:
        print(f"\nUNICODE CHARACTERS DETECTED:")
        print("=" * 40)
        
        for file_result in results['files_with_unicode']:
            relative_path = os.path.relpath(file_result['file'], project_root)
            print(f"\nFile: {relative_path}")
            print(f"Encoding: {file_result['encoding']}")
            print(f"Unicode characters found: {len(file_result['unicode_chars'])}")
            
            for char_info in file_result['unicode_chars'][:10]:  # Limit to first 10
                print(f"  Line {char_info['line']}, Col {char_info['column']}: "
                      f"'{char_info['char']}' (Unicode: {char_info['ord']})")
            
            if len(file_result['unicode_chars']) > 10:
                remaining = len(file_result['unicode_chars']) - 10
                print(f"  ... and {remaining} more unicode characters")
    
    # Report errors
    if results['errors']:
        print(f"\nERRORS DURING SCAN:")
        print("=" * 30)
        
        for error_result in results['errors']:
            relative_path = os.path.relpath(error_result['file'], project_root)
            print(f"File: {relative_path}")
            print(f"Error: {error_result['error']}")
    
    # Final summary
    print(f"\nTEST SUMMARY:")
    print("=" * 20)
    
    if not results['files_with_unicode'] and not results['errors']:
        print("SUCCESS: No unicode characters detected in project files!")
        print("All files contain ASCII-only content.")
        return 0
    else:
        if results['files_with_unicode']:
            print(f"WARNING: {len(results['files_with_unicode'])} files contain unicode characters")
            print("These files should be cleaned to remove unicode characters.")
        
        if results['errors']:
            print(f"ERROR: {len(results['errors'])} files could not be processed")
            print("Check file permissions and encoding issues.")
        
        print("\nRecommendations:")
        print("1. Remove or replace unicode characters with ASCII equivalents")
        print("2. Use ASCII-only characters in code, comments, and documentation")
        print("3. Re-run this test after making corrections")
        
        return 1

if __name__ == "__main__":
    sys.exit(run_unicode_detection_test())

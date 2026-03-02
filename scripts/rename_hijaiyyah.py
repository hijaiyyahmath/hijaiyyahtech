import os
import sys

def replace_text_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        orig_content = content
        
        # Replace occurrences with case preservation mostly
        content = content.replace('hijaiyyah', 'hijaiyyah')
        content = content.replace('Hijaiyyah', 'Hijaiyyah')
        content = content.replace('HIJAIYYAH', 'HIJAIYYAH')
        
        if content != orig_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated content in: {filepath}")
    except (UnicodeDecodeError, PermissionError):
        # Skip binary files or unreadable files
        pass

def main():
    root_dir = r"c:\hijaiyyah-codex"
    ignore_dirs = {'.git', 'node_modules', '.next', '__pycache__', '.venv', 'venv'}
    
    # First pass: replace content and rename files
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Filter ignore dirs
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        
        # skip ignored directories completely in the path
        if any(ignored in dirpath.split(os.sep) for ignored in ignore_dirs):
            continue

        # Process files in directory
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            # replacing text in file
            replace_text_in_file(filepath)
            
            # rename file if needed
            new_filename = filename.replace('hijaiyyah', 'hijaiyyah')
            new_filename = new_filename.replace('Hijaiyyah', 'Hijaiyyah')
            new_filename = new_filename.replace('HIJAIYYAH', 'HIJAIYYAH')
            if new_filename != filename:
                new_filepath = os.path.join(dirpath, new_filename)
                os.rename(filepath, new_filepath)
                print(f"Renamed file: {filepath} -> {new_filename}")

        # Process directories
        for dirname in dirnames:
            dirpath_full = os.path.join(dirpath, dirname)
            new_dirname = dirname.replace('hijaiyyah', 'hijaiyyah')
            new_dirname = new_dirname.replace('Hijaiyyah', 'Hijaiyyah')
            new_dirname = new_dirname.replace('HIJAIYYAH', 'HIJAIYYAH')
            
            if new_dirname != dirname:
                new_dirpath = os.path.join(dirpath, new_dirname)
                try:
                    os.rename(dirpath_full, new_dirpath)
                    print(f"Renamed directory: {dirpath_full} -> {new_dirname}")
                except Exception as e:
                    print(f"Failed to rename directory {dirpath_full}: {e}")

if __name__ == "__main__":
    main()

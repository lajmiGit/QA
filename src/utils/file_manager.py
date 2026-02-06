import os
from typing import List
from src.models import GeneratedFile

class FileManager:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def write_files(self, files: List[GeneratedFile]):
        """Writes the list of generated files to the disk."""
        created_paths = []
        for file in files:
            # Ensure path is relative and safe
            clean_path = file.file_path.lstrip('/')
            full_path = os.path.join(self.base_path, clean_path)
            
            # Create subdirectories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file.content)
            
            created_paths.append(full_path)
            print(f"    [FILE MANAGER] Created: {clean_path}")
            
        return created_paths

"""
File Utilities for AI Agent Benchmark system.

This module provides file operation utilities including
reading, writing, and analyzing files.
"""

import os
import json
import yaml
import shutil
import hashlib
from typing import Any, Dict, List, Optional, Union
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class FileUtils:
    """File utility functions."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize file utilities.
        
        Args:
            base_path: Base path for operations
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
        logger.info(f"File utilities initialized for {self.base_path}")
    
    def read_file(
        self,
        file_path: Union[str, Path],
        encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Read file content.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            File content or None if error
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            logger.debug(f"Read file: {path}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def write_file(
        self,
        file_path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> bool:
        """
        Write content to file.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding
            create_dirs: Create parent directories if needed
            
        Returns:
            True if successful
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.debug(f"Wrote file: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return False
    
    def append_file(
        self,
        file_path: Union[str, Path],
        content: str,
        encoding: str = "utf-8"
    ) -> bool:
        """
        Append content to file.
        
        Args:
            file_path: Path to file
            content: Content to append
            encoding: File encoding
            
        Returns:
            True if successful
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            with open(path, 'a', encoding=encoding) as f:
                f.write(content)
            
            logger.debug(f"Appended to file: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append to file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path
        return path.exists() and path.is_file()
    
    def directory_exists(self, dir_path: Union[str, Path]) -> bool:
        """Check if directory exists."""
        path = Path(dir_path)
        if not path.is_absolute():
            path = self.base_path / path
        return path.exists() and path.is_dir()
    
    def create_directory(
        self,
        dir_path: Union[str, Path],
        parents: bool = True
    ) -> bool:
        """Create directory."""
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            path.mkdir(parents=parents, exist_ok=True)
            logger.debug(f"Created directory: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            return False
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """Delete file."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if path.exists():
                path.unlink()
                logger.debug(f"Deleted file: {path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def copy_file(
        self,
        source: Union[str, Path],
        destination: Union[str, Path]
    ) -> bool:
        """Copy file."""
        try:
            src_path = Path(source)
            if not src_path.is_absolute():
                src_path = self.base_path / src_path
            
            dst_path = Path(destination)
            if not dst_path.is_absolute():
                dst_path = self.base_path / dst_path
            
            shutil.copy2(src_path, dst_path)
            logger.debug(f"Copied file: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file {source} to {destination}: {e}")
            return False
    
    def move_file(
        self,
        source: Union[str, Path],
        destination: Union[str, Path]
    ) -> bool:
        """Move file."""
        try:
            src_path = Path(source)
            if not src_path.is_absolute():
                src_path = self.base_path / src_path
            
            dst_path = Path(destination)
            if not dst_path.is_absolute():
                dst_path = self.base_path / dst_path
            
            shutil.move(str(src_path), str(dst_path))
            logger.debug(f"Moved file: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file {source} to {destination}: {e}")
            return False
    
    def get_file_info(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Get file information."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists():
                return None
            
            stat = path.stat()
            
            return {
                "name": path.name,
                "extension": path.suffix,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "absolute_path": str(path.absolute()),
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info {file_path}: {e}")
            return None
    
    def calculate_file_hash(
        self,
        file_path: Union[str, Path],
        algorithm: str = "sha256"
    ) -> Optional[str]:
        """Calculate file hash."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            hash_func = hashlib.new(algorithm)
            
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return None
    
    def list_files(
        self,
        dir_path: Union[str, Path],
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """List files in directory."""
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if recursive:
                return list(path.rglob(pattern))
            else:
                return list(path.glob(pattern))
                
        except Exception as e:
            logger.error(f"Failed to list files in {dir_path}: {e}")
            return []
    
    def read_json(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Read JSON file."""
        content = self.read_file(file_path)
        if content is None:
            return None
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            return None
    
    def write_json(
        self,
        file_path: Union[str, Path],
        data: Dict[str, Any],
        indent: int = 2
    ) -> bool:
        """Write JSON file."""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.write_file(file_path, content)
        except Exception as e:
            logger.error(f"Failed to write JSON file {file_path}: {e}")
            return False
    
    def read_yaml(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Read YAML file."""
        content = self.read_file(file_path)
        if content is None:
            return None
        
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {file_path}: {e}")
            return None
    
    def write_yaml(
        self,
        file_path: Union[str, Path],
        data: Dict[str, Any]
    ) -> bool:
        """Write YAML file."""
        try:
            content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
            return self.write_file(file_path, content)
        except Exception as e:
            logger.error(f"Failed to write YAML file {file_path}: {e}")
            return False
    
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """Get file size in bytes."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            return path.stat().st_size if path.exists() else None
            
        except Exception as e:
            logger.error(f"Failed to get file size {file_path}: {e}")
            return None
    
    def get_directory_size(self, dir_path: Union[str, Path]) -> int:
        """Get total size of directory."""
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            total_size = 0
            for file in path.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
            
            return total_size
            
        except Exception as e:
            logger.error(f"Failed to get directory size {dir_path}: {e}")
            return 0
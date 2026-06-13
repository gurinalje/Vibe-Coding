"""
Git Utilities for AI Agent Benchmark system.

This module provides Git-related utility functions for
repository operations and code analysis.
"""

import subprocess
import os
from typing import Any, Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class GitUtils:
    """Git utility functions."""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git utilities.
        
        Args:
            repo_path: Path to Git repository
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        
        logger.info(f"Git utilities initialized for {self.repo_path}")
    
    def _run_command(
        self,
        command: List[str],
        cwd: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """
        Run a Git command.
        
        Args:
            command: Command to run
            cwd: Working directory
            
        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                cwd=cwd or str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(command)}")
            return -1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Git command failed: {e}")
            return -1, "", str(e)
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        returncode, _, _ = self._run_command(["git", "rev-parse", "--git-dir"])
        return returncode == 0
    
    def get_repo_info(self) -> Dict[str, Any]:
        """Get repository information."""
        info = {}
        
        # Get current branch
        returncode, stdout, _ = self._run_command(["git", "branch", "--show-current"])
        if returncode == 0:
            info["branch"] = stdout.strip()
        
        # Get remote URL
        returncode, stdout, _ = self._run_command(["git", "remote", "get-url", "origin"])
        if returncode == 0:
            info["remote_url"] = stdout.strip()
        
        # Get last commit
        returncode, stdout, _ = self._run_command(["git", "log", "-1", "--pretty=format:%H %s"])
        if returncode == 0:
            parts = stdout.strip().split(" ", 1)
            if len(parts) == 2:
                info["last_commit_hash"] = parts[0]
                info["last_commit_message"] = parts[1]
        
        # Get status
        returncode, stdout, _ = self._run_command(["git", "status", "--porcelain"])
        if returncode == 0:
            info["modified_files"] = len(stdout.strip().split("\n")) if stdout.strip() else 0
        
        return info
    
    def get_diff(
        self,
        branch: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> str:
        """Get diff for changes."""
        command = ["git", "diff"]
        
        if branch:
            command.append(branch)
        
        if file_path:
            command.append("--")
            command.append(file_path)
        
        returncode, stdout, _ = self._run_command(command)
        return stdout if returncode == 0 else ""
    
    def get_staged_diff(self) -> str:
        """Get diff for staged changes."""
        returncode, stdout, _ = self._run_command(["git", "diff", "--cached"])
        return stdout if returncode == 0 else ""
    
    def get_file_history(
        self,
        file_path: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get commit history for a file."""
        command = [
            "git", "log",
            f"--max-count={limit}",
            "--pretty=format:%H|%an|%ae|%ad|%s",
            "--date=short",
            "--",
            file_path
        ]
        
        returncode, stdout, _ = self._run_command(command)
        
        if returncode != 0:
            return []
        
        history = []
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) == 5:
                    history.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4],
                    })
        
        return history
    
    def get_blame(self, file_path: str) -> List[Dict[str, str]]:
        """Get blame information for a file."""
        command = ["git", "blame", "--porcelain", file_path]
        
        returncode, stdout, _ = self._run_command(command)
        
        if returncode != 0:
            return []
        
        # Parse blame output (simplified)
        blame_lines = []
        current_commit = None
        current_author = None
        
        for line in stdout.split("\n"):
            if line.startswith("\t"):
                # Content line
                blame_lines.append({
                    "commit": current_commit,
                    "author": current_author,
                    "content": line[1:],  # Remove tab
                })
            elif line.startswith("commit "):
                current_commit = line[7:]
            elif line.startswith("author "):
                current_author = line[7:]
        
        return blame_lines
    
    def get_branches(self) -> List[str]:
        """Get list of branches."""
        returncode, stdout, _ = self._run_command(["git", "branch", "--format=%(refname:short)"])
        
        if returncode != 0:
            return []
        
        return [b.strip() for b in stdout.strip().split("\n") if b.strip()]
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch."""
        returncode, _, _ = self._run_command(["git", "checkout", "-b", branch_name])
        return returncode == 0
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a branch."""
        returncode, _, _ = self._run_command(["git", "checkout", branch_name])
        return returncode == 0
    
    def get_changed_files(
        self,
        base_branch: Optional[str] = None
    ) -> List[str]:
        """Get list of changed files."""
        if base_branch:
            command = ["git", "diff", "--name-only", base_branch]
        else:
            command = ["git", "diff", "--name-only"]
        
        returncode, stdout, _ = self._run_command(command)
        
        if returncode != 0:
            return []
        
        return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
    
    def get_file_content(
        self,
        file_path: str,
        ref: Optional[str] = None
    ) -> Optional[str]:
        """Get content of a file."""
        if ref:
            command = ["git", "show", f"{ref}:{file_path}"]
        else:
            command = ["git", "show", f"HEAD:{file_path}"]
        
        returncode, stdout, _ = self._run_command(command)
        
        return stdout if returncode == 0 else None
    
    def stash_changes(self) -> bool:
        """Stash current changes."""
        returncode, _, _ = self._run_command(["git", "stash"])
        return returncode == 0
    
    def pop_stash(self) -> bool:
        """Pop stashed changes."""
        returncode, _, _ = self._run_command(["git", "stash", "pop"])
        return returncode == 0
    
    def commit_changes(self, message: str) -> bool:
        """Commit staged changes."""
        returncode, _, _ = self._run_command(["git", "commit", "-m", message])
        return returncode == 0
    
    def add_files(self, files: List[str]) -> bool:
        """Add files to staging."""
        command = ["git", "add"] + files
        returncode, _, _ = self._run_command(command)
        return returncode == 0
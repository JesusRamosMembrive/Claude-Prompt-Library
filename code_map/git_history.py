"""
Git history analysis module for Code Timeline Visualization.

Provides utilities to parse git log, analyze file history, and extract commit information.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Set
import re


class GitHistoryError(Exception):
    """Raised when git operations fail."""
    pass


class CommitInfo:
    """Information about a single git commit."""

    def __init__(
        self,
        hash: str,
        author: str,
        date: datetime,
        message: str,
        files_changed: List[str]
    ):
        self.hash = hash
        self.author = author
        self.date = date
        self.message = message
        self.files_changed = files_changed

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "hash": self.hash,
            "author": self.author,
            "date": self.date.isoformat(),
            "message": self.message,
            "files_changed": self.files_changed
        }


class GitHistory:
    """
    Git history analyzer for timeline visualization.

    Stage 1 MVP:
    - Parse git log with file changes
    - Filter by date range, author, file path
    - Extract commit metadata
    """

    def __init__(self, repo_path: Path):
        """
        Initialize git history analyzer.

        Args:
            repo_path: Path to git repository root
        """
        self.repo_path = Path(repo_path)
        self._validate_git_repo()

    def _validate_git_repo(self) -> None:
        """Validate that repo_path is a git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise GitHistoryError(f"Not a git repository: {self.repo_path}")

    def _run_git_command(self, args: List[str]) -> str:
        """
        Run a git command and return output.

        Args:
            args: Git command arguments (without 'git')

        Returns:
            Command output as string

        Raises:
            GitHistoryError: If command fails
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise GitHistoryError(f"Git command failed: {e.stderr}")

    def get_commits(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        author: Optional[str] = None,
        file_path: Optional[str] = None,
        limit: int = 100
    ) -> List[CommitInfo]:
        """
        Get commit history with optional filters.

        Args:
            since: Only commits after this date
            until: Only commits before this date
            author: Filter by author name/email
            file_path: Only commits that modified this file
            limit: Maximum number of commits to return

        Returns:
            List of CommitInfo objects
        """
        # Build git log command
        # Format: hash|author|date|message
        args = [
            "log",
            "--name-only",  # Show file names
            "--pretty=format:%H|%an|%ai|%s",
            f"-n{limit}"
        ]

        # Add filters
        if since:
            args.append(f"--since={since.isoformat()}")
        if until:
            args.append(f"--until={until.isoformat()}")
        if author:
            args.append(f"--author={author}")
        if file_path:
            args.append("--")
            args.append(file_path)

        output = self._run_git_command(args)

        return self._parse_commit_log(output)

    def _parse_commit_log(self, log_output: str) -> List[CommitInfo]:
        """
        Parse git log output into CommitInfo objects.

        Format:
        hash|author|date|message
        file1.py
        file2.py

        hash2|author2|date2|message2
        file3.py
        """
        commits = []
        lines = log_output.strip().split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Parse commit header
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) == 4:
                    hash_str, author, date_str, message = parts

                    # Parse date
                    try:
                        # Git date format: 2025-11-09 12:34:56 +0100
                        date = datetime.fromisoformat(date_str.rsplit(" ", 1)[0])
                    except (ValueError, IndexError):
                        date = datetime.now()

                    # Collect files changed (lines after header until next commit or end)
                    files_changed = []
                    i += 1
                    while i < len(lines) and "|" not in lines[i]:
                        file_line = lines[i].strip()
                        if file_line:
                            files_changed.append(file_line)
                        i += 1

                    commits.append(CommitInfo(
                        hash=hash_str,
                        author=author,
                        date=date,
                        message=message,
                        files_changed=files_changed
                    ))
                    continue

            i += 1

        return commits

    def get_file_history(
        self,
        file_path: str,
        limit: int = 50
    ) -> Dict[str, any]:
        """
        Get commit history for a specific file.

        Args:
            file_path: Path to file (relative to repo root)
            limit: Maximum number of commits

        Returns:
            Dictionary with file_path, commits, and total_changes
        """
        commits = self.get_commits(file_path=file_path, limit=limit)

        return {
            "file_path": file_path,
            "commits": [c.to_dict() for c in commits],
            "total_changes": len(commits)
        }

    def get_commit_details(self, commit_hash: str) -> Optional[CommitInfo]:
        """
        Get detailed information about a specific commit.

        Args:
            commit_hash: Git commit hash (full or short)

        Returns:
            CommitInfo object or None if commit not found
        """
        try:
            commits = self.get_commits(limit=1)
            # Get specific commit
            args = [
                "show",
                "--name-only",
                "--pretty=format:%H|%an|%ai|%s",
                commit_hash
            ]
            output = self._run_git_command(args)
            commits = self._parse_commit_log(output)
            return commits[0] if commits else None
        except GitHistoryError:
            return None

    def get_all_files(self) -> List[str]:
        """
        Get list of all files currently tracked by git.

        Returns:
            List of file paths (relative to repo root)
        """
        try:
            output = self._run_git_command(["ls-files"])
            return [line.strip() for line in output.split("\n") if line.strip()]
        except GitHistoryError:
            return []

    def get_timeline_matrix(
        self,
        limit: int = 50,
        file_pattern: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Get timeline data structured for DAW-style visualization.

        Returns a matrix where:
        - Rows: Files
        - Columns: Commits (chronological)
        - Cells: True if file changed in that commit

        Args:
            limit: Maximum number of commits
            file_pattern: Optional regex pattern to filter files

        Returns:
            Dictionary with:
            - commits: List of commit metadata
            - files: List of file paths
            - matrix: 2D array of booleans (file_index, commit_index)
        """
        commits = self.get_commits(limit=limit)

        # Collect all unique files
        all_files: Set[str] = set()
        for commit in commits:
            all_files.update(commit.files_changed)

        # Filter files by pattern if provided
        if file_pattern:
            pattern = re.compile(file_pattern)
            all_files = {f for f in all_files if pattern.search(f)}

        files_list = sorted(all_files)

        # Build matrix
        matrix = []
        for file_path in files_list:
            row = []
            for commit in commits:
                row.append(file_path in commit.files_changed)
            matrix.append(row)

        return {
            "commits": [c.to_dict() for c in commits],
            "files": files_list,
            "matrix": matrix,
            "total_files": len(files_list),
            "total_commits": len(commits)
        }

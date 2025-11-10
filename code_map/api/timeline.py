"""
Timeline API endpoints for git history visualization.

Provides REST endpoints for:
- GET /api/timeline/commits - List commits with filters
- GET /api/timeline/files/{file_path:path} - File history
- GET /api/timeline/commit/{commit_hash} - Commit details
- GET /api/timeline/matrix - Timeline matrix for DAW-style visualization
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from ..git_history import GitHistory, GitHistoryError
from ..state import AppState
from .deps import get_app_state


# ============================================================================
# Pydantic Schemas
# ============================================================================


class CommitInfoSchema(BaseModel):
    """Schema for commit information."""

    hash: str = Field(..., description="Git commit hash")
    author: str = Field(..., description="Commit author")
    date: str = Field(..., description="Commit date (ISO format)")
    message: str = Field(..., description="Commit message")
    files_changed: List[str] = Field(
        default_factory=list, description="Files changed in this commit"
    )


class CommitsResponse(BaseModel):
    """Response for /commits endpoint."""

    commits: List[CommitInfoSchema]
    total: int = Field(..., description="Total number of commits returned")
    filters_applied: dict = Field(
        default_factory=dict, description="Filters that were applied"
    )


class FileHistoryResponse(BaseModel):
    """Response for /files/{path} endpoint."""

    file_path: str = Field(..., description="Path to the file")
    commits: List[CommitInfoSchema]
    total_changes: int = Field(
        ..., description="Total number of commits affecting this file"
    )


class CommitDetailsResponse(BaseModel):
    """Response for /commit/{hash} endpoint."""

    commit: Optional[CommitInfoSchema] = None
    found: bool = Field(..., description="Whether the commit was found")


class TimelineMatrixResponse(BaseModel):
    """Response for /matrix endpoint - DAW-style visualization data."""

    commits: List[CommitInfoSchema] = Field(
        ..., description="List of commits (columns)"
    )
    files: List[str] = Field(..., description="List of files (rows)")
    matrix: List[List[bool]] = Field(
        ..., description="2D matrix: matrix[file_idx][commit_idx] = file changed"
    )
    total_files: int
    total_commits: int


# ============================================================================
# Router
# ============================================================================


router = APIRouter(prefix="/timeline", tags=["timeline"])


def get_git_history(state: AppState = Depends(get_app_state)) -> GitHistory:
    """
    Dependency to get GitHistory instance.

    Args:
        state: Application state with root_path

    Returns:
        GitHistory instance

    Raises:
        HTTPException: If not a git repository
    """
    try:
        return GitHistory(state.settings.root_path)
    except GitHistoryError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/commits", response_model=CommitsResponse)
async def get_commits(
    git_history: GitHistory = Depends(get_git_history),
    since: Optional[str] = Query(
        None, description="ISO date string (e.g., '2025-01-01')"
    ),
    until: Optional[str] = Query(
        None, description="ISO date string (e.g., '2025-12-31')"
    ),
    author: Optional[str] = Query(None, description="Filter by author name/email"),
    file_path: Optional[str] = Query(None, description="Filter by file path"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of commits"),
) -> CommitsResponse:
    """
    Get commit history with optional filters.

    Args:
        git_history: GitHistory dependency
        since: Only commits after this date
        until: Only commits before this date
        author: Filter by author
        file_path: Only commits affecting this file
        limit: Max commits to return

    Returns:
        CommitsResponse with list of commits
    """
    # Parse dates
    since_dt = None
    until_dt = None

    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid 'since' date format: {since}"
            )

    if until:
        try:
            until_dt = datetime.fromisoformat(until)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid 'until' date format: {until}"
            )

    try:
        commits = git_history.get_commits(
            since=since_dt,
            until=until_dt,
            author=author,
            file_path=file_path,
            limit=limit,
        )

        # Convert to schemas
        commit_schemas = [
            CommitInfoSchema(
                hash=c.hash,
                author=c.author,
                date=c.date.isoformat(),
                message=c.message,
                files_changed=c.files_changed,
            )
            for c in commits
        ]

        filters = {}
        if since:
            filters["since"] = since
        if until:
            filters["until"] = until
        if author:
            filters["author"] = author
        if file_path:
            filters["file_path"] = file_path

        return CommitsResponse(
            commits=commit_schemas, total=len(commit_schemas), filters_applied=filters
        )

    except GitHistoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_path:path}", response_model=FileHistoryResponse)
async def get_file_history(
    file_path: str,
    git_history: GitHistory = Depends(get_git_history),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of commits"),
) -> FileHistoryResponse:
    """
    Get commit history for a specific file.

    Args:
        file_path: Path to file (relative to repo root)
        git_history: GitHistory dependency
        limit: Max commits to return

    Returns:
        FileHistoryResponse with file history
    """
    try:
        result = git_history.get_file_history(file_path=file_path, limit=limit)

        # Convert commits from dict to schema
        commit_schemas = [
            CommitInfoSchema(**commit_dict) for commit_dict in result["commits"]
        ]

        return FileHistoryResponse(
            file_path=result["file_path"],
            commits=commit_schemas,
            total_changes=result["total_changes"],
        )

    except GitHistoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commit/{commit_hash}", response_model=CommitDetailsResponse)
async def get_commit_details(
    commit_hash: str,
    git_history: GitHistory = Depends(get_git_history),
) -> CommitDetailsResponse:
    """
    Get detailed information about a specific commit.

    Args:
        commit_hash: Git commit hash (full or short)
        git_history: GitHistory dependency

    Returns:
        CommitDetailsResponse with commit details or found=False
    """
    try:
        commit = git_history.get_commit_details(commit_hash)

        if commit is None:
            return CommitDetailsResponse(commit=None, found=False)

        commit_schema = CommitInfoSchema(
            hash=commit.hash,
            author=commit.author,
            date=commit.date.isoformat(),
            message=commit.message,
            files_changed=commit.files_changed,
        )

        return CommitDetailsResponse(commit=commit_schema, found=True)

    except GitHistoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrix", response_model=TimelineMatrixResponse)
async def get_timeline_matrix(
    git_history: GitHistory = Depends(get_git_history),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of commits"),
    file_pattern: Optional[str] = Query(
        None, description="Regex pattern to filter files"
    ),
) -> TimelineMatrixResponse:
    """
    Get timeline data structured for DAW-style visualization.

    Returns a matrix where:
    - Rows: Files
    - Columns: Commits (chronological)
    - Cells: True if file changed in that commit

    Args:
        git_history: GitHistory dependency
        limit: Max commits to include
        file_pattern: Optional regex to filter files (e.g., r"\\.py$" for Python files)

    Returns:
        TimelineMatrixResponse with commits, files, and matrix
    """
    try:
        result = git_history.get_timeline_matrix(limit=limit, file_pattern=file_pattern)

        # Convert commits from dict to schema
        commit_schemas = [
            CommitInfoSchema(**commit_dict) for commit_dict in result["commits"]
        ]

        return TimelineMatrixResponse(
            commits=commit_schemas,
            files=result["files"],
            matrix=result["matrix"],
            total_files=result["total_files"],
            total_commits=result["total_commits"],
        )

    except GitHistoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diff/{commit_hash}")
async def get_file_diff(
    commit_hash: str,
    file_path: str = Query(..., description="File path relative to repo root"),
    git_history: GitHistory = Depends(get_git_history),
) -> dict:
    """
    Get the git diff for a specific file in a commit.

    Args:
        commit_hash: Git commit hash (full or short)
        file_path: Path to file (relative to repo root)
        git_history: GitHistory dependency

    Returns:
        Dictionary with diff content
    """
    try:
        diff = git_history.get_file_diff(commit_hash, file_path)

        if diff is None:
            raise HTTPException(
                status_code=404,
                detail=f"File '{file_path}' not found in commit '{commit_hash}'",
            )

        return {"commit_hash": commit_hash, "file_path": file_path, "diff": diff}

    except GitHistoryError as e:
        raise HTTPException(status_code=500, detail=str(e))

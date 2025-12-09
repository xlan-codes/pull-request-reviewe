"""
Base adapter for platform integrations.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileChange:
    """Represents a file change in a PR/MR."""
    filename: str
    status: str  # added, modified, deleted, renamed
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None
    previous_filename: Optional[str] = None


@dataclass
class PullRequest:
    """Unified representation of a PR/MR across platforms."""
    platform: str  # github, gitlab, bitbucket
    id: str
    number: int
    title: str
    description: str
    author: str
    created_at: datetime
    updated_at: datetime
    state: str  # open, closed, merged
    source_branch: str
    target_branch: str
    repository: str
    url: str
    files_changed: List[FileChange]
    commits_count: int
    additions: int
    deletions: int
    changed_files: int
    labels: List[str]
    language: Optional[str] = None



class BasePlatformAdapter(ABC):
    """Abstract base class for platform adapters."""

    def __init__(self, token: Optional[str] = None, **kwargs):
        """Initialize the adapter with credentials."""
        self.token = token
        self.extra_config = kwargs

    @abstractmethod
    def fetch_pull_request(self, url: str) -> PullRequest:
        """
        Fetch PR/MR details from the platform.

        Args:
            url: The URL of the PR/MR

        Returns:
            PullRequest object with all details
        """
        pass

    @abstractmethod
    def get_file_content(self, repo: str, filepath: str, ref: str) -> str:
        """
        Get content of a specific file at a specific commit.

        Args:
            repo: Repository identifier
            filepath: Path to the file
            ref: Git reference (commit SHA, branch name)

        Returns:
            File content as string
        """
        pass

    @abstractmethod
    def post_review_comment(self, pr_url: str, comment: str) -> bool:
        """
        Post a review comment on the PR/MR.

        Args:
            pr_url: The URL of the PR/MR
            comment: The review comment

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse platform URL to extract repository and PR/MR info.

        Args:
            url: The PR/MR URL

        Returns:
            Dictionary with parsed components
        """
        pass

    def validate_token(self) -> bool:
        """Validate that the token is valid."""
        return self.token is not None


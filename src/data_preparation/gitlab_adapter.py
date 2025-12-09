"""
GitLab adapter for fetching MR data.
"""
import re
from typing import Dict, Optional
from datetime import datetime
import gitlab
import logging

from src.data_preparation.base_adapter import BasePlatformAdapter, PullRequest, FileChange
from src.config.settings import settings

logger = logging.getLogger(__name__)


class GitLabAdapter(BasePlatformAdapter):
    """Adapter for GitLab API."""

    def __init__(self, token: Optional[str] = None, url: Optional[str] = None):
        """Initialize GitLab adapter."""
        super().__init__(
            token or settings.gitlab_token,
            url=url or settings.gitlab_url
        )
        if not self.token:
            logger.warning("No GitLab token provided. Private projects won't be accessible.")

        self.gitlab_url = self.extra_config.get('url', settings.gitlab_url)
        self.client = gitlab.Gitlab(self.gitlab_url, private_token=self.token)

    def parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse GitLab MR URL.

        Example: https://gitlab.com/owner/repo/-/merge_requests/123
        """
        pattern = r"gitlab\.com/([^/]+/[^/]+)/-/merge_requests/(\d+)"
        match = re.search(pattern, url)

        if not match:
            raise ValueError(f"Invalid GitLab MR URL: {url}")

        return {
            "project": match.group(1),
            "mr_number": int(match.group(2))
        }

    def fetch_pull_request(self, url: str) -> PullRequest:
        """Fetch MR details from GitLab."""
        try:
            parsed = self.parse_url(url)
            project_path = parsed['project']
            mr_number = parsed['mr_number']

            logger.info(f"Fetching GitLab MR: {project_path}!{mr_number}")

            # Get project and MR
            project = self.client.projects.get(project_path)
            mr = project.mergerequests.get(mr_number)

            # Get file changes
            files_changed = []
            changes = mr.changes()

            for change in changes.get('changes', []):
                # Determine status
                if change.get('new_file'):
                    status = 'added'
                elif change.get('deleted_file'):
                    status = 'deleted'
                elif change.get('renamed_file'):
                    status = 'renamed'
                else:
                    status = 'modified'

                files_changed.append(FileChange(
                    filename=change.get('new_path', change.get('old_path')),
                    status=status,
                    additions=0,  # GitLab doesn't provide per-file stats easily
                    deletions=0,
                    changes=0,
                    patch=change.get('diff'),
                    previous_filename=change.get('old_path') if status == 'renamed' else None
                ))

            # Get labels
            labels = mr.labels

            pull_request = PullRequest(
                platform="gitlab",
                id=str(mr.id),
                number=mr.iid,
                title=mr.title,
                description=mr.description or "",
                author=mr.author.get('username', 'unknown'),
                created_at=datetime.fromisoformat(mr.created_at.replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(mr.updated_at.replace('Z', '+00:00')),
                state=mr.state,
                source_branch=mr.source_branch,
                target_branch=mr.target_branch,
                repository=project_path,
                url=url,
                files_changed=files_changed,
                commits_count=len(mr.commits()),
                additions=0,  # Not easily available
                deletions=0,
                changed_files=len(files_changed),
                labels=labels,
                language=None  # Would need to analyze project
            )

            logger.info(f"Successfully fetched MR with {len(files_changed)} files changed")
            return pull_request

        except gitlab.exceptions.GitlabError as e:
            logger.error(f"GitLab API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching GitLab MR: {e}")
            raise

    def get_file_content(self, repo: str, filepath: str, ref: str) -> str:
        """Get file content from GitLab."""
        try:
            project = self.client.projects.get(repo)
            file_info = project.files.get(file_path=filepath, ref=ref)

            import base64
            content = base64.b64decode(file_info.content).decode('utf-8')
            return content

        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            raise

    def post_review_comment(self, pr_url: str, comment: str) -> bool:
        """Post a review comment on GitLab MR."""
        try:
            parsed = self.parse_url(pr_url)
            project_path = parsed['project']
            mr_number = parsed['mr_number']

            project = self.client.projects.get(project_path)
            mr = project.mergerequests.get(mr_number)

            # Post as a note
            mr.notes.create({'body': comment})

            logger.info(f"Posted review comment to MR !{mr_number}")
            return True

        except Exception as e:
            logger.error(f"Error posting review comment: {e}")
            return False


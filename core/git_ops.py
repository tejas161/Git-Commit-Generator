"""
Git Operations Module

Handles all git repository interactions including:
- Repository validation
- Reading staged changes
- Creating commits
"""

from git import Repo, InvalidGitRepositoryError
from typing import Dict, List, Optional


class GitOperations:
    """Handles git repository operations."""
    
    def __init__(self, repo_path: str = "."):
        """Initialize with repository path."""
        self.repo_path = repo_path
        self._repo = None
    
    @property
    def repo(self) -> Repo:
        """Get git repository instance."""
        if self._repo is None:
            try:
                self._repo = Repo(self.repo_path)
            except InvalidGitRepositoryError:
                raise Exception("Not a git repository")
        return self._repo
    
    def is_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            self.repo
            return True
        except Exception:
            return False
    
    def has_staged_changes(self) -> bool:
        """Check if there are staged changes."""
        try:
            # Check if repository has any commits
            try:
                self.repo.head.commit
                # Repository has commits, compare against HEAD
                staged_changes = self.repo.index.diff("HEAD", cached=True)
            except ValueError:
                # No commits yet, check staged files directly
                staged_changes = self.repo.index.diff(None, cached=True)
            
            return len(staged_changes) > 0
        except Exception:
            return False
    
    def get_staged_changes(self) -> Optional[Dict]:
        """
        Get detailed information about staged changes.
        
        Returns:
            Dict with change information or None if no changes
        """
        try:
            # Check if repository has any commits
            try:
                self.repo.head.commit
                # Repository has commits, compare against HEAD
                staged_changes = self.repo.index.diff("HEAD", cached=True)
            except ValueError:
                # No commits yet, check staged files directly
                staged_changes = self.repo.index.diff(None, cached=True)
            
            if not staged_changes:
                return None
            
            changes_data = {
                'files': [],
                'total_files': len(staged_changes),
                'summary': ''
            }
            
            for change in staged_changes:
                file_info = {
                    'path': change.a_path or change.b_path,
                    'change_type': change.change_type,
                    'status': self._get_change_status(change.change_type)
                }
                changes_data['files'].append(file_info)
            
            # Create human-readable summary
            changes_data['summary'] = self._create_changes_summary(changes_data['files'])
            
            return changes_data
            
        except Exception as e:
            raise Exception(f"Failed to get staged changes: {str(e)}")
    
    def create_commit(self, message: str) -> Dict:
        """
        Create a commit with the given message.
        
        Args:
            message: Commit message
            
        Returns:
            Dict with commit information
        """
        try:
            commit = self.repo.index.commit(message)
            
            return {
                'hash': commit.hexsha[:8],
                'message': message,
                'author': str(commit.author),
                'timestamp': commit.committed_datetime.isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to create commit: {str(e)}")
    
    def get_recent_commits(self, count: int = 5) -> List[Dict]:
        """Get recent commit messages for context."""
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=count):
                commits.append({
                    'hash': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': commit.committed_datetime.strftime('%Y-%m-%d')
                })
            return commits
        except Exception:
            return []
    
    def _get_change_status(self, change_type: str) -> str:
        """Convert git change type to human readable status."""
        status_map = {
            'A': 'Added',
            'M': 'Modified', 
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            'T': 'Type changed'
        }
        return status_map.get(change_type, 'Unknown')
    
    def _create_changes_summary(self, files: List[Dict]) -> str:
        """Create a formatted summary of changes for the LLM."""
        summary_lines = [
            f"Git Changes Summary:",
            f"Total files changed: {len(files)}",
            "",
            "Files changed:"
        ]
        
        for file_info in files:
            summary_lines.append(
                f"- {file_info['path']} ({file_info['status']})"
            )
        
        return "\n".join(summary_lines) 
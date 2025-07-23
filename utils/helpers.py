"""
Helper Functions

Utility functions for various operations.
"""

import re
from typing import Dict, List, Optional, Tuple


def validate_commit_message(message: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if a commit message follows conventional commit format.
    
    Args:
        message: Commit message to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Commit message cannot be empty"
    
    # Basic conventional commit pattern
    pattern = r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .+'
    
    if not re.match(pattern, message):
        return False, "Message doesn't follow conventional commit format: type(scope): description"
    
    # Check length
    if len(message) > 72:
        return False, f"Message too long ({len(message)} chars). Keep under 72 characters."
    
    # Check if description starts with lowercase
    colon_pos = message.find(': ')
    if colon_pos != -1 and colon_pos + 2 < len(message):
        description = message[colon_pos + 2:]
        if description[0].isupper():
            return False, "Description should start with lowercase letter"
    
    return True, None


def format_commit_message(commit_type: str, scope: Optional[str], description: str) -> str:
    """
    Format a commit message following conventional commit format.
    
    Args:
        commit_type: Type of commit (feat, fix, etc.)
        scope: Optional scope
        description: Commit description
        
    Returns:
        Formatted commit message
    """
    scope_part = f"({scope})" if scope else ""
    return f"{commit_type}{scope_part}: {description}"


def extract_commit_info(message: str) -> Dict[str, Optional[str]]:
    """
    Extract components from a conventional commit message.
    
    Args:
        message: Commit message to parse
        
    Returns:
        Dict with type, scope, description
    """
    pattern = r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\((.+)\))?: (.+)'
    match = re.match(pattern, message)
    
    if not match:
        return {
            'type': None,
            'scope': None,
            'description': message
        }
    
    return {
        'type': match.group(1),
        'scope': match.group(3),
        'description': match.group(4)
    }


def get_conventional_types() -> List[Dict[str, str]]:
    """
    Get list of conventional commit types with descriptions.
    
    Returns:
        List of dicts with type and description
    """
    return [
        {'type': 'feat', 'description': 'A new feature'},
        {'type': 'fix', 'description': 'A bug fix'},
        {'type': 'docs', 'description': 'Documentation only changes'},
        {'type': 'style', 'description': 'Changes that do not affect the meaning of the code'},
        {'type': 'refactor', 'description': 'A code change that neither fixes a bug nor adds a feature'},
        {'type': 'test', 'description': 'Adding missing tests or correcting existing tests'},
        {'type': 'chore', 'description': 'Changes to the build process or auxiliary tools'},
        {'type': 'perf', 'description': 'A code change that improves performance'},
        {'type': 'ci', 'description': 'Changes to CI configuration files and scripts'},
        {'type': 'build', 'description': 'Changes that affect the build system or external dependencies'},
        {'type': 'revert', 'description': 'Reverts a previous commit'}
    ]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized or 'unnamed'


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_environment_bool(value: str, default: bool = False) -> bool:
    """
    Parse environment variable as boolean.
    
    Args:
        value: Environment variable value
        default: Default value if parsing fails
        
    Returns:
        Boolean value
    """
    if not value:
        return default
    
    return value.lower() in ['true', '1', 'yes', 'on'] 
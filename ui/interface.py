"""
User Interface Module

Handles all user interactions including:
- Displaying information
- Getting user input
- Showing progress
"""

from typing import List, Optional, Dict
import sys


class UserInterface:
    """Handles user interface interactions."""
    
    def __init__(self, config=None):
        """Initialize UI with configuration."""
        self.config = config
        self.debug_enabled = config.show_confidence if config else False
    
    def show_header(self):
        """Display application header."""
        print("AI-Powered Git Commit Generator")
        print("=" * 50)
    
    def show_step(self, step: int, total: int, message: str):
        """Display step progress."""
        progress = f"[{step}/{total}]"
        print(f"{progress} {message}")
    
    def show_success(self, message: str):
        """Display success message."""
        print(f"SUCCESS: {message}")
    
    def show_error(self, message: str):
        """Display error message."""
        print(f"ERROR: {message}")
    
    def show_warning(self, message: str):
        """Display warning message."""
        print(f"WARNING: {message}")
    
    def show_info(self, message: str):
        """Display info message."""
        print(f"INFO: {message}")
    
    def show_debug(self, message: str):
        """Display debug message if enabled."""
        if self.debug_enabled:
            print(f"DEBUG: {message}")
    
    def show_git_changes(self, changes_data: Dict):
        """Display git changes information."""
        print("\nFound staged changes:")
        print("-" * 30)
        
        for file_info in changes_data['files']:
            status_emoji = self._get_status_indicator(file_info['status'])
            print(f"{status_emoji} {file_info['path']} ({file_info['status']})")
        
        print(f"\nTotal files: {changes_data['total_files']}")
        print("-" * 30)
    
    def show_llm_status(self, status: Dict):
        """Display LLM connection status."""
        if status['connected']:
            if status['model_available']:
                self.show_success("Ollama connected and model ready")
            else:
                self.show_error(f"Model not available: {status['error']}")
                if status['available_models']:
                    print(f"Available models: {', '.join(status['available_models'])}")
        else:
            self.show_error(f"Ollama connection failed: {status['error']}")
    
    def show_generating_message(self):
        """Display message while generating suggestions."""
        print("Generating commit message suggestions...")
    
    def display_suggestions(self, suggestions: List[str]) -> Optional[str]:
        """
        Display commit suggestions and get user choice.
        
        Args:
            suggestions: List of commit message suggestions
            
        Returns:
            Selected commit message or None if cancelled
        """
        if not suggestions:
            self.show_error("No valid suggestions received")
            return None
        
        print("\n" + "=" * 60)
        print("Generated Commit Message Suggestions:")
        print("=" * 60)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        print("0. Cancel (don't commit)")
        print("=" * 60)
        
        return self._get_user_choice(len(suggestions))
    
    def confirm_commit(self, message: str) -> bool:
        """
        Confirm commit creation with user.
        
        Args:
            message: Commit message to confirm
            
        Returns:
            True if user confirms, False otherwise
        """
        print(f"\nReady to commit with message:")
        print(f"'{message}'")
        
        if self.config and self.config.auto_confirm:
            print("Auto-confirm enabled")
            return True
        
        response = input("\nProceed with commit? (y/N): ").strip().lower()
        return response in ['y', 'yes']
    
    def show_commit_result(self, commit_info: Dict):
        """Display commit creation result."""
        self.show_success("Commit created successfully!")
        print(f"{commit_info['hash']} - {commit_info['message']}")
        if self.debug_enabled:
            print(f"Author: {commit_info['author']}")
            print(f"Timestamp: {commit_info['timestamp']}")
    
    def show_recent_commits(self, commits: List[Dict]):
        """Display recent commits for context."""
        if not commits:
            return
        
        print("\nRecent commits (for context):")
        print("-" * 40)
        
        for commit in commits[:3]:  # Show only last 3
            print(f"{commit['hash']} - {commit['message'][:50]}...")
        
        print("-" * 40)
    
    def ask_yes_no(self, question: str, default: bool = False) -> bool:
        """
        Ask a yes/no question.
        
        Args:
            question: Question to ask
            default: Default answer if user just presses enter
            
        Returns:
            True for yes, False for no
        """
        default_text = "(Y/n)" if default else "(y/N)"
        response = input(f"{question} {default_text}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes']
    
    def handle_keyboard_interrupt(self):
        """Handle Ctrl+C gracefully."""
        print("\nOperation cancelled by user")
        sys.exit(0)
    
    def _get_user_choice(self, max_choice: int) -> Optional[str]:
        """Get user's choice from suggestions."""
        while True:
            try:
                choice_input = input(f"\nChoose a commit message (0-{max_choice}): ").strip()
                
                if choice_input == '0':
                    self.show_info("Commit cancelled")
                    return None
                
                try:
                    choice_num = int(choice_input)
                    if 1 <= choice_num <= max_choice:
                        # We need to return the actual suggestion, but we don't have access to it here
                        # This will be handled by the caller
                        return choice_input
                    else:
                        self.show_error(f"Please enter a number between 0 and {max_choice}")
                except ValueError:
                    self.show_error("Please enter a valid number")
                    
            except KeyboardInterrupt:
                self.handle_keyboard_interrupt()
            except EOFError:
                print("\nOperation cancelled")
                return None
    
    def _get_status_indicator(self, status: str) -> str:
        """Get text indicator for file status."""
        indicator_map = {
            'Added': '[+]',
            'Modified': '[M]', 
            'Deleted': '[D]',
            'Renamed': '[R]',
            'Copied': '[C]',
            'Type changed': '[T]'
        }
        return indicator_map.get(status, '[?]') 
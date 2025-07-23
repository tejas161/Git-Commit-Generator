#!/usr/bin/env python3
"""
AI-Powered Git Commit Generator - Main Application

Orchestrates all components to provide a seamless commit generation experience.
"""

import sys
from typing import Optional

# Handle import errors gracefully
try:
    from core import GitOperations, LLMClient, Config
    from ui import UserInterface
    from utils import validate_commit_message
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


class CommitGenerator:
    """Main application class that orchestrates commit generation."""
    
    def __init__(self, repo_path: str = "."):
        """Initialize the commit generator."""
        self.config = Config()
        self.git_ops = GitOperations(repo_path)
        self.llm_client = LLMClient(self.config)
        self.ui = UserInterface(self.config)
        
        # Validate configuration
        is_valid, error = self.config.validate()
        if not is_valid:
            self.ui.show_error(f"Configuration error: {error}")
            sys.exit(1)
    
    def run(self) -> None:
        """Main application flow."""
        try:
            self._run_workflow()
        except KeyboardInterrupt:
            self.ui.handle_keyboard_interrupt()
        except Exception as e:
            self.ui.show_error(f"Unexpected error: {str(e)}")
            if self.config.show_confidence:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    def _run_workflow(self) -> None:
        """Execute the main workflow steps."""
        # Step 1: Show header and validate environment
        self.ui.show_header()
        
        # Step 2: Validate git repository
        self.ui.show_step(1, 5, "Validating git repository...")
        if not self._validate_git_repository():
            return
        
        # Step 3: Check LLM availability
        self.ui.show_step(2, 5, "Checking AI model availability...")
        if not self._check_llm_availability():
            return
        
        # Step 4: Get and analyze git changes
        self.ui.show_step(3, 5, "Analyzing staged changes...")
        changes_data = self._get_git_changes()
        if not changes_data:
            return
        
        # Step 5: Generate commit suggestions
        self.ui.show_step(4, 5, "Generating AI commit suggestions...")
        suggestions = self._generate_suggestions(changes_data)
        if not suggestions:
            return
        
        # Step 6: Handle user selection and commit
        self.ui.show_step(5, 5, "Processing user selection...")
        self._handle_commit_process(suggestions)
    
    def _validate_git_repository(self) -> bool:
        """Validate that we're in a git repository with staged changes."""
        if not self.git_ops.is_git_repository():
            self.ui.show_error("Not a git repository!")
            self.ui.show_info("Please run this command from inside a git repository.")
            return False
        
        if not self.git_ops.has_staged_changes():
            self.ui.show_error("No staged changes found!")
            self.ui.show_info("Please stage some changes first:")
            self.ui.show_info("  git add <files>")
            self.ui.show_info("  git add .  # to stage all changes")
            return False
        
        self.ui.show_success("Git repository validated")
        return True
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM is available and ready."""
        status = self.llm_client.test_connection()
        self.ui.show_llm_status(status)
        
        if not status['connected']:
            self.ui.show_info("To fix this:")
            self.ui.show_info("  1. Start Ollama: ollama serve")
            self.ui.show_info("  2. Install model: ollama pull llama3.2:latest")
            return False
        
        if not status['model_available']:
            self.ui.show_info(f"Install the model: ollama pull {self.config.llm_model}")
            return False
        
        return True
    
    def _get_git_changes(self) -> Optional[dict]:
        """Get and display git changes."""
        try:
            changes_data = self.git_ops.get_staged_changes()
            
            if not changes_data:
                self.ui.show_error("No staged changes found")
                return None
            
            self.ui.show_git_changes(changes_data)
            
            # Show recent commits for context
            recent_commits = self.git_ops.get_recent_commits(3)
            if recent_commits:
                self.ui.show_recent_commits(recent_commits)
            
            return changes_data
            
        except Exception as e:
            self.ui.show_error(f"Failed to analyze git changes: {str(e)}")
            return None
    
    def _generate_suggestions(self, changes_data: dict) -> Optional[list]:
        """Generate commit message suggestions using LLM."""
        self.ui.show_generating_message()
        
        try:
            suggestions = self.llm_client.generate_commit_suggestions(changes_data['summary'])
            
            if not suggestions:
                self.ui.show_error("Failed to generate commit suggestions")
                self.ui.show_info("This could be due to:")
                self.ui.show_info("  - LLM request timeout")
                self.ui.show_info("  - Model overloaded")
                self.ui.show_info("  - Network connectivity issues")
                return None
            
            # Validate generated suggestions
            validated_suggestions = []
            for suggestion in suggestions:
                is_valid, error = validate_commit_message(suggestion)
                if is_valid:
                    validated_suggestions.append(suggestion)
                else:
                    self.ui.show_debug(f"Invalid suggestion filtered: {suggestion} ({error})")
            
            if not validated_suggestions:
                self.ui.show_error("No valid commit suggestions generated")
                return None
            
            self.ui.show_success(f"Generated {len(validated_suggestions)} commit suggestions")
            return validated_suggestions
            
        except Exception as e:
            self.ui.show_error(f"Failed to generate suggestions: {str(e)}")
            return None
    
    def _handle_commit_process(self, suggestions: list) -> None:
        """Handle user selection and commit creation."""
        # Display suggestions and get user choice
        choice_input = self.ui.display_suggestions(suggestions)
        
        if not choice_input:
            self.ui.show_info("Operation cancelled")
            return
        
        # Convert choice to suggestion
        try:
            choice_index = int(choice_input) - 1
            selected_message = suggestions[choice_index]
        except (ValueError, IndexError):
            self.ui.show_error("Invalid selection")
            return
        
        # Confirm commit
        if not self.ui.confirm_commit(selected_message):
            self.ui.show_info("Commit cancelled")
            return
        
        # Create commit
        try:
            commit_info = self.git_ops.create_commit(selected_message)
            self.ui.show_commit_result(commit_info)
            
        except Exception as e:
            self.ui.show_error(f"Failed to create commit: {str(e)}")


def main():
    """Entry point for the application."""
    # Parse command line arguments (if any)
    repo_path = "."
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    
    # Create and run the commit generator
    generator = CommitGenerator(repo_path)
    generator.run()


if __name__ == "__main__":
    main() 
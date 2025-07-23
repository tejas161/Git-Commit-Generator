#!/usr/bin/env python3
"""
Simple Git Commit Generator using Ollama LLM
Analyzes git changes and generates commit message suggestions using llama3.2
"""

import json
import os
import sys
import subprocess
from pathlib import Path

try:
    import requests
    from git import Repo, InvalidGitRepositoryError
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


class SimpleCommitGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.llm_model = "llama3.2:latest"
        
    def check_git_repo(self):
        """Check if we're in a git repository."""
        try:
            self.repo = Repo(".")
            return True
        except InvalidGitRepositoryError:
            print("❌ Not a git repository!")
            print("Please run this script from inside a git repository.")
            return False
    
    def get_git_changes(self):
        """Get staged git changes as a formatted string."""
        try:
            # Check if there are staged changes
            try:
                self.repo.head.commit
                # Repository has commits, compare against HEAD
                staged_changes = self.repo.index.diff("HEAD", cached=True)
            except ValueError:
                # No commits yet, check staged files directly
                staged_changes = self.repo.index.diff(None, cached=True)
            
            if not staged_changes:
                print("❌ No staged changes found!")
                print("Please stage some changes first: git add <files>")
                return None
            
            # Get detailed diff information
            changes_summary = []
            total_additions = 0
            total_deletions = 0
            
            for change in staged_changes:
                file_path = change.a_path or change.b_path
                change_type = change.change_type
                
                # Try to get line counts
                try:
                    diff_text = change.diff.decode('utf-8', errors='ignore')
                    additions = len([line for line in diff_text.split('\n') if line.startswith('+')])
                    deletions = len([line for line in diff_text.split('\n') if line.startswith('-')])
                    total_additions += additions
                    total_deletions += deletions
                except:
                    additions = deletions = 0
                
                changes_summary.append({
                    'file': file_path,
                    'type': change_type,
                    'additions': additions,
                    'deletions': deletions
                })
            
            # Format changes for LLM
            summary_text = f"Git Changes Summary:\n"
            summary_text += f"Total files changed: {len(changes_summary)}\n"
            summary_text += f"Total additions: {total_additions} lines\n"
            summary_text += f"Total deletions: {total_deletions} lines\n\n"
            summary_text += "Files changed:\n"
            
            for change in changes_summary:
                summary_text += f"- {change['file']} ({change['type']}) +{change['additions']} -{change['deletions']}\n"
            
            return summary_text
            
        except Exception as e:
            print(f"❌ Error getting git changes: {e}")
            return None
    
    def check_ollama_connection(self):
        """Check if Ollama is running and has the model."""
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                return False
                
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if self.llm_model not in model_names:
                print(f"❌ Model {self.llm_model} not found!")
                print("Available models:", model_names)
                print(f"Please install the model: ollama pull {self.llm_model}")
                return False
                
            return True
            
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama!")
            print("Please make sure Ollama is running: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
            return False
    
    def get_commit_suggestions(self, git_changes):
        """Get 5 commit message suggestions from LLM."""
        prompt = f"""Based on the following git changes, generate exactly 5 different conventional commit messages.

{git_changes}

Rules:
1. Use conventional commit format: type(scope)?: description
2. Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build
3. Keep descriptions under 50 characters
4. Make each suggestion unique and meaningful
5. Respond ONLY with 5 commit messages, one per line, no extra text

Example format:
feat(auth): add user login functionality
fix(api): resolve timeout issue in requests
docs: update installation instructions
refactor(utils): simplify error handling
test: add unit tests for user service"""

        try:
            print("🤖 Asking LLM for commit suggestions...")
            
            payload = {
                "model": self.llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 300
                }
            }
            
            response = requests.post(
                self.ollama_url, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ LLM request failed: {response.status_code}")
                return None
            
            result = response.json()
            suggestions_text = result.get('response', '').strip()
            
            # Parse suggestions (one per line)
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
            
            # Filter and clean suggestions
            clean_suggestions = []
            for suggestion in suggestions:
                # Remove any numbering or bullets
                suggestion = suggestion.strip()
                if suggestion and not suggestion.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')):
                    clean_suggestions.append(suggestion)
                elif ':' in suggestion:
                    # Remove numbering if present
                    if suggestion[0].isdigit():
                        suggestion = suggestion.split(' ', 1)[1] if ' ' in suggestion else suggestion[2:]
                    clean_suggestions.append(suggestion.strip())
            
            return clean_suggestions[:5]  # Ensure we only return max 5
            
        except requests.exceptions.Timeout:
            print("❌ LLM request timed out. Please try again.")
            return None
        except Exception as e:
            print(f"❌ Error getting LLM suggestions: {e}")
            return None
    
    def display_suggestions(self, suggestions):
        """Display commit suggestions and get user choice."""
        if not suggestions:
            print("❌ No valid suggestions received from LLM")
            return None
            
        print("\n" + "="*60)
        print("🚀 Generated Commit Message Suggestions:")
        print("="*60)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        print("0. Cancel (don't commit)")
        print("="*60)
        
        while True:
            try:
                choice = input(f"\nChoose a commit message (0-{len(suggestions)}): ").strip()
                
                if choice == '0':
                    print("🚫 Commit cancelled")
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(suggestions):
                    return suggestions[choice_num - 1]
                else:
                    print(f"❌ Please enter a number between 0 and {len(suggestions)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n🚫 Cancelled")
                return None
    
    def create_commit(self, message):
        """Create git commit with the chosen message."""
        try:
            print(f"\n📝 Creating commit with message: '{message}'")
            
            # Confirm before committing
            confirm = input("Proceed with commit? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("🚫 Commit cancelled")
                return False
            
            # Create the commit
            self.repo.index.commit(message)
            print("✅ Commit created successfully!")
            
            # Show the commit
            latest_commit = self.repo.head.commit
            print(f"📋 Commit: {latest_commit.hexsha[:8]} - {message}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating commit: {e}")
            return False
    
    def run(self):
        """Main execution flow."""
        print("🚀 Simple Git Commit Generator")
        print("=" * 50)
        
        # Step 1: Check git repository
        print("🔍 Checking git repository...")
        if not self.check_git_repo():
            return
        
        # Step 2: Check Ollama connection
        print("🔗 Checking Ollama connection...")
        if not self.check_ollama_connection():
            return
        
        # Step 3: Get git changes
        print("📊 Analyzing git changes...")
        git_changes = self.get_git_changes()
        if not git_changes:
            return
        
        print("✅ Found staged changes:")
        print(git_changes)
        
        # Step 4: Get LLM suggestions
        suggestions = self.get_commit_suggestions(git_changes)
        if not suggestions:
            return
        
        # Step 5: User selection
        chosen_message = self.display_suggestions(suggestions)
        if not chosen_message:
            return
        
        # Step 6: Create commit
        self.create_commit(chosen_message)


def main():
    """Entry point."""
    generator = SimpleCommitGenerator()
    generator.run()


if __name__ == "__main__":
    main() 
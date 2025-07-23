"""
LLM Client Module

Handles communication with Ollama for generating commit messages.
"""

import requests
from typing import List, Optional, Dict
from .config import Config


class LLMClient:
    """Client for interacting with Ollama LLM."""
    
    def __init__(self, config: Config = None):
        """Initialize LLM client with configuration."""
        self.config = config or Config()
        self.ollama_url = f"{self.config.ollama_base_url}/api/generate"
        self.model = self.config.llm_model
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            # Check if Ollama is running
            response = requests.get(
                f"{self.config.ollama_base_url}/api/tags", 
                timeout=5
            )
            
            if response.status_code != 200:
                return False
            
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            return self.model in model_names
            
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = requests.get(
                f"{self.config.ollama_base_url}/api/tags", 
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            
        except Exception:
            pass
        
        return []
    
    def generate_commit_suggestions(self, git_summary: str) -> Optional[List[str]]:
        """
        Generate commit message suggestions based on git changes.
        
        Args:
            git_summary: Formatted summary of git changes
            
        Returns:
            List of commit message suggestions or None if failed
        """
        prompt = self._create_prompt(git_summary)
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "max_tokens": self.config.max_tokens
                }
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=self.config.request_timeout
            )
            
            if response.status_code != 200:
                return None
            
            result = response.json()
            suggestions_text = result.get('response', '').strip()
            
            # Parse and clean suggestions
            suggestions = self._parse_suggestions(suggestions_text)
            
            return suggestions[:self.config.max_suggestions]
            
        except requests.exceptions.Timeout:
            return None
        except Exception:
            return None
    
    def _create_prompt(self, git_summary: str) -> str:
        """Create optimized prompt for commit message generation."""
        prompt = f"""Based on the following git changes, generate exactly {self.config.max_suggestions} different conventional commit messages.

{git_summary}

Requirements:
1. Use conventional commit format: type(scope): description
2. Valid types: feat, fix, docs, style, refactor, test, chore, perf, ci, build
3. Keep descriptions under 50 characters  
4. Make each suggestion unique and meaningful
5. Respond with ONLY the commit messages, one per line
6. No numbering, bullets, or extra text

Examples:
feat(auth): add user login functionality
fix(api): resolve timeout issue in requests
docs: update installation instructions
refactor(utils): simplify error handling
test: add unit tests for user service"""

        return prompt
    
    def _parse_suggestions(self, response_text: str) -> List[str]:
        """
        Parse and clean LLM response into commit message suggestions.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            List of cleaned commit messages
        """
        # Split by lines and filter empty lines
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        
        cleaned_suggestions = []
        
        for line in lines:
            # Remove common prefixes (numbering, bullets)
            cleaned_line = line
            
            # Remove numbering like "1. ", "2. ", etc.
            if line and line[0].isdigit() and '. ' in line:
                cleaned_line = line.split('. ', 1)[1]
            
            # Remove bullet points
            elif line.startswith(('- ', '* ', '• ')):
                cleaned_line = line[2:]
            
            # Only keep lines that look like commit messages (contain ':')
            if ':' in cleaned_line and len(cleaned_line) > 10:
                cleaned_suggestions.append(cleaned_line.strip())
        
        return cleaned_suggestions
    
    def test_connection(self) -> Dict[str, any]:
        """
        Test connection to Ollama and return status information.
        
        Returns:
            Dict with connection status and details
        """
        status = {
            'connected': False,
            'model_available': False,
            'available_models': [],
            'error': None
        }
        
        try:
            # Test basic connection
            response = requests.get(
                f"{self.config.ollama_base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code != 200:
                status['error'] = f"Ollama responded with status {response.status_code}"
                return status
            
            status['connected'] = True
            
            # Get available models
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            status['available_models'] = model_names
            
            # Check if our specific model is available  
            status['model_available'] = self.model in model_names
            
            if not status['model_available']:
                status['error'] = f"Model '{self.model}' not found"
            
        except requests.exceptions.ConnectionError:
            status['error'] = "Cannot connect to Ollama (is 'ollama serve' running?)"
        except Exception as e:
            status['error'] = f"Unexpected error: {str(e)}"
        
        return status 
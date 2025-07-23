"""
Configuration Module

Centralized configuration for the commit generator.
"""

import os
from typing import Optional


class Config:
    """Configuration settings for the commit generator from AI Model."""
    
    def __init__(self):
        """Initialize configuration with defaults and environment overrides."""
        
        # Ollama settings
        self.ollama_base_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.llm_model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        
        # LLM generation parameters
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        self.top_p = float(os.getenv('LLM_TOP_P', '0.9'))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '300'))
        self.max_suggestions = int(os.getenv('MAX_SUGGESTIONS', '5'))
        
        # Request settings
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Git settings
        self.default_repo_path = os.getenv('DEFAULT_REPO_PATH', '.')
        
        # UI settings
        self.show_confidence = os.getenv('SHOW_CONFIDENCE', 'false').lower() == 'true'
        self.auto_confirm = os.getenv('AUTO_CONFIRM', 'false').lower() == 'true'
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration settings.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate temperature range
        if not 0.0 <= self.temperature <= 2.0:
            return False, f"Temperature must be between 0.0 and 2.0, got {self.temperature}"
        
        # Validate top_p range
        if not 0.0 <= self.top_p <= 1.0:
            return False, f"Top_p must be between 0.0 and 1.0, got {self.top_p}"
        
        # Validate max_suggestions
        if not 1 <= self.max_suggestions <= 10:
            return False, f"Max suggestions must be between 1 and 10, got {self.max_suggestions}"
        
        # Validate timeout
        if self.request_timeout < 1:
            return False, f"Request timeout must be positive, got {self.request_timeout}"
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'ollama_base_url': self.ollama_base_url,
            'llm_model': self.llm_model,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens,
            'max_suggestions': self.max_suggestions,
            'request_timeout': self.request_timeout,
            'default_repo_path': self.default_repo_path,
            'show_confidence': self.show_confidence,
            'auto_confirm': self.auto_confirm
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        lines = []
        for key, value in config_dict.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines) 
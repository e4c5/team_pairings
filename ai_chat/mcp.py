"""
MCP (Model Context Protocol) processor for AI chat functionality.
Handles integration with various LLM providers.
"""
import time
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
import requests
import json

logger = logging.getLogger(__name__)


class MCPProcessor:
    """
    Main processor for handling LLM requests through various providers.
    Configurable via Django settings.
    """
    
    def __init__(self):
        self.provider = getattr(settings, 'AI_CHAT_PROVIDER', 'openai')
        self.api_key = getattr(settings, 'AI_CHAT_API_KEY', None)
        self.model = getattr(settings, 'AI_CHAT_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = getattr(settings, 'AI_CHAT_MAX_TOKENS', 150)
        self.temperature = getattr(settings, 'AI_CHAT_TEMPERATURE', 0.7)
        
        if not self.api_key:
            logger.warning("AI_CHAT_API_KEY not configured in settings")

    def process_message(self, message: str, chat_history: List[Dict] = None) -> Tuple[str, Dict]:
        """
        Process a user message and return AI response with metadata.
        
        Args:
            message: User's input message
            chat_history: Previous messages for context (optional)
            
        Returns:
            Tuple of (response_text, metadata_dict)
        """
        start_time = time.time()
        
        try:
            if self.provider == 'openai':
                response, metadata = self._process_openai(message, chat_history)
            elif self.provider == 'anthropic':
                response, metadata = self._process_anthropic(message, chat_history)
            elif self.provider == 'mock':
                response, metadata = self._process_mock(message, chat_history)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
            metadata['response_time'] = time.time() - start_time
            metadata['model_used'] = self.model
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Error processing message with {self.provider}: {str(e)}")
            error_response = "I'm sorry, I encountered an error processing your request. Please try again."
            metadata = {
                'error': str(e),
                'response_time': time.time() - start_time,
                'model_used': self.model
            }
            return error_response, metadata

    def _process_openai(self, message: str, chat_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Process message using OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build conversation history
        messages = []
        if chat_history:
            for msg in chat_history[-10:]:  # Keep last 10 messages for context
                role = "user" if msg.get('is_user', True) else "assistant"
                messages.append({"role": role, "content": msg['content']})
        
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        metadata = {
            'tokens_used': result.get('usage', {}).get('total_tokens', 0),
            'provider': 'openai'
        }
        
        return ai_response, metadata

    def _process_anthropic(self, message: str, chat_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Process message using Anthropic Claude API"""
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Build conversation for Claude
        messages = []
        if chat_history:
            for msg in chat_history[-10:]:
                role = "user" if msg.get('is_user', True) else "assistant"
                messages.append({"role": role, "content": msg['content']})
        
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['content'][0]['text']
        
        metadata = {
            'tokens_used': result.get('usage', {}).get('input_tokens', 0) + result.get('usage', {}).get('output_tokens', 0),
            'provider': 'anthropic'
        }
        
        return ai_response, metadata

    def _process_mock(self, message: str, chat_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Mock processor for testing and development"""
        # Simple mock responses for testing
        responses = [
            f"Thank you for your message: '{message}'. This is a mock AI response.",
            f"I understand you said '{message}'. How can I help you further?",
            f"Regarding '{message}', I'm a mock AI assistant and this is a test response.",
            f"You mentioned '{message}'. As a mock AI, I'm here to help with your tournament questions!"
        ]
        
        # Use hash of message to get consistent response for same input
        response_index = hash(message) % len(responses)
        ai_response = responses[response_index]
        
        metadata = {
            'tokens_used': len(message.split()) + len(ai_response.split()),
            'provider': 'mock'
        }
        
        return ai_response, metadata

    def validate_configuration(self) -> Dict[str, bool]:
        """Validate the current configuration"""
        validation = {
            'provider_supported': self.provider in ['openai', 'anthropic', 'mock'],
            'api_key_configured': bool(self.api_key) or self.provider == 'mock',
            'model_configured': bool(self.model)
        }
        
        validation['is_valid'] = all(validation.values())
        return validation
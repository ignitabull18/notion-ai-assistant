"""OpenAI integration for Jungle Scout AI Assistant"""
import os
from typing import Dict, List, Optional, Any
from openai import OpenAI
from jungle_scout_ai.logging import logger
from jungle_scout_ai.retry import with_retry


class LLMCallerOpenAI:
    """Handles LLM calls using OpenAI directly for Jungle Scout AI Assistant"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set")
            
        self.client = OpenAI(api_key=self.api_key)
    
    @with_retry(max_attempts=3)
    def call(
        self,
        messages: List[Dict[str, str]],
        model: str = "o3",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Make a call to OpenAI for Jungle Scout analysis
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments for the API
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            raise


# Convenience function for backward compatibility
def call_llm(messages: List[Dict[str, str]], **kwargs) -> str:
    """Call OpenAI for Jungle Scout analysis"""
    caller = LLMCallerOpenAI()
    return caller.call(messages, **kwargs)
"""
LLM Client - Abstraction layer for LLM API calls.

Design philosophy:
- Provider-agnostic (Groq, OpenAI, Anthropic)
- Automatic retries with exponential backoff
- Structured output parsing
- Cost tracking
- Error handling

Why this exists:
- DRY: Reusable across all agents
- Reliability: Handles transient failures
- Observability: Logs all LLM calls
- Maintainability: Easy to swap providers
"""

from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from .config import get_settings


# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)


class LLMClient:
    """
    Universal LLM client supporting multiple providers.
    
    Usage:
        client = LLMClient()
        response = await client.generate(
            system_prompt="You are a legal AI...",
            user_prompt="Analyze this clause...",
            response_model=Answer
        )
    
    Features:
    - Automatic provider selection from config
    - Structured output (Pydantic models)
    - Retry logic for transient failures
    - Token counting and cost tracking
    """
    
    def __init__(self):
        """
        Initialize LLM client based on config.
        
        Design decision: Lazy initialization.
        - Don't fail at import time
        - Fail at call time with clear error
        """
        self.settings = get_settings()
        self._llm = None
        self._provider = None
    
    def _get_llm(self):
        """
        Get LLM instance (lazy initialization).
        
        Why lazy:
        - Faster imports
        - Better error messages (fail when actually needed)
        - Can mock in tests
        """
        if self._llm is not None:
            return self._llm
        
        provider = self.settings.llm_provider
        model = self.settings.llm_model
        temperature = self.settings.llm_temperature
        
        logger.info(f"Initializing LLM: {provider}/{model} (temp={temperature})")
        
        # Create LLM based on provider
        if provider == "groq":
            if not self.settings.groq_api_key:
                raise ValueError(
                    "GROQ_API_KEY not set in .env file. "
                    "Get your free key at: https://console.groq.com/keys"
                )
            self._llm = ChatGroq(
                api_key=self.settings.groq_api_key,
                model_name=model,
                temperature=temperature,
                max_tokens=2000,  # Enough for detailed legal answers
            )
            self._provider = "groq"
        
        elif provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in .env file")
            self._llm = ChatOpenAI(
                api_key=self.settings.openai_api_key,
                model_name=model,
                temperature=temperature,
                max_tokens=2000,
            )
            self._provider = "openai"
        
        elif provider == "anthropic":
            if not self.settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in .env file")
            self._llm = ChatAnthropic(
                api_key=self.settings.anthropic_api_key,
                model_name=model,
                temperature=temperature,
                max_tokens=2000,
            )
            self._provider = "anthropic"
        
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                f"Supported: groq, openai, anthropic"
            )
        
        return self._llm
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Optional[Type[T]] = None,
        max_tokens: Optional[int] = None,
    ) -> T | dict:
        """
        Generate LLM response with structured output.
        
        Args:
            system_prompt: System message (role, instructions)
            user_prompt: User message (query, context)
            response_model: Pydantic model for structured output
            max_tokens: Override default max tokens
        
        Returns:
            Pydantic model instance or dict
        
        Raises:
            ValueError: Invalid configuration
            TimeoutError: LLM request timeout (after retries)
            Exception: Other LLM errors
        
        Design decisions:
        - Use messages format (system + user) → Clear role separation
        - Return Pydantic models → Type safety
        - Retry on transient errors → Reliability
        - Log everything → Observability
        
        Example:
            answer = await client.generate(
                system_prompt="You are a legal AI",
                user_prompt="Analyze this: ...",
                response_model=Answer
            )
        """
        llm = self._get_llm()
        
        # Override max_tokens if specified
        if max_tokens:
            llm.max_tokens = max_tokens
        
        # Build messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        # Log the request (truncated for readability)
        logger.debug(
            f"LLM Request: provider={self._provider}, "
            f"model={self.settings.llm_model}, "
            f"system_prompt_len={len(system_prompt)}, "
            f"user_prompt_len={len(user_prompt)}"
        )
        
        try:
            # Call LLM
            response = await llm.ainvoke(messages)
            
            # Extract content
            content = response.content
            
            logger.debug(f"LLM Response received: {len(content)} chars")
            
            # Parse structured output if model provided
            if response_model:
                parser = JsonOutputParser(pydantic_object=response_model)
                try:
                    # Try to parse as JSON
                    parsed = parser.parse(content)
                    # Validate with Pydantic
                    try:
                        result = response_model(**parsed)
                    except ValidationError as ve:
                        # Opportunistic repair: some models occasionally omit required fields.
                        # We only apply narrow, low-risk defaults for known fields.
                        repaired = dict(parsed) if isinstance(parsed, dict) else parsed
                        if isinstance(repaired, dict):
                            missing_fields = {
                                err.get("loc", [None])[0]
                                for err in ve.errors()
                                if err.get("type") == "missing"
                            }
                            if "severity" in missing_fields and "severity" in getattr(response_model, "model_fields", {}):
                                repaired["severity"] = "moderate"
                                logger.warning(
                                    f"Auto-repaired missing field 'severity' for {response_model.__name__} "
                                    f"(defaulted to 'moderate')."
                                )
                            result = response_model(**repaired)
                        else:
                            raise
                    logger.info(f"Successfully parsed response as {response_model.__name__}")
                    return result
                except Exception as e:
                    # Try to fix common JSON errors (missing commas, trailing commas, etc.)
                    logger.warning(f"Initial parse failed, attempting to fix JSON: {e}")
                    try:
                        import json
                        import re
                        
                        # Try to extract JSON from markdown code blocks
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                        if json_match:
                            content = json_match.group(1)
                        elif re.search(r'```\s*(\{.*?\})\s*```', content, re.DOTALL):
                            json_match = re.search(r'```\s*(\{.*?\})\s*```', content, re.DOTALL)
                            content = json_match.group(1)
                        
                        # Try direct JSON parse (sometimes works when parser doesn't)
                        parsed = json.loads(content)
                        try:
                            result = response_model(**parsed)
                        except ValidationError as ve:
                            repaired = dict(parsed) if isinstance(parsed, dict) else parsed
                            if isinstance(repaired, dict):
                                missing_fields = {
                                    err.get("loc", [None])[0]
                                    for err in ve.errors()
                                    if err.get("type") == "missing"
                                }
                                if "severity" in missing_fields and "severity" in getattr(response_model, "model_fields", {}):
                                    repaired["severity"] = "moderate"
                                    logger.warning(
                                        f"Auto-repaired missing field 'severity' for {response_model.__name__} "
                                        f"(defaulted to 'moderate')."
                                    )
                                result = response_model(**repaired)
                            else:
                                raise
                        logger.info(f"Successfully parsed response as {response_model.__name__} after fixes")
                        return result
                    except Exception as e2:
                        logger.error(f"Failed to parse LLM output as {response_model.__name__}: {e}")
                        logger.debug(f"Raw output: {content[:500]}...")
                        raise ValueError(
                            f"LLM returned invalid format. Expected {response_model.__name__}. "
                            f"Error: {e}"
                        )
            else:
                # Return raw dict
                try:
                    parser = JsonOutputParser()
                    return parser.parse(content)
                except:
                    # If not JSON, return as text
                    return {"text": content}
        
        except Exception as e:
            logger.error(f"LLM generation failed: {type(e).__name__}: {e}")
            raise
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).
        
        Why approximate:
        - Different models have different tokenizers
        - Exact counting requires model-specific libraries
        - Rough estimate is good enough for planning
        
        Rule of thumb: ~4 chars per token for English
        """
        return len(text) // 4
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost based on provider and model.
        
        Why this matters:
        - Track spend per query
        - Optimize expensive operations
        - Alert on cost anomalies
        
        Groq pricing (per 1M tokens):
        - Llama 3.1 70B: $0.59 input, $0.79 output
        - Llama 3.1 8B: $0.05 input, $0.08 output
        - Mixtral 8x7B: $0.24 input, $0.24 output
        """
        if self._provider == "groq":
            if "70b" in self.settings.llm_model.lower():
                return (input_tokens * 0.59 + output_tokens * 0.79) / 1_000_000
            elif "8b" in self.settings.llm_model.lower():
                return (input_tokens * 0.05 + output_tokens * 0.08) / 1_000_000
            elif "mixtral" in self.settings.llm_model.lower():
                return (input_tokens * 0.24 + output_tokens * 0.24) / 1_000_000
        elif self._provider == "openai":
            if "gpt-4" in self.settings.llm_model.lower():
                return (input_tokens * 10 + output_tokens * 30) / 1_000_000
            elif "gpt-3.5" in self.settings.llm_model.lower():
                return (input_tokens * 0.5 + output_tokens * 1.5) / 1_000_000
        
        return 0.0  # Unknown, assume free


# Singleton instance
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get LLM client singleton.
    
    Why singleton:
    - Reuse connection pools
    - Share rate limit state
    - Consistent configuration
    """
    global _client
    if _client is None:
        _client = LLMClient()
    return _client

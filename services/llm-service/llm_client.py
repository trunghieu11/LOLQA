"""LLM Client - Abstracts different LLM backends"""
import httpx
from typing import List, Optional, Dict, Any
from shared.common.logging import logger
from shared.common.config import LLMServiceConfig
from shared.common.models import ChatResponse, EmbeddingResponse
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class LLMClient:
    """Client for LLM operations supporting multiple backends"""
    
    def __init__(self, config: LLMServiceConfig):
        """
        Initialize LLM client.
        
        Args:
            config: LLM service configuration
        """
        self.config = config
        self.backend = config.backend
        
        if self.backend == "openai":
            self._init_openai()
        elif self.backend == "vllm":
            self._init_vllm()
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if not self.config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI backend")
        
        self.chat_llm = ChatOpenAI(
            model=self.config.default_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.config.openai_api_key
        )
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.config.openai_api_key
        )
        
        logger.info("Initialized OpenAI client")
    
    def _init_vllm(self):
        """Initialize vLLM client (OpenAI-compatible API)"""
        if not self.config.vllm_endpoint:
            raise ValueError("VLLM_ENDPOINT is required for vLLM backend")
        
        # vLLM uses OpenAI-compatible API
        self.chat_llm = ChatOpenAI(
            model=self.config.default_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            base_url=self.config.vllm_endpoint,
            api_key="dummy"  # vLLM doesn't require real API key
        )
        
        # For embeddings, we might need a separate endpoint or use OpenAI
        # For now, fallback to OpenAI embeddings
        if self.config.openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=self.config.openai_api_key
            )
        else:
            logger.warning("No OpenAI API key for embeddings, vLLM embeddings not yet supported")
            self.embeddings = None
        
        logger.info(f"Initialized vLLM client with endpoint: {self.config.vllm_endpoint}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """
        Generate chat completion.
        
        Args:
            messages: List of messages with role and content
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Returns:
            Chat response
        """
        try:
            # Convert messages to LangChain format
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            langchain_messages = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
                elif role == "system":
                    langchain_messages.append(SystemMessage(content=content))
            
            # Override config if provided
            llm = self.chat_llm
            if model or temperature is not None or max_tokens:
                llm_kwargs = {}
                if model:
                    llm_kwargs["model"] = model
                if temperature is not None:
                    llm_kwargs["temperature"] = temperature
                if max_tokens:
                    llm_kwargs["max_tokens"] = max_tokens
                
                # Create new instance with overrides
                if self.backend == "openai":
                    llm = ChatOpenAI(
                        api_key=self.config.openai_api_key,
                        **llm_kwargs
                    )
                else:  # vllm
                    llm = ChatOpenAI(
                        base_url=self.config.vllm_endpoint,
                        api_key="dummy",
                        **llm_kwargs
                    )
            
            # Generate response
            response = await llm.ainvoke(langchain_messages)
            
            content = response.content if hasattr(response, 'content') else str(response)
            
            return ChatResponse(
                content=content,
                model=model or self.config.default_model,
                usage=None  # OpenAI SDK doesn't always provide usage in response object
            )
        except Exception as e:
            logger.error(f"Error in chat completion: {e}", exc_info=True)
            raise
    
    async def embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> EmbeddingResponse:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            model: Optional model override
            
        Returns:
            Embedding response
        """
        if not self.embeddings:
            raise ValueError("Embeddings not available for current backend configuration")
        
        try:
            # Generate embeddings
            embedding_vectors = await self.embeddings.aembed_documents(texts)
            
            return EmbeddingResponse(
                embeddings=embedding_vectors,
                model=model or "text-embedding-3-small"
            )
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}", exc_info=True)
            raise
    
    async def list_models(self) -> List[str]:
        """List available models"""
        if self.backend == "openai":
            # Return common OpenAI models
            return [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ]
        elif self.backend == "vllm":
            # vLLM models depend on what's deployed
            # This would typically be fetched from the vLLM endpoint
            return [self.config.default_model]
        else:
            return []


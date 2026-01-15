"""LLM service for answer generation using Groq."""
from groq import Groq
from typing import List, Dict, Tuple
import re


class LLMService:
    """Service for generating answers using Groq LLM."""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.1,
        max_tokens: int = 1000
    ):
        """
        Initialize the LLM service.
        
        Args:
            api_key: Groq API key
            model: LLM model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate_answer(
        self, 
        query: str, 
        contexts: List[Dict]
    ) -> Tuple[str, bool]:
        """
        Generate an answer based on query and context.
        
        Args:
            query: User query
            contexts: List of context documents
            
        Returns:
            Tuple of (answer, has_answer)
        """
        # Build context string with citations
        context_str = self._build_context_string(contexts)
        
        # Build prompt
        prompt = self._build_prompt(query, context_str)
        
        # Generate answer
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context. Always cite your sources using [1], [2], etc."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Check if the model said it doesn't know
            has_answer = not self._is_no_answer(answer)
            
            return answer, has_answer
            
        except Exception as e:
            return f"Error generating answer: {str(e)}", False
    
    def _build_context_string(self, contexts: List[Dict]) -> str:
        """Build a formatted context string from documents."""
        context_parts = []
        for idx, context in enumerate(contexts, 1):
            text = context.get("text", "")
            source = context.get("source", "Unknown")
            title = context.get("title", "")
            
            context_part = f"[{idx}] "
            if title:
                context_part += f"{title} - "
            if source:
                context_part += f"({source}): "
            context_part += text
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build the prompt for the LLM."""
        prompt = f"""Answer the following question based on the provided context. Use inline citations like [1], [2] to reference the sources.

Context:
{context}

Question: {query}

Instructions:
1. Answer the question using ONLY information from the context above
2. Cite your sources using [1], [2], etc. corresponding to the context numbers
3. If you cannot answer the question based on the context, say "I don't have enough information to answer this question."
4. Be concise but complete in your answer
5. Use multiple citations if information comes from multiple sources

Answer:"""
        
        return prompt
    
    def _is_no_answer(self, answer: str) -> bool:
        """Check if the answer indicates no information available."""
        no_answer_phrases = [
            "i don't have enough information",
            "i cannot answer",
            "not enough information",
            "unable to answer",
            "cannot determine",
            "don't know",
            "insufficient information"
        ]
        
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in no_answer_phrases)
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> Dict:
        """
        Estimate cost for the LLM call.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            
        Returns:
            Dictionary with cost information
        """
        # Groq is free during beta, but we'll estimate as if using standard pricing
        # Standard pricing approximation: $0.0001 per 1K tokens
        
        prompt_cost = (prompt_tokens / 1000) * 0.0001
        completion_cost = (completion_tokens / 1000) * 0.0001
        total_cost = prompt_cost + completion_cost
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost_usd": round(total_cost, 6),
            "note": "Groq is currently free during beta"
        }

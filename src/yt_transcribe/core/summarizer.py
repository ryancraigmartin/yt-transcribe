"""
AI-powered summarization using Ollama.

Connects to a local Ollama instance to generate specialized summaries
based on prompt templates.

TypeScript Context:
- Similar to calling OpenAI or Anthropic API
- Uses async/await pattern like in Node.js
- Type hints for request/response similar to API client types
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..prompt_templates import PromptTemplate


@dataclass
class SummaryResult:
    """
    Result of summarization.

    TypeScript Equivalent:
        interface SummaryResult {
            summary: string;
            rawResponse: string;
            model: string;
            tokensUsed?: number;
        }
    """

    summary: str
    raw_response: str
    model: str
    tokens_used: Optional[int] = None


class SummarizationError(Exception):
    """Raised when summarization fails."""

    pass


class OllamaSummarizer:
    """
    Summarizer using local Ollama instance.

    Ollama runs LLMs locally, ensuring:
    - Complete data privacy (no external API calls)
    - Zero recurring costs
    - Fast processing with local GPU

    TypeScript Context:
        Similar to an API client class:
        class OllamaSummarizer {
            constructor(private baseUrl: string, private model: string) {}
            async summarize(text: string, template: Template): Promise<Summary> {}
        }
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama summarizer.

        Args:
            base_url: Ollama API base URL
            model: Model name to use (e.g., 'llama2', 'mistral')
        """
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def check_connection(self) -> bool:
        """
        Check if Ollama is running and accessible.

        Returns:
            bool: True if Ollama is available, False otherwise

        TypeScript Equivalent:
            async checkConnection(): Promise<boolean> {
                try {
                    await fetch(`${this.baseUrl}/api/tags`)
                    return true
                } catch {
                    return false
                }
            }
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    async def list_models(self) -> list[str]:
        """
        Get list of available models from Ollama.

        Returns:
            list[str]: List of model names

        Raises:
            SummarizationError: If unable to fetch models
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise SummarizationError(f"Failed to fetch models: {response.status}")

                    data = await response.json()
                    return [model["name"] for model in data.get("models", [])]

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise SummarizationError(f"Failed to connect to Ollama: {e}")

    async def summarize(
        self,
        transcription: str,
        template: PromptTemplate,
        video_title: Optional[str] = None,
    ) -> SummaryResult:
        """
        Generate summary using Ollama.

        Args:
            transcription: Full transcription text
            template: Prompt template to use
            video_title: Optional video title for context

        Returns:
            SummaryResult: Generated summary

        Raises:
            SummarizationError: If summarization fails

        TypeScript Context:
            Similar to calling an LLM API:
            async summarize(text: string, template: Template): Promise<Summary> {
                const response = await fetch(this.url, {
                    method: 'POST',
                    body: JSON.stringify({
                        model: this.model,
                        messages: [
                            { role: 'system', content: template.systemPrompt },
                            { role: 'user', content: text }
                        ]
                    })
                })
                return response.json()
            }
        """
        # Build prompt
        user_prompt = f"Video Title: {video_title}\n\n" if video_title else ""
        user_prompt += f"Transcription:\n\n{transcription}\n\n"
        user_prompt += "Please provide a comprehensive summary following the specified format."

        # Prepare request
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": template.system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,  # Get complete response at once
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300),  # 5 minutes max
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise SummarizationError(
                            f"Ollama API error {response.status}: {error_text}"
                        )

                    data = await response.json()

                    # Extract response
                    message = data.get("message", {})
                    content = message.get("content", "")

                    if not content:
                        raise SummarizationError("Empty response from Ollama")

                    # Extract token usage if available
                    tokens_used = None
                    if "prompt_eval_count" in data and "eval_count" in data:
                        tokens_used = data["prompt_eval_count"] + data["eval_count"]

                    return SummaryResult(
                        summary=content,
                        raw_response=content,
                        model=self.model,
                        tokens_used=tokens_used,
                    )

        except asyncio.TimeoutError:
            raise SummarizationError("Summarization timed out (max 5 minutes)")
        except aiohttp.ClientError as e:
            raise SummarizationError(f"Failed to connect to Ollama: {e}")
        except KeyError as e:
            raise SummarizationError(f"Unexpected response format: {e}")


def create_summarizer(
    base_url: Optional[str] = None, model: Optional[str] = None
) -> OllamaSummarizer:
    """
    Factory function to create an Ollama summarizer.

    Args:
        base_url: Optional custom Ollama URL
        model: Optional custom model name

    Returns:
        OllamaSummarizer: Configured summarizer

    TypeScript Context:
        Factory function pattern:
        const createSummarizer = (config?: SummarizerConfig): Summarizer => {
            return new OllamaSummarizer(
                config?.baseUrl ?? DEFAULT_URL,
                config?.model ?? DEFAULT_MODEL
            )
        }
    """
    return OllamaSummarizer(
        base_url=base_url or "http://localhost:11434",
        model=model or "llama2",
    )

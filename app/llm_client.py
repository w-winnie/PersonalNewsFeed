import os
from openai import OpenAI
import logging
from src.token_utils import estimate_openai_cost

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key=None, model="gpt-4o-mini", temperature=0.5):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No OpenAI API key provided")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature

    def chat(self, messages, return_cost_info=False):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            choice = response.choices[0]
            content = choice.message.content

            usage = response.usage
            tokens_prompt = usage.prompt_tokens
            tokens_completion = usage.completion_tokens

            cost_info = estimate_openai_cost(self.model, tokens_prompt, tokens_completion)

            if return_cost_info:
                return content, cost_info

            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "Error: " + str(e)

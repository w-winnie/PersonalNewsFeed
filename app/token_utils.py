# app/token_utils.py

MODEL_PRICING = {
    "gpt-4": {
        "input": 0.01,   # $0.01 per 1K tokens
        "output": 0.03   # $0.03 per 1K tokens
    },
    "gpt-4-1106-preview": {
        "input": 0.01,
        "output": 0.03
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,
        "output": 0.002
    },
    "gpt-4o": {
        "input": 0.005,
        "output": 0.015
    },
    "gpt-4o-mini": {
        "input": 0.00015,
        "output": 0.00060
    }
}


def estimate_openai_cost(model_name, prompt_tokens, completion_tokens):
    pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["gpt-4"])  # default fallback

    input_cost = (prompt_tokens / 1000) * pricing["input"]
    output_cost = (completion_tokens / 1000) * pricing["output"]
    total_cost = round(input_cost + output_cost, 6)

    return total_cost
    # {
    #     "prompt_tokens": prompt_tokens,
    #     "completion_tokens": completion_tokens,
    #     "total_tokens": prompt_tokens + completion_tokens,
    #     "estimated_cost_usd": total_cost
    # }

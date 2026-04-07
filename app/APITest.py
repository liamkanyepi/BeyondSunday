from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

response = client.chat.completions.create(
    model="openai/gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}],
)

print(response)
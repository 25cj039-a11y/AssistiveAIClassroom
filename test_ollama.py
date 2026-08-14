from ollama import chat

response = chat(
    model="qwen2.5:1.5b",
    messages=[
        {
            "role": "user",
            "content": "Say hello to the Accessible Classroom Assistant."
        }
    ]
)

print(response.message.content)
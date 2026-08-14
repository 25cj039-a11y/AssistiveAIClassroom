from ollama import chat


def analyze_classroom_text(text):
    response = chat(
        model="qwen2.5:1.5b",
        messages=[
            {
                "role": "system",
                "content": """
You are an accessibility assistant for a classroom.

Read the teacher's statement and identify important information.

Look specifically for:
- assignments
- deadlines
- exams or tests
- dates
- times
- important announcements

Keep the response short and clear.
If there is no important information, say:
No important information detected.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.message.content


text = input("Enter classroom speech text: ")

result = analyze_classroom_text(text)

print("\nImportant classroom information:")
print(result)
from ollama import chat 

def ai_chat(messages):
    response = chat(
        model="gemma4:e4b",
        messages=messages,
        think=False
    )

    return response["message"]["content"]
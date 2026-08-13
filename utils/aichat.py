from ollama import chat 

def ai_chat(messages):
    response = chat(
        model="",
        messages=messages,
        think=False
    )

    return response["message"]["content"]

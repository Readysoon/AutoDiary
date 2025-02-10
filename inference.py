import subprocess

conversation_history = []  # Stores conversation history

def run_ollama(input_text):
    global conversation_history

    # Combine conversation history with new input
    full_input = "\n".join(conversation_history + [input_text])

    command = ["ollama", "run", "llama3.2", full_input]

    result = subprocess.run(
        command, 
        capture_output=True, 
        text=True, 
        encoding="utf-8"
    )

    model_response = result.stdout.strip()

    # Append user input and model response to history
    conversation_history.append(f"User: {input_text}")
    conversation_history.append(f"Llama: {model_response}")

    print("\nModel Output:", model_response)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    run_ollama(user_input)

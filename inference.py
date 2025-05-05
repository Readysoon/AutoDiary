import subprocess

# make sure to start ollama via 'brew services start ollama'

conversation_history = []  # Stores conversation history

def load_conversation_history(file_path):
    global conversation_history
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            conversation_history = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {file_path}. Starting with an empty conversation history.")
    except Exception as e:
        print(f"An error occurred while loading the conversation history: {e}")

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

def main():
    # Load conversation history from a text file
    load_conversation_history('_chat_2.txt')  # Replace 'chat.txt' with your file path

    with open('_chat_2.txt', 'r') as file:
        for line in file:
            cleaned_line = line.replace('\u200e', '').strip()
            print(cleaned_line)


    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        run_ollama(user_input)

if __name__ == "__main__":
    main()

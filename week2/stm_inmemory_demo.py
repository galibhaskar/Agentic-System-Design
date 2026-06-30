from memory import STMInMemory
from helpers import load_env_vars

load_env_vars.load()  # Load environment variables from .env file

if __name__ == "__main__":
    stm_memory = STMInMemory()

    print("Short-term memory demo — full history is sent on every call.")
    print("Type 'exit' to quit, '/create <thread_name>' to create a new thread, '/switch <thread_name>' to switch threads, '/history' to see stored messages.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Exiting the demo.")
            break
        elif user_input.lower().startswith("/create"):
            thread_name = user_input.split(maxsplit=1)[1] if len(user_input.split()) > 1 else None
            if thread_name:
                stm_memory.add_thread(thread_name)
                print(f"Thread '{thread_name}' created.")
            else:
                print("Please provide a thread name after '/create'.")
        elif user_input.lower().startswith("/switch"):
            thread_name = user_input.split(maxsplit=1)[1] if len(user_input.split()) > 1 else None
            if thread_name:
                stm_memory.switch_thread(thread_name)
                print(f"Switched to thread '{thread_name}'.")
            else:
                print("Please provide a thread name after '/switch'.")
        elif user_input.lower() == "/history":
            print("\nConversation History:")
            stm_memory.display_conversation_history()
            print("\n")
            continue

        response = stm_memory.ask(user_input)
        print(f"Assistant: {response}\n")

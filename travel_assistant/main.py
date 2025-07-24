import uuid
from travel_assistant.config import _set_env
from travel_assistant.agent.graph import part_4_graph
from travel_assistant.utils.print_utils import _print_event

# Set up config for the session
config = {
    "configurable": {
        "passenger_id": "3442 587242",
        "thread_id": str(uuid.uuid4()),
    }
}

_printed = set()

def main():
    print("Welcome to the Travel Assistant! Type 'exit' to quit.")
    while True:
        question = input("Ask your travel question: ")
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        events = part_4_graph.stream(
            {"messages": ("user", question)}, config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)
        snapshot = part_4_graph.get_state(config)
        while getattr(snapshot, 'next', None):
            try:
                user_input = input(
                    "Do you approve of the above actions? Type 'y' to continue; otherwise, explain your requested changes.\n\n"
                )
            except Exception:
                user_input = "y"
            if user_input.strip().lower() == "y":
                result = part_4_graph.invoke(
                    None,
                    config,
                )
            else:
                result = part_4_graph.invoke(
                    {
                        "messages": [
                            {"tool_call_id": event["messages"][-1].tool_calls[0]["id"],
                             "content": f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input."}
                        ]
                    },
                    config,
                )
            snapshot = part_4_graph.get_state(config)

if __name__ == "__main__":
    main() 
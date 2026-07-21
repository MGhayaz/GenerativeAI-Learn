from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env file.

from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph.state import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver

# MongoDB connection URI.
# authSource=admin -> Authenticate using the admin database.
DB_URI = "mongodb://admin:admin@localhost:27017/?authSource=admin"

# Runtime configuration for LangGraph.
# thread_id uniquely identifies a conversation/session.
# Same thread_id -> Previous checkpoints are loaded.
config = {
    "configurable": {
        "thread_id": "ghayaz"
    }
}

# Initializes Gemini chat model.
llm = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai"
)


class State(TypedDict):
    # Graph state.
    # add_messages automatically appends new messages
    # instead of replacing the existing message history.
    messages: Annotated[list, add_messages]


def gemini(state: State):
    # Reads current conversation history.
    response = llm.invoke(state.get("messages"))

    # Returns the new AI response.
    # add_messages merges it with previous history.
    return {"messages": [response]}


# Creates an empty graph.
graph_builder = StateGraph(State)

# Registers the node.
graph_builder.add_node("gemini", gemini)

# START -> gemini
graph_builder.add_edge(START, "gemini")

# gemini -> END
graph_builder.add_edge("gemini", END)

# Compiles graph without persistence.
graphed = graph_builder.compile()


def compile_graph_with_checkpointer(checkpointer):
    # Generic helper function.
    # Compiles the graph using any checkpoint backend
    # (MongoDB, SQLite, Memory, etc.)
    return graph_builder.compile(checkpointer=checkpointer)


# Creates MongoDB checkpointer.
# Context manager automatically opens and closes the connection.
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:

    # Graph now has persistence support.
    graphed = compile_graph_with_checkpointer(checkpointer=checkpointer)

    updated_graph = graphed.invoke(
        {
            "messages": ["where do i live??"]
        },
        config=config
    )

    print("updated_graph", updated_graph)
    
    
# MongoDBSaver
# Saves graph checkpoints in MongoDB.
# Checkpoint
# Snapshot of the graph's current state.
# Used to continue execution later.
# thread_id
# Unique memory/session id.
# Same thread_id -> Same conversation history.
# Different thread_id -> New conversation.
# checkpointer
# Handles saving and loading graph state automatically.
# graph.compile()
# Converts graph definition into an executable graph.
# graph.compile(checkpointer=...)
# Same graph + automatic state persistence.
# config
# Runtime settings passed while invoking the graph.
# Used for thread_id, user_id, checkpoint options, etc.
# with ...
# Automatically cleans up MongoDB connection after execution.    
from dotenv import load_dotenv
# Existing type ke saath extra metadata attach karta hai.
# LangGraph is metadata (e.g., add_messages) ko state update rules samajhne ke liye use karta hai.
from typing import Annotated
# Dictionary ka blueprint define karta hai, jisse state ki allowed keys aur types fixed rehte hain.
from typing_extensions import TypedDict
# LangGraph workflow builder hai jisme nodes, edges aur state define karke graph create kiya jata hai.
from langgraph.graph import StateGraph,START,END
# Reducer function jo naye messages ko existing chat history me append karta hai, overwrite nahi.
from langgraph.graph.message import add_messages
# ai model direct access from langchain
load_dotenv()
from langchain.chat_models import init_chat_model
llm = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai"
)

class State(TypedDict):
    # message
    # -------
    # Graph ka shared state field jo conversation history store karta hai.
    # add_messages ensure karta hai ki naye messages existing history me append hon.
    messages: Annotated[list, add_messages]
# StateGraph ko State schema diya ja raha hai.
# Is graph ke saare nodes isi shared state ko read aur update karenge.
graph_builder = StateGraph(State)

def chat_1(state : State):
    result = llm.invoke(state.get("messages")) # model ku call kare, response liye by giving the existing input log present in state by using "state.get(messages)"
    return {"messages": [result]}
def chat_2(state:State):
    # this node runs after chat_1 as per defined schema below at line 33
    print("\nfrom chat_2",state , "\n")
    return {"messages": [" i am chat 2 Node"]}
# noding and edgeing

graph_builder.add_node("chat_1",chat_1)
graph_builder.add_node("chat_2", chat_2)
graph_builder.add_edge(START, "chat_1")
graph_builder.add_edge("chat_1","chat_2")
graph_builder.add_edge("chat_2",END)

graphed = graph_builder.compile()

updated_graph = graphed.invoke(
    State(
        {
            "messages": ["hi, this is my first initial message, which will be always placed first in state graph"]
        }
    )
)
print("updated_state", updated_graph )

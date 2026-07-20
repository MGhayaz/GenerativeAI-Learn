from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict, Optional,Literal
from langgraph.graph import StateGraph,START,END
load_dotenv()
llm = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai"
)

class State(TypedDict):
    input : str
    llm_response : Optional[str]
    is_good : Optional[bool]
     
graph_build = StateGraph(State) # stategraph ku apna decided input-output wale state ka schema diye

def chat_model_one(state : State): # ek llm jo apna response state me store karta and return bi karta
    print("chat_model_one node",state)
    response = llm.invoke(
        state.get("input")
    )
    state["llm_response"] = response.content
    return state

# Current state check karke decide karta next kis node pe jana hai.
def evaluate_response(state: State) -> Literal["chat_model_two", "end_node"]:
    print("evaluate_response node", state)
    # Literal batata hai ki function sirf "chat_model_two" ya "end_node" hi return karega.
    if False:
        return "end_node"
    # LangGraph isi returned node ko next execute karta hai. 
    return "chat_model_two"
    # LangGraph isi returned node ko next execute karta hai. 

def chat_model_two(state:State): # DITTO of chat_model_one, ye bas mechanism test karne banaye
    print("chat_model_two node",state)
    response = llm.invoke(
        state.get("input")
    )
    state["llm_response"] = response.content
    return state

def end_node(state : State) :
    print("end_node node",state)
    return state    

# nodeing
graph_build.add_node("chat_model_one",chat_model_one)
graph_build.add_node("chat_model_two",chat_model_two)
graph_build.add_node("end_node",end_node)
#
graph_build.add_edge(START , "chat_model_one")
graph_build.add_conditional_edges("chat_model_one", evaluate_response) # condtional edge method second method [evaluate_response] ku power deta to run further any one node,
#iske paas do edges rehte outer me, also yahan jo string me node hai ["chat_mode_one"] define karta upper/inner edge

graph_build.add_edge("chat_model_two", "end_node") # agar false rakhe, toh evaluate_response chat_model_two ku chalata jiske baad ye line chalti
graph_build.add_edge("end_node", END) # agar true rakkhe, toh evualte_response sidha end_node run karta jiske baad ye line chalti
graph = graph_build.compile()
updated_graph = graph.invoke(
    State (
        {
            "input" : "what is 300+9" # ye as usual first string jaati state me, ye query lene perfect hai
        }
    )
)
print("updated_graph",updated_graph)


        

    
    
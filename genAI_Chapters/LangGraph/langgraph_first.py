# ===========================
# IMPORTS
# ===========================

# Annotated ka kaam?
# ------------------
# Ye Python ka special type wrapper hai.
#
# Normally:
#     message: list
#
# Sirf itna batata hai ki ye list hai.
#
# Lekin Annotated ke through hum extra metadata attach kar sakte.
#
# Syntax:
#     Annotated[OriginalType, ExtraInformation]
#
# Example:
#     Annotated[list, add_messages]
#
# Matlab:
# "Ye list hai, aur LangGraph is list ko add_messages rule ke hisaab se update kare."
#
# Python ko add_messages se matlab nahi.
# LangGraph is metadata ko read karta hai.

from typing import Annotated


# TypedDict kya hai?
# -------------------
# Ye ek dictionary ka blueprint hai.
#
# Normally:
#
# state = {
#     "message": [...],
#     "name": "Ali"
# }
#
# Is dictionary me kuch bhi daal sakte.
#
# TypedDict bolta:
#
# "Nahi.
# Is dictionary me sirf ye predefined keys hi allowed hain."
#
# Isse IDE autocomplete,
# static type checking,
# aur code readability improve hoti hai.

from typing_extensions import TypedDict


# StateGraph
# ----------
# Ye LangGraph ka main workflow builder hai.
#
# Iske andar hi:
#
# Node add karoge
# Edge connect karoge
# START/END define karoge
# Compile karoge
#
# Ye basically graph ka constructor hai.

from langgraph.graph import StateGraph


# add_messages
# ------------
#
# Ye LangGraph ka reducer function hai.
#
# Reducer matlab:
#
# Agar multiple nodes same state field ko update kare,
# to merge kaise hoga?
#
# Example:
#
# Old:
# [
#   HumanMessage(...)
# ]
#
# New:
# [
#   AIMessage(...)
# ]
#
# Without reducer:
#
# Old list replace ho jaati.
#
# Result:
# [
#   AIMessage(...)
# ]
#
# Human message gayab.
#
# add_messages reducer bolta:
#
# Replace mat karo.
#
# Existing messages ke END me naye messages append karo.
#
# Result:
#
# [
#   HumanMessage(...),
#   AIMessage(...)
# ]
#
# Isliye chat history survive karti.

from langgraph.graph.message import add_messages


# ===========================
# STATE DEFINITION
# ===========================

class State(TypedDict):

    # message
    # -------
    #
    # Ye state ki ek field hai.
    #
    # Ye ordinary Python list nahi hai.
    #
    # Runtime me usually isme LangChain message objects rehte.
    #
    # Example:
    #
    # [
    #     HumanMessage(
    #         content="Hi"
    #     ),
    #
    #     AIMessage(
    #         content="Hello!"
    #     )
    # ]
    #
    # Technically:
    #
    # list[AnyMessage]
    #
    # jahan AnyMessage ho sakta:
    #
    # HumanMessage
    # AIMessage
    # SystemMessage
    # ToolMessage
    #
    # Tumne generic "list" likha,
    # isliye Python strict type check nahi karega.
    #
    # Production code me usually:
    #
    # messages: Annotated[
    #     list[AnyMessage],
    #     add_messages
    # ]
    #
    # likhte.
    #
    # add_messages metadata LangGraph ko bolta:
    #
    # "Jab bhi koi node new messages return kare,
    # unhe overwrite mat karna.
    # Existing history me append karna."

    message: Annotated[list, add_messages]


# ===========================
# GRAPH CREATION
# ===========================

# Ab LangGraph ko bataya ja raha:
#
# "Mere workflow ka state
# State class follow karega."
#
# Matlab graph ke andar jitne bhi nodes chalenge,
#
# sab isi dictionary ko read/update karenge.
#
# Example runtime state:
#
# {
#     "message": [
#         HumanMessage(...),
#         AIMessage(...),
#         HumanMessage(...)
#     ]
# }
#
# Har node ko ye state milega.
#
# Node chahe:
#
# LLM ho
# Retriever ho
# Tool ho
# Validator ho
#
# sab isi state pe kaam karenge.

graph_builder = StateGraph(State)
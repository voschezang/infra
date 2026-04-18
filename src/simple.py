
from langchain.messages import HumanMessage
from IPython.display import Image, display
from langchain.messages import SystemMessage, ToolMessage
import operator
from typing import Annotated, Literal, TypedDict

from langchain.messages import AnyMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

# Initialize the model
model = ChatOllama(
    model="gemma4:e2b",
    # model="gemma4:e4b",
    # model="llama3.1:8b",
)


# Use the model
response = model.invoke("Explain LangChain in one sentence.")
print(response.content)

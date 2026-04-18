from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.messages import AnyMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langfuse import get_client
from langgraph.graph import END, START, StateGraph
from typing import Annotated, Literal, TypedDict
import logging
import operator


@tool
def multiply(a: float, b: float) -> float:
    """Multiply `a` and `b`.

    Args:
        a: First number
        b: Second number
    """
    print('tool_call: multiply', a, b)
    return a * b


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


# Initialize the model
model = ChatOllama(model="gemma4:e2b")

# Augment the LLM with tools
tools = [multiply]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)

langfuse_logger = logging.getLogger("langfuse")
langfuse_logger.setLevel(logging.DEBUG)


def llm_call(state: dict):
    """LLM decides whether to call a tool or not
    """
    global model_with_tools

    msg = [SystemMessage(content='Use short answers')] + state["messages"]
    llm_input = state["messages"][-1]
    llm_response = model_with_tools.invoke(msg)

    # log_call(llm_input, llm_response)
    return {
        "messages": [llm_response],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


def log_call(input, response):
    model_name = model_with_tools.bound.model

    langfuse = get_client()
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")

    # Create a span using a context manager
    with langfuse.start_as_current_observation(as_type="span", name="process-request") as span:
        # Your processing logic here
        span.update(output="Processing complete")

        # Create a nested generation for an LLM call
        with langfuse.start_as_current_observation(as_type="generation", name="llm-response", model=model_name) as generation:
            # Your LLM call logic here
            generation.update(input=input, output=response)

    # All spans are automatically closed when exiting their context blocks

    # Flush events in short-lived applications
    langfuse.flush()


def tool_node(state: dict):
    """Performs the tool call
    """
    global tools_by_name
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(
            content=observation,
            tool_call_id=tool_call["id"]))
    return {"messages": result}


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide whether to continue the loop or stop based upon whether the LLM made a tool call.
    """

    messages = state["messages"]

    # If the LLM makes a tool call, then perform an action
    if messages[-1].tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


def build_agent():
    # Build workflow
    agent_builder = StateGraph(MessagesState)

    # Add nodes
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)

    # Add edges to connect nodes
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call",
        should_continue,
        ["tool_node", END]
    )
    agent_builder.add_edge("tool_node", "llm_call")

    # Compile the agent
    agent = agent_builder.compile()

    # Show the agent
    img = agent.get_graph(xray=True).draw_mermaid_png()
    with open('graph.png', 'wb') as f:
        f.write(img)

    return agent


def run():
    agent = build_agent()

    # Invoke
    msg = "Multiply 10.0101 and pi. Use the tools available."
    msg = "Multiply 10.0101 and pi. Use an extremely high precision for pi."
    prompt = HumanMessage(content=msg)
    return prompt, agent.invoke({"messages": [prompt]})


def logged_llm():
    global model_with_tools
    model_name = model_with_tools.bound.model

    langfuse = get_client()
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")

    # Create a span using a context manager
    with langfuse.start_as_current_observation(as_type="span", name="process-request") as span:
        # Your processing logic here
        span.update(output="Processing complete")

        # Your LLM call logic here

        prompt, result = run()

        for msg in result['messages']:
            msg.pretty_print()
            log_message(model_name, langfuse, msg)

    # Flush events in short-lived applications
    langfuse.flush()


def log_message(model_name, langfuse, msg):
    if isinstance(msg, HumanMessage):
        with langfuse.start_as_current_observation(as_type="generation", name="user-input") as generation:
            generation.update(input=msg.content)
    elif isinstance(msg, AIMessage):
        if msg.content:
            with langfuse.start_as_current_observation(as_type="generation", name="llm-response", model=model_name) as generation:
                generation.update(output=msg.content)
        for tool in msg.tool_calls:
            with langfuse.start_as_current_observation(as_type="generation", name="llm-response-tool", model=model_name) as generation:
                generation.update(output=tool['name'])

    elif isinstance(msg, ToolMessage):
        with langfuse.start_as_current_observation(as_type="tool", name="external-tool-call") as tool_call:
            tool_call.update(output=msg.content)

    else:
        print("Unknown message type:", msg)


if __name__ == '__main__':
    # run()
    logged_llm()

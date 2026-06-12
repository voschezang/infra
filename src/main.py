from datetime import datetime
from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.messages import AnyMessage
from langchain_ollama import ChatOllama
from langfuse import get_client
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing import Annotated, Iterable, Literal, TypedDict
import logging
import operator
import re

from review import Review
from trip import Trip


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


class MyModel:
    def __init__(self, name='my_model', tools=None, logfile=''):
        # Initialize the model
        model = ChatOllama(model="gemma4:e2b")

        # Augment the LLM with tools
        self.tools_by_name = {tool.name: tool for tool in tools}
        self.model_with_tools = model.bind_tools(tools)

        langfuse_logger = logging.getLogger("langfuse")
        langfuse_logger.setLevel(logging.DEBUG)

        self.system_prompt = 'Use short answers'
        self.name = re.sub(r'[^\w\-]+', '', name)
        self.logfile = logfile

        self.init_logfile(logfile)

    def init_logfile(self, logfile):
        if logfile:
            with open(self.logfile, 'w') as f:
                print(self.name, file=f)

    def llm_call(self, state: dict):
        """LLM decides whether to call a tool or not
        """
        msg = [SystemMessage(content=self.system_prompt)] + state["messages"]
        llm_response = self.invoke(msg)

        return {
            "messages": [llm_response],
            "llm_calls": state.get('llm_calls', 0) + 1
        }

    def invoke(self, msg: str):
        """Wrapper to allow patching in unittests
        """
        return self.model_with_tools.invoke(msg)

    def tool_node(self, state: dict):
        """Performs the tool call
        """
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = self.tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(
                content=observation,
                tool_call_id=tool_call["id"]))

        return {"messages": result}

    def logged_llm(self, prompt: str):
        model_name = self.model_with_tools.bound.model

        langfuse = get_client()
        if langfuse.auth_check():
            self.log("Langfuse client is authenticated and ready!")
        else:
            raise RuntimeError(
                "Authentication failed. Please check your credentials and host.")

        # Create a span using a context manager
        with langfuse.start_as_current_observation(as_type="span", name="process-request") as span:
            # Your processing logic here
            span.update(output="Processing complete")

            # Your LLM call logic here

            msg = self.run_fully(prompt, langfuse)

        # Flush events in short-lived applications
        langfuse.flush()

        return msg.content

    def run_fully(self, prompt: str, logger=None) -> str:
        model_name = self.model_with_tools.bound.model
        results = self.run(prompt)
        for result in results:
            for msg in result['messages']:
                self.log(msg.pretty_repr())
                # msg.pretty_print()

                # remote logging
                if logger:
                    log_message(model_name, logger, msg)

        return msg

    def run(self, content: str) -> Iterable[dict]:
        """Run the agent and return an iterable of messages.
        """
        agent = self.build_agent()
        # show_agent(agent, self.name)
        prompt = HumanMessage(content=content)

        for event in agent.stream({"messages": [prompt]}, stream_mode="updates"):
            yield infer_messages(event)

    def build_agent(self) -> CompiledStateGraph:
        # Build workflow
        agent_builder = StateGraph(MessagesState)

        # Add nodes
        agent_builder.add_node("llm_call", self.llm_call)
        agent_builder.add_node("tool_node", self.tool_node)

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

        return agent

    def log(self, *args, **kwds):
        if self.logfile is None:
            print(f'{self.name}:', *args, **kwds)
            return

        with open(self.logfile, 'a') as f:
            print(datetime.now(), file=f)
            print(*args, file=f, **kwds)


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide whether to continue the loop or stop based upon whether the LLM made a tool call.
    """

    messages = state["messages"]

    # If the LLM makes a tool call, then perform an action
    if messages[-1].tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


def infer_messages(event: dict) -> dict:
    if 'llm_call' in event:
        return event['llm_call']
    elif 'tool_node' in event:
        return event['tool_node']
    elif 'tool_call' in event:
        return event['tool_call']

    raise NotImplementedError(event)


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
        raise NotImplementedError(f'Unknown message type: {msg}')


def stringify(s: str) -> str:
    """Converts a string to a valid method name (snake_case).
    """
    without_spaces = re.sub(r'\s', '_', s)
    return re.sub(r'[^\w\-]+', '', without_spaces)


def show_agent(agent, name: str):
    img = agent.get_graph(xray=True).draw_mermaid_png()
    filename = f'graph-{name}.png'
    with open(filename, 'wb') as f:
        f.write(img)


def init_models(planner_log='', reviewer_log=''):
    if planner_log:
        print(f'Writing planner output to {planner_log}')
    if reviewer_log:
        print(f'Writing reviewer output to {reviewer_log}')

    review = Review()
    trip = Trip()
    planner = MyModel('planner',
                      tools=trip.tools + review.reading_tools,
                      logfile=planner_log)
    reviewer = MyModel('reviewer',
                       tools=review.tools + trip.reading_tools,
                       logfile=reviewer_log)
    return planner, reviewer


if __name__ == '__main__':
    planner, reviewer = init_models('out-planner.log', 'out-reviewer.log')
    planner.run_fully("""You're in the business of planning holiday trips.
Continuously, do the following:
- Post a new trip to the board.
- Check how many trips have been posted.
Stop when a handful of trips has been posted or after 5 iteration.
Do not ask any questions.
When writing trips, try to be creative and imaginative. Appeal to a diverse audience.
""")
    reviewer.run_fully("""You're in the business of reviewing holiday trips.
Continuously, do the following:
- List which trips do not have a review.
- Pick a trip that does not have a review.
- Post a review of that trip to the board. 
Stop when all trips have been reviewed or after 5 iteration.
Do not ask any questions.
When writing reviews, keep it brief. Less is more.
""")

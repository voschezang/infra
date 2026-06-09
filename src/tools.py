from langchain.tools import tool

global trips
trips = []


@tool
def multiply(a: float, b: float) -> float:
    """Multiply `a` and `b`.

    Args:
        a: First number
        b: Second number
    """
    print('tool_call: multiply', a, b)
    return a * b

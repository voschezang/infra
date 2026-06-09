from typing import List, Tuple
from langchain.tools import tool

global trips
trips = []


@tool
def list_trips() -> List[int]:
    """List all trips on the board.
    """
    return []


@tool
def post_trip(title: str, description: str):
    """Post a trip to the board.
    Fails if the trip already exists.
    """
    # print('Post trip:', title, description)
    pass


@tool
def read_trip() -> Tuple[int, str, str]:
    """Read the latest trip from the board.
    Returns a tuple of (trip number, title, description)
    """
    # print('Read trip')
    return (0, 'Trip to Rome', 'A magnificient trip to Rome')


@tool
def multiply(a: float, b: float) -> float:
    """Multiply `a` and `b`.

    Args:
        a: First number
        b: Second number
    """
    print('tool_call: multiply', a, b)
    return a * b

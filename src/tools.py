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
def list_reviews() -> List[int]:
    """List all reviews on the board.
    A review is always associated with a trip.
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
def post_review(i: int, review: str):
    """Post a review to trip number `i` to the board.
    Fails if the trip already exists.
    """
    # print('Post review:', i, review)
    pass


@tool
def read_review(i: int) -> str | None:
    """Read the review for trip number `i` from the board.
    Returns the review iself if it exists or None otherwise.
    """
    # print('Read review')
    return 'A great plan'


@tool
def multiply(a: float, b: float) -> float:
    """Multiply `a` and `b`.

    Args:
        a: First number
        b: Second number
    """
    print('tool_call: multiply', a, b)
    return a * b

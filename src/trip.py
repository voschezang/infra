from typing import List
from langchain.tools import tool
from langchain_core.tools import StructuredTool


from repository import Repository, RepositoryError


class Trip(Repository):
    def __init__(self):
        self.data = {}

    def list(self) -> List[int]:
        return list(self.data.keys())

    def read(self, i: int):
        try:
            return self.data[i]
        except KeyError:
            raise RepositoryError(f'Review {i} not found')

    def write(self, i: int, data: str):
        # write or update
        self.data[i] = data

    @property
    def tools(self):
        return [
            StructuredTool.from_function(
                func=self.list,
                name="list_trips",
                description="""List all trips on the board.
            Returns a list of indices.
            """),
            StructuredTool.from_function(
                func=self.read,
                name="read_trip",
                description="""Read the trip for trip number `i` from the board.
            Returns the trip itself if it exists or None otherwise.
            """),
            StructuredTool.from_function(
                func=self.write,
                name="write_trip",
                description="""Post a review to trip number `i` to the board.
            Fails if the trip already exists.
            """)
        ]

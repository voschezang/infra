from typing import List
from langchain.tools import tool
from langchain_core.tools import StructuredTool


from repository import Repository, RepositoryError


class Review(Repository):
    def __init__(self):
        self.reviews = {}

    def list(self) -> List[int]:
        return list(self.reviews.keys())

    def read(self, i: int):
        try:
            return self.reviews[i]
        except KeyError:
            raise RepositoryError(f'Review {i} not found')

    def write(self, i: int, data: str):
        # write or update
        self.reviews[i] = data

    @property
    def tools(self):
        return [
            StructuredTool.from_function(
                func=self.list,
                name="list_reviews",
                description="""List all reviews on the board.
            A review is always associated with a trip.
            """),
            StructuredTool.from_function(
                func=self.read,
                name="read_review",
                description="""Read the review for trip number `i` from the board.
            Returns the review itself if it exists or None otherwise.
            """),
            StructuredTool.from_function(
                func=self.write,
                name="write_review",
                description="""Post a review to trip number `i` to the board.
            Fails if the trip already exists.
            """)
        ]

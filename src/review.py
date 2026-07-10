from langchain_core.tools import StructuredTool


from repository import Repository


class Review(Repository):
    def read(self, i: int):
        try:
            return self.data[i]
        except KeyError:
            return f'Error: Review {i} not found'

    def write(self, i: int, data: str) -> int:
        # write or update
        self.data[i] = data
        return i

    @property
    def tools(self):
        return self.reading_tools + self.writing_tools

    @property
    def reading_tools(self):
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
            Returns the review itself if it exists or an error message otherwise.
            """)
        ]

    @property
    def writing_tools(self):
        return [
            StructuredTool.from_function(
                func=self.write,
                name="write_review",
                description="""Post a review to trip number `i` to the board.
            """)
        ]

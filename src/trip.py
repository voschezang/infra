from langchain_core.tools import StructuredTool


from repository import Repository


class Trip(Repository):
    def read(self, i: int) -> str:
        try:
            return self.data[i]
        except KeyError:
            return f'Error: Trip {i} not found'

    def write(self, title: str, description: str) -> int:
        i = len(self.data)
        self.data[i] = {'title': title, 'description': description}
        return i

    @property
    def tools(self):
        return self.reading_tools + self.writing_tools

    @property
    def reading_tools(self):
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
            Returns the trip itself if it exists or an error message otherwise.
            """),

        ]

    @property
    def writing_tools(self):
        return [
            StructuredTool.from_function(
                func=self.write,
                name="write_trip",
                description="""Post a trip to the board.
            """)
        ]

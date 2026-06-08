from typing import List

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

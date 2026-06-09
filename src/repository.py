from abc import ABC, abstractmethod
from typing import List


class Repository(ABC):
    """A repository with CRUD methods.
    """

    def __init__(self):
        self.data = {}

    def list(self) -> List[int]:
        """List all items.
        """
        return list(self.data.keys())

    @abstractmethod
    def read(self, i: int) -> str:
        """Return the item with index `i`.
        """
        pass

    @abstractmethod
    def write(self, *args, **kwds) -> int:
        """Returns the index or UUID of the new item.
        """
        pass


class RepositoryError(RuntimeError):
    pass

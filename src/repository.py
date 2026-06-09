from abc import ABC, abstractmethod
from typing import List


class Repository(ABC):
    """A repository with CRUD methods.
    """

    @abstractmethod
    def list(self) -> List[int]:
        """List all items.
        """
        pass

    @abstractmethod
    def read(self, i: int) -> str:
        """Return the item with index `i`.
        """
        pass

    @abstractmethod
    def write(self, i: int, data: str):
        """(Over)write the item with index `i`.
        """
        pass


class RepositoryError(RuntimeError):
    pass

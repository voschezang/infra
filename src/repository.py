from abc import ABC, abstractmethod
from typing import List


class Repository(ABC):
    @abstractmethod
    def list(self) -> List[int]:
        pass

    @abstractmethod
    def read(self, i: int) -> str:
        pass

    @abstractmethod
    def write(self, i: int, data: str):
        pass


class RepositoryError(RuntimeError):
    pass

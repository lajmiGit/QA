from abc import ABC, abstractmethod

class RequirementConnector(ABC):
    @abstractmethod
    def fetch(self, identifier: str) -> str:
        """Fetch requirement content from a source using an identifier."""
        pass

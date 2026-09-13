from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class UniversityDataProvider(ABC):
    """Abstract interface for higher education data providers (seed, free APIs, QS/THE)."""

    @abstractmethod
    def search_universities(self, query: str = "", country: str = "", max_tuition: Optional[int] = None,
                            min_acceptance_rate: Optional[float] = None, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Search and filter universities based on criteria."""
        pass

    @abstractmethod
    def get_university_by_id(self, university_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve detailed profile for a single university."""
        pass

    @abstractmethod
    def get_courses(self, university_id: str) -> List[Dict[str, Any]]:
        """Fetch available degree programs for an institution."""
        pass

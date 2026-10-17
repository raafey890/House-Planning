from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.layout import LayoutData

class AIPlanningProvider(ABC):
    @abstractmethod
    def generate_layout(self, context: Dict[str, Any], feedback: str = None) -> LayoutData:
        """
        Generates structured floor plan layout data based on the context.
        If feedback is provided, the generation should act as a retry with constraints.
        
        Args:
            context: A normalized dictionary of project requirements (PlanningContext).
            feedback: Optional string describing validation failures from previous attempt.
            
        Returns:
            LayoutData: The parsed, pydantic-validated layout data.
        """
        pass

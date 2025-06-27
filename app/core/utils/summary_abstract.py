from abc import ABC, abstractmethod
from typing import Optional


class AbstractSummaryService(ABC):
    """Абстрактный класс для сервисов генерации summary"""
    
    @abstractmethod
    async def generate_summary(self, text: str) -> str:
        ...

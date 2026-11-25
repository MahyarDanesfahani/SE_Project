from dataclasses import dataclass
from typing import Protocol


@dataclass
class MealConnectionStatus:
    provider: str = "student.znu.ac.ir"
    configured: bool = False
    status: str = "not_configured"
    message: str = "API یا مجوز رسمی پورتال تغذیه هنوز دریافت نشده است."


class MealAdapter(Protocol):
    def connection_status(self) -> MealConnectionStatus: ...

    def sync_menu(self) -> None:
        """Sync only through an approved official integration."""
        ...

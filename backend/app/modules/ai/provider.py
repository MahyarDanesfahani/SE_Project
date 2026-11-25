from dataclasses import dataclass
from typing import Protocol

@dataclass
class AIReply:
    provider: str
    content: str
    configured: bool

class AIProvider(Protocol):
    def reply(self, user_message: str) -> AIReply: ...

class NotConfiguredProvider:
    def reply(self, user_message: str) -> AIReply:
        return AIReply(provider="not_configured", content="ارائه‌دهنده هوش مصنوعی هنوز پیکربندی نشده است؛ پاسخ قطعی تولید نشد.", configured=False)

"""Data models for Salesforce support case triage and escalation tracking."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any


class ChannelType(str, Enum):
    VOICE = "Voice"
    EMAIL = "Email"
    WEB = "Web Portal"
    CHAT = "Chat"


class Priority(str, Enum):
    P1_CRITICAL = "P1-Critical"     # Business down, severe revenue/compliance impact
    P2_HIGH = "P2-High"             # Major feature unavailable, no workaround
    P3_MEDIUM = "P3-Medium"         # Feature impaired, viable workaround exists
    P4_LOW = "P4-Low"               # General inquiry, how-to guidance


class Category(str, Enum):
    USER_MANAGEMENT = "User Management & Access"
    DATA_MANAGEMENT = "Data Management & Bulk Operations"
    REPORTS_DASHBOARDS = "Reports & Dashboards"
    INTEGRATION_API = "Integration & APIs"
    CUSTOM_CODE = "Custom Apex/Visualforce/LWC"
    BILLING_LICENSING = "Billing & Org Licensing"
    GENERAL_CONFIG = "General Salesforce Configuration"


class EscalationTarget(str, Enum):
    FRONT_LINE = "Frontline Technical Support (L1/L2)"
    PRO_SERVICES = "Professional Services"
    ACCOUNT_EXECUTIVE = "Account Executive / Customer Success Manager"
    TIER3_ENGINEERING = "Tier-3 Product Engineering"


@dataclass
class SupportCase:
    case_id: str
    subject: str
    description: str
    channel: ChannelType
    customer_org_id: str
    customer_tier: str = "Standard"  # Standard, Premier, Signature
    category: Optional[Category] = None
    priority: Priority = Priority.P3_MEDIUM
    escalation_target: EscalationTarget = EscalationTarget.FRONT_LINE
    escalation_reason: Optional[str] = None
    suggested_steps: List[str] = field(default_factory=list)
    voice_metadata: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sla_target_minutes: int = 240
    status: str = "New"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "subject": self.subject,
            "description": self.description,
            "channel": self.channel.value if isinstance(self.channel, Enum) else self.channel,
            "customer_org_id": self.customer_org_id,
            "customer_tier": self.customer_tier,
            "category": self.category.value if isinstance(self.category, Enum) else self.category,
            "priority": self.priority.value if isinstance(self.priority, Enum) else self.priority,
            "escalation_target": self.escalation_target.value if isinstance(self.escalation_target, Enum) else self.escalation_target,
            "escalation_reason": self.escalation_reason,
            "suggested_steps": self.suggested_steps,
            "voice_metadata": self.voice_metadata,
            "sla_target_minutes": self.sla_target_minutes,
            "status": self.status,
            "created_at": self.created_at
        }

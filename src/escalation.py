"""Escalation routing matrix for Salesforce Cloud Success support.

Distinguishes between frontline support scope, Professional Services (custom code / implementation),
Account Executive (commercial / licensing), and Tier-3 Platform Engineering.
"""

import re
from typing import Tuple
from src.models import EscalationTarget, Category


PRO_SERVICES_INDICATORS = [
    r"\b(custom trigger|rewrite apex|architectural review|new lwc development)\b",
    r"\b(develop custom component|build custom integration|data migration service)\b",
    r"\b(system\.nullpointerexception in custom|trigger .* soql queries: 101)\b",
    r"\b(custom visualforce controller|help us write an apex class)\b"
]

AE_INDICATORS = [
    r"\b(purchase licenses|need more licenses|add 50 users|user license limit reached)\b",
    r"\b(storage limit exceeded|buy additional storage|upgrade to enterprise|upgrade edition)\b",
    r"\b(renew contract|contract pricing|billing inquiry|invoice dispute)\b",
    r"\b(agentforce add-on pricing|einstein 1 license expansion)\b"
]

TIER3_INDICATORS = [
    r"\b(gack error|internal server error 500|salesforce core bug|known issue)\b",
    r"\b(trust\.salesforce\.com incident|platform degradation|instance na\d+ outage)\b"
]


class EscalationRouter:
    """Evaluates case description and category to identify appropriate routing target."""

    def evaluate(self, text: str, category: Category) -> Tuple[EscalationTarget, str]:
        """Returns the EscalationTarget and the rationale for the routing decision."""
        lower_text = text.lower()

        # Check Account Executive / Commercial triggers first
        for pattern in AE_INDICATORS:
            if re.search(pattern, lower_text):
                return (
                    EscalationTarget.ACCOUNT_EXECUTIVE,
                    "Commercial request identified (user licensing, storage tier upgrade, or contract modification). Route to assigned Account Executive."
                )

        # Check Professional Services triggers (Custom code / development scope)
        if category == Category.CUSTOM_CODE:
            return (
                EscalationTarget.PRO_SERVICES,
                "Case involves custom Apex/LWC development or out-of-scope trigger architecture. Frontline support covers declarative features; engagement requires Professional Services."
            )

        for pattern in PRO_SERVICES_INDICATORS:
            if re.search(pattern, lower_text):
                return (
                    EscalationTarget.PRO_SERVICES,
                    "Request requires custom application development, custom script migration, or code refactoring outside standard support scope. Refer to Professional Services."
                )

        # Check Tier-3 Engineering triggers
        for pattern in TIER3_INDICATORS:
            if re.search(pattern, lower_text):
                return (
                    EscalationTarget.TIER3_ENGINEERING,
                    "Platform-level core defect or GACK error suspected. Prepare technical replication log for Tier-3 Product Engineering escalation."
                )

        # Retain on Frontline Technical Support
        return (
            EscalationTarget.FRONT_LINE,
            "Standard declarative configuration, user permissions, bulk data operation, or reporting guidance. Resolvable by Frontline Cloud Success."
        )

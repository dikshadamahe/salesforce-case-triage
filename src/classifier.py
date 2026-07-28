"""Classification engine for Salesforce Cloud support cases.

Analyzes ticket text, error logs, and metadata to classify problem domains
and calculate priority according to customer SLA contracts.
"""

import re
from typing import Tuple, List, Dict
from src.models import Category, Priority


CATEGORY_RULES: Dict[Category, List[str]] = {
    Category.USER_MANAGEMENT: [
        r"\b(login|log-in|password|reset password|locked out|sso|single sign-on|saml|mfa)\b",
        r"\b(permission set|profile|owd|organization-wide default|sharing rule|role hierarchy)\b",
        r"\b(frozen user|deactivated user|user license|ip range|trusted ip)\b",
        r"\b(insufficient_access_on_cross_reference_entity)\b",
    ],
    Category.DATA_MANAGEMENT: [
        r"\b(data loader|bulk api|import wizard|export|csv|upsert|insert)\b",
        r"\b(duplicate|duplicate record|duplicate rule|matching rule)\b",
        r"\b(field_custom_validation_exception|validation rule|required field)\b",
        r"\b(string length exceeds|invalid picklist|malformed date)\b",
    ],
    Category.REPORTS_DASHBOARDS: [
        r"\b(report|dashboard|matrix report|summary report|joined report)\b",
        r"\b(chart|component|dashboard refresh|scheduled refresh)\b",
        r"\b(report type|custom report type|filter limit|summary formula)\b",
        r"\b(folder access|dashboard viewer|running user)\b",
    ],
    Category.INTEGRATION_API: [
        r"\b(rest api|soap api|bulk api 2\.0|composite api|streaming api)\b",
        r"\b(connected app|oauth|client id|client secret|jwt bearer|callback url)\b",
        r"\b(invalid_session_id|http 401|http 403|http 500|handshake failure)\b",
        r"\b(webhook|external service|named credential)\b",
    ],
    Category.CUSTOM_CODE: [
        r"\b(apex|trigger|apex class|visualforce|lwc|lightning web component)\b",
        r"\b(system\.nullpointerexception|system\.limitexception|soql queries: 101)\b",
        r"\b(test coverage|unit test failure|code coverage below 75%)\b",
    ],
    Category.BILLING_LICENSING: [
        r"\b(license limit|out of licenses|buy license|additional user license)\b",
        r"\b(storage limit|data storage exceeded|file storage|contract renewal)\b",
        r"\b(edition upgrade|enterprise edition|unlimited edition|renewal quote)\b",
    ]
}

P1_TRIGGERS = [
    r"\b(system down|production down|all users locked|cannot login across company)\b",
    r"\b(critical revenue|month end close|financial impact|data corruption|severity 1)\b"
]

P2_TRIGGERS = [
    r"\b(major feature down|bulk import blocked|sales team unable to submit|executive dashboard)\b",
    r"\b(urgent deadline|sso authentication broken for department)\b"
]


class CaseClassifier:
    """Classifies support tickets and calculates priority based on impact."""

    def classify_category(self, text: str) -> Category:
        """Determines the primary category based on keyword density and regex matching."""
        lower_text = text.lower()
        scores: Dict[Category, int] = {cat: 0 for cat in CATEGORY_RULES}

        for cat, patterns in CATEGORY_RULES.items():
            for pat in patterns:
                matches = re.findall(pat, lower_text)
                scores[cat] += len(matches)

        best_category = max(scores, key=lambda c: scores[c])
        if scores[best_category] > 0:
            return best_category
        return Category.GENERAL_CONFIG

    def determine_priority(self, text: str, customer_tier: str = "Standard") -> Tuple[Priority, int]:
        """Calculates Priority and SLA target minutes based on severity indicators and customer contract tier."""
        lower_text = text.lower()

        # Check P1 conditions
        for trigger in P1_TRIGGERS:
            if re.search(trigger, lower_text):
                # Signature/Premier tiers get accelerated 15-30m response
                sla = 15 if customer_tier.lower() == "signature" else 30
                return Priority.P1_CRITICAL, sla

        # Check P2 conditions
        for trigger in P2_TRIGGERS:
            if re.search(trigger, lower_text):
                sla = 60 if customer_tier.lower() in ("signature", "premier") else 120
                return Priority.P2_HIGH, sla

        # Check P4 conditions (informational / how-to)
        if any(w in lower_text for w in ["how to", "best practice", "guide me", "documentation link", "general question"]):
            return Priority.P4_LOW, 480

        # Default to P3 Medium
        sla = 120 if customer_tier.lower() == "premier" else 240
        return Priority.P3_MEDIUM, sla

"""Main triage orchestration engine for Salesforce support cases."""

from typing import Dict, Any, List
from src.models import SupportCase, ChannelType, Category
from src.classifier import CaseClassifier
from src.escalation import EscalationRouter
from src.knowledge_base import SolutionRecommender


class TriageEngine:
    """Orchestrates end-to-end case triage: classification, SLA assignment,

    escalation determination, and diagnostic playbook recommendation.
    """

    def __init__(self):
        self.classifier = CaseClassifier()
        self.router = EscalationRouter()
        self.recommender = SolutionRecommender()

    def process_case(self, case: SupportCase) -> SupportCase:
        """Processes an incoming case and updates it with triage decisions."""
        combined_text = f"{case.subject}\n{case.description}"

        # 1. Classify Category
        category = self.classifier.classify_category(combined_text)
        case.category = category

        # 2. Determine Priority & SLA
        priority, sla_minutes = self.classifier.determine_priority(
            combined_text, customer_tier=case.customer_tier
        )
        case.priority = priority
        case.sla_target_minutes = sla_minutes

        # 3. Evaluate Escalation Target
        escalation_target, escalation_reason = self.router.evaluate(
            combined_text, category=category
        )
        case.escalation_target = escalation_target
        case.escalation_reason = escalation_reason

        # 4. Generate Recommended Steps
        case.suggested_steps = self.recommender.get_recommendations(category)
        case.status = "Triaged"

        return case

    def triage_batch(self, cases: List[SupportCase]) -> List[SupportCase]:
        """Triages a batch of incoming cases."""
        return [self.process_case(c) for c in cases]

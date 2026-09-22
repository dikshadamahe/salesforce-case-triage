import unittest
from src.escalation import EscalationRouter
from src.models import Category, EscalationTarget


class TestEscalationRouter(unittest.TestCase):
    def setUp(self):
        self.router = EscalationRouter()

    def test_route_to_pro_services_for_apex(self):
        text = "Client wants us to rewrite apex trigger because of system.nullpointerexception in custom code."
        target, reason = self.router.evaluate(text, category=Category.CUSTOM_CODE)
        self.assertEqual(target, EscalationTarget.PRO_SERVICES)
        self.assertIn("Professional Services", reason)

    def test_route_to_account_executive_for_licenses(self):
        text = "Customer says user license limit reached and needs to purchase licenses for 25 new reps."
        target, reason = self.router.evaluate(text, category=Category.BILLING_LICENSING)
        self.assertEqual(target, EscalationTarget.ACCOUNT_EXECUTIVE)
        self.assertIn("Account Executive", reason)

    def test_route_to_frontline_for_standard_config(self):
        text = "Need help setting up role hierarchy and sharing rules for EMEA sales group."
        target, reason = self.router.evaluate(text, category=Category.USER_MANAGEMENT)
        self.assertEqual(target, EscalationTarget.FRONT_LINE)
        self.assertIn("Frontline Cloud Success", reason)


if __name__ == "__main__":
    unittest.main()

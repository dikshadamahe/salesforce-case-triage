import unittest
from src.classifier import CaseClassifier
from src.models import Category, Priority


class TestCaseClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = CaseClassifier()

    def test_user_management_classification(self):
        text = "User cannot reset password and received insufficient_access_on_cross_reference_entity on Contact object."
        category = self.classifier.classify_category(text)
        self.assertEqual(category, Category.USER_MANAGEMENT)

    def test_data_loader_classification(self):
        text = "Data loader failed during bulk upsert of 5000 accounts. Error: FIELD_CUSTOM_VALIDATION_EXCEPTION."
        category = self.classifier.classify_category(text)
        self.assertEqual(category, Category.DATA_MANAGEMENT)

    def test_reports_classification(self):
        text = "Executive matrix report summary formula error and scheduled dashboard refresh not delivering emails."
        category = self.classifier.classify_category(text)
        self.assertEqual(category, Category.REPORTS_DASHBOARDS)

    def test_api_integration_classification(self):
        text = "Connected app OAuth handshake failed with HTTP 401 invalid_session_id in REST API client."
        category = self.classifier.classify_category(text)
        self.assertEqual(category, Category.INTEGRATION_API)

    def test_p1_priority_detection(self):
        text = "Critical revenue impact: Production down! All users locked out during month end close."
        priority, sla = self.classifier.determine_priority(text, customer_tier="Signature")
        self.assertEqual(priority, Priority.P1_CRITICAL)
        self.assertEqual(sla, 15)

    def test_p4_informational_priority(self):
        text = "How to best practice for creating a custom report type for opportunities."
        priority, sla = self.classifier.determine_priority(text, customer_tier="Standard")
        self.assertEqual(priority, Priority.P4_LOW)
        self.assertEqual(sla, 480)


if __name__ == "__main__":
    unittest.main()

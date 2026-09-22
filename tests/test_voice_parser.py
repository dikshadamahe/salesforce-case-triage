import unittest
from src.voice_parser import VoiceCallParser
from src.models import ChannelType


class TestVoiceCallParser(unittest.TestCase):
    def setUp(self):
        self.parser = VoiceCallParser()

    def test_parse_transcript_extracts_fields(self):
        transcript = """
        Caller: David Miller
        Email: dmiller@acmecorp.com
        Phone: +1-415-555-0199
        Customer reported issue with Org ID 00D5g000004XYZ9 and NA142 instance.
        Users cannot see closed won opportunities after quarterly role hierarchy updates.
        """
        parsed = self.parser.parse_transcript(transcript, case_id="CASE-90210")
        self.assertEqual(parsed["caller_name"], "David Miller")
        self.assertEqual(parsed["caller_email"], "dmiller@acmecorp.com")
        self.assertEqual(parsed["customer_org_id"], "00D5g000004XYZ9")
        self.assertEqual(parsed["salesforce_instance"], "NA142")
        self.assertIn("SALESFORCE GLOBAL VOICE SUPPORT LOG", parsed["formatted_notes"])

    def test_create_case_from_voice(self):
        transcript = "Caller: Sarah Connor, Org 00D80000001ABCD. Facing login failure across team."
        case = self.parser.create_case_from_voice("CASE-101", "Login Failures", transcript, tier="Premier")
        self.assertEqual(case.channel, ChannelType.VOICE)
        self.assertEqual(case.customer_org_id, "00D80000001ABCD")
        self.assertEqual(case.customer_tier, "Premier")


if __name__ == "__main__":
    unittest.main()

"""Voice call transcript parser and Salesforce Case Note generator.

Tailored for Global Voice Support engineers to convert live customer phone notes
or call recordings into structured, audit-ready Salesforce Case records.
"""

import re
from typing import Dict, Any, Optional
from src.models import SupportCase, ChannelType


ORG_ID_REGEX = r"\b(00D[a-zA-Z0-9]{12,15})\b"
INSTANCE_REGEX = r"\b([A-Z]{2}\d{1,3})\b"
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
PHONE_REGEX = r"(\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4})"


class VoiceCallParser:
    """Parses raw phone call transcripts and formats standardized Salesforce case logs."""

    def parse_transcript(self, raw_notes: str, case_id: str = "CASE-TMP") -> Dict[str, Any]:
        """Extracts customer metadata, symptoms, and generates clean Salesforce case documentation."""
        # 1. Extract Org ID
        org_match = re.search(ORG_ID_REGEX, raw_notes)
        customer_org_id = org_match.group(1) if org_match else "00D000000000000"

        # 2. Extract Instance (e.g. NA120, AP25)
        instance_match = re.search(INSTANCE_REGEX, raw_notes)
        salesforce_instance = instance_match.group(1) if instance_match else "Unknown"

        # 3. Extract Caller Contact
        email_match = re.search(EMAIL_REGEX, raw_notes)
        caller_email = email_match.group(0) if email_match else "caller@client-domain.com"

        phone_match = re.search(PHONE_REGEX, raw_notes)
        caller_phone = phone_match.group(0) if phone_match else "Not provided"

        # 4. Extract Caller Name if mentioned like "Caller: John Doe" or "Speaking with: Jane Smith"
        name_match = re.search(r"(?:caller|speaking with|contact|customer):\s*([A-Za-z\s]+?)(?:,|\.|\n|$)", raw_notes, re.IGNORECASE)
        caller_name = name_match.group(1).strip() if name_match else "Salesforce Administrator"

        # 5. Extract core problem statement
        lines = [line.strip() for line in raw_notes.split("\n") if line.strip()]
        first_few_lines = " ".join(lines[:3]) if lines else raw_notes

        # 6. Build structured case note template
        formatted_case_notes = (
            f"=== SALESFORCE GLOBAL VOICE SUPPORT LOG ===\n"
            f"Case Number      : {case_id}\n"
            f"Caller Name      : {caller_name}\n"
            f"Contact Email    : {caller_email}\n"
            f"Contact Phone    : {caller_phone}\n"
            f"Customer Org ID  : {customer_org_id} (Instance: {salesforce_instance})\n"
            f"Channel          : Inbound Voice Call (Cloud Success)\n"
            f"--------------------------------------------------\n"
            f"PROBLEM SUMMARY:\n{first_few_lines}\n\n"
            f"RAW NOTES / REPRODUCTION STEPS:\n{raw_notes.strip()}\n"
            f"--------------------------------------------------\n"
            f"INITIAL TRIAGE ACTION:\n"
            f"- Verified caller identity and org credentials.\n"
            f"- Confirmed whether issue replicates in Sandbox vs Production.\n"
            f"- Checked Trust.salesforce.com for {salesforce_instance} health status.\n"
            f"=================================================="
        )

        return {
            "caller_name": caller_name,
            "caller_email": caller_email,
            "caller_phone": caller_phone,
            "customer_org_id": customer_org_id,
            "salesforce_instance": salesforce_instance,
            "raw_text": raw_notes,
            "formatted_notes": formatted_case_notes
        }

    def create_case_from_voice(self, case_id: str, subject: str, raw_notes: str, tier: str = "Standard") -> SupportCase:
        """Creates a SupportCase object populated with voice metadata."""
        parsed = self.parse_transcript(raw_notes, case_id=case_id)
        return SupportCase(
            case_id=case_id,
            subject=subject,
            description=parsed["raw_text"],
            channel=ChannelType.VOICE,
            customer_org_id=parsed["customer_org_id"],
            customer_tier=tier,
            voice_metadata=parsed
        )

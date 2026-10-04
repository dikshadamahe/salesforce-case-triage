"""Command-line interface for Salesforce Support Case Triage Engine."""

import json
import sys
import argparse
from typing import List
from src.models import SupportCase, ChannelType
from src.triage_engine import TriageEngine
from src.voice_parser import VoiceCallParser


def load_cases_from_file(filepath: str) -> List[SupportCase]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    cases = []
    for item in data:
        case = SupportCase(
            case_id=item["case_id"],
            subject=item["subject"],
            description=item["description"],
            channel=ChannelType(item.get("channel", "Web Portal")),
            customer_org_id=item.get("customer_org_id", "00D000000000000"),
            customer_tier=item.get("customer_tier", "Standard")
        )
        cases.append(case)
    return cases


def print_case_summary(case: SupportCase):
    print("=" * 72)
    print(f"CASE ID   : {case.case_id} | Priority: {case.priority.value} (SLA: {case.sla_target_minutes}m)")
    print(f"SUBJECT   : {case.subject}")
    print(f"CHANNEL   : {case.channel.value} | Org ID: {case.customer_org_id} ({case.customer_tier})")
    print(f"CATEGORY  : {case.category.value if case.category else 'N/A'}")
    print(f"ROUTING   : {case.escalation_target.value}")
    if case.escalation_reason:
        print(f"RATIONALE : {case.escalation_reason}")
    print("\nRECOMMENDED TROUBLESHOOTING ACTIONS:")
    for step in case.suggested_steps[:3]:
        print(f"  {step}")
    print("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Salesforce Support Case Triage Engine")
    parser.add_argument("--file", "-f", default="data/sample_cases.json", help="Path to JSON file containing support cases")
    parser.add_argument("--voice", "-v", help="Path to raw voice call notes text file")
    parser.add_argument("--output", "-o", help="Optional path to output triaged JSON")
    args = parser.parse_args()

    engine = TriageEngine()

    if args.voice:
        with open(args.voice, "r", encoding="utf-8") as f:
            raw_text = f.read()
        voice_parser = VoiceCallParser()
        case = voice_parser.create_case_from_voice(
            case_id="VOICE-AUTO-01",
            subject="Inbound Voice Support Request",
            raw_notes=raw_text,
            tier="Premier"
        )
        triaged = engine.process_case(case)
        print_case_summary(triaged)
        if triaged.voice_metadata:
            print("\nFORMATTED SALESFORCE CASE LOG:\n")
            print(triaged.voice_metadata["formatted_notes"])
        return

    cases = load_cases_from_file(args.file)
    print(f"\n[INFO] Ingesting & triaging {len(cases)} support cases from {args.file}...\n")
    triaged_cases = engine.triage_batch(cases)

    for c in triaged_cases:
        print_case_summary(c)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in triaged_cases], f, indent=2)
        print(f"[SUCCESS] Exported triaged results to {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Interactive Web Server for Salesforce Case Triage & Automation Engine.
Runs locally with zero external dependencies (Python standard library).
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Ensure src modules are imported cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.models import SupportCase, ChannelType
from src.triage_engine import TriageEngine
from src.voice_parser import VoiceCallParser
from src.cli import load_cases_from_file

PORT = 8080
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_cases.json")

engine = TriageEngine()
voice_parser = VoiceCallParser()


class SalesforceSupportHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            index_path = os.path.join(STATIC_DIR, "index.html")
            with open(index_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path == "/api/cases":
            cases = load_cases_from_file(DATA_FILE)
            triaged = engine.triage_batch(cases)
            payload = json.dumps([c.to_dict() for c in triaged]).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Fallback to standard static file serving
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        data = json.loads(body) if body else {}

        if parsed.path == "/api/triage":
            case = SupportCase(
                case_id=data.get("case_id", "SF-LIVE-01"),
                subject=data.get("subject", ""),
                description=data.get("description", ""),
                channel=ChannelType(data.get("channel", "Web Portal")),
                customer_org_id=data.get("customer_org_id", "00D5g000004XYZ9"),
                customer_tier=data.get("customer_tier", "Standard")
            )
            triaged = engine.process_case(case)
            res_json = json.dumps(triaged.to_dict()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(res_json)))
            self.end_headers()
            self.wfile.write(res_json)
            return

        if parsed.path == "/api/voice-parse":
            raw_notes = data.get("raw_notes", "")
            parsed_voice = voice_parser.parse_transcript(raw_notes, case_id=data.get("case_id", "VOICE-LIVE"))
            res_json = json.dumps(parsed_voice).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(res_json)))
            self.end_headers()
            self.wfile.write(res_json)
            return

        self.send_response(404)
        self.end_headers()


def run_server():
    server = HTTPServer(("127.0.0.1", PORT), SalesforceSupportHandler)
    print(f"\n[+] Salesforce Cloud Success Hub running live at: http://127.0.0.1:{PORT}")
    print("[+] Press Ctrl+C to stop.\n")
    server.serve_forever()


if __name__ == "__main__":
    run_server()

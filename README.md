# Salesforce Case Triage & Automation Engine

An intelligent triage, diagnostic recommendation, and escalation assistant built for frontline technical support engineers supporting global Salesforce Cloud customers.

---

## Why I Built This
In 24/7 global customer support operations, technical support engineers handle dozens of multi-channel cases (inbound phone calls, web submissions, and priority emails) daily across time zones. Fast first-contact resolution (FCR), accurate SLA adherence, and clear escalation boundaries are vital. 

Frontline engineers often lose valuable minutes:
1. Manually classifying customer issues across complex domains (User Management, Data Loader, Reports & Dashboards, Connected Apps).
2. Manually writing out case notes after high-stress customer voice calls.
3. Deciding whether a case is resolvable in frontline support or must be routed to **Professional Services** (for custom Apex/LWC development) or the **Account Executive (AE)** team (for contract/user license expansion).

This engine automates that intake pipeline, standardizes case notes, and equips the engineer with immediate diagnostic playbooks.

---

## Key Features

- **Multi-Channel Ingestion:** Standardizes tickets submitted via Voice call transcripts, Email, or Web-to-Case JSON payloads.
- **Voice Transcript Parser:** Automatically parses raw phone call notes to extract Caller Name, Customer Org ID (15/18-character `00D...`), Salesforce Instance (`NA142`, `AP25`), contact details, and formats standard audit-ready Salesforce Case Notes.
- **Domain Classifier:** Categorizes incoming tickets into core Salesforce domains:
  - *User Management & Access* (SSO/SAML, MFA, Permission Sets, Profiles, OWD, Role Hierarchy)
  - *Data Management & Bulk Operations* (Data Loader errors, Bulk API 2.0, CSV encoding, Duplicate Rules)
  - *Reports & Dashboards* (Matrix grouping formulas, Scheduled Refresh, Custom Report Types)
  - *Integration & APIs* (OAuth 2.0 Connected Apps, REST/SOAP API errors, 401/403 limits)
  - *Custom Code & Licensing*
- **Automated Escalation Matrix:**
  - Identifies out-of-scope custom code (e.g. `System.LimitException: 101 SOQL queries`) and routes to **Professional Services**.
  - Identifies commercial license deficits or storage breaches and routes to the assigned **Account Executive (AE)**.
  - Retains declarative configuration & standard issues in Frontline L1/L2 Support.
- **Resolution Playbook Recommender:** Delivers step-by-step diagnostic procedures directly to the support engineer to reduce average handle time (AHT).
- **SLA & Priority Engine:** Computes SLA response target (15m, 30m, 60m, 120m, 240m) based on business impact and Customer Support Tier (Signature, Premier, Standard).

---

## Architecture Flow

```
Incoming Customer Ticket
(Voice Call / Email / Web Portal)
              │
              ▼
    [VoiceCallParser] ────────► Extracts Org ID, Instance, Caller info, Formats Case Note
              │
              ▼
    [CaseClassifier]  ────────► Categorizes domain (User Mgmt, Data Loader, Reports, APIs)
              │                 & calculates SLA Priority (P1-Critical to P4-Low)
              ▼
   [EscalationRouter] ────────► Evaluates routing target:
              │                 • Frontline Support (L1/L2)
              │                 • Professional Services (Custom Apex/LWC)
              │                 • Account Executive (Licensing / Storage)
              ▼
 [SolutionRecommender] ───────► Generates step-by-step troubleshooting actions
              │
              ▼
 Triaged Case Record / Export
```

---

## Project Structure

```
salesforce-case-triage/
├── data/
│   └── sample_cases.json          # Realistic sample Salesforce support tickets
├── src/
│   ├── __init__.py
│   ├── models.py                  # Case, Priority, Category & Escalation data models
│   ├── classifier.py              # Domain classification & SLA priority engine
│   ├── escalation.py              # Escalation matrix (Pro-Services, AE, Frontline)
│   ├── voice_parser.py            # Phone transcript parser & Case Note formatter
│   ├── knowledge_base.py          # Diagnostic playbooks for common Salesforce issues
│   ├── triage_engine.py           # Core triage orchestrator
│   └── cli.py                     # Command-line interface for support engineers
├── tests/
│   ├── __init__.py
│   ├── test_classifier.py
│   ├── test_escalation.py
│   └── test_voice_parser.py
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.9+

### Installation
```bash
git clone https://github.com/dikshadamahe/salesforce-case-triage.git
cd salesforce-case-triage
pip install -r requirements.txt
```

### Running Unit Tests
```bash
python3 -m unittest discover tests
```

### Triaging Sample Cases
Run the CLI on the bundled sample dataset:
```bash
python3 -m src.cli --file data/sample_cases.json
```

### Processing a Voice Support Call Note
```bash
python3 -m src.cli --voice sample_transcript.txt
```

---

## Example CLI Output

```
========================================================================
CASE ID   : SF-10492 | Priority: P1-Critical (SLA: 30m)
SUBJECT   : Bulk API upload failing with FIELD_CUSTOM_VALIDATION_EXCEPTION
CHANNEL   : Email | Org ID: 00D80000001ABCD (Signature)
CATEGORY  : Data Management & Bulk Operations
ROUTING   : Frontline Technical Support (L1/L2)
RATIONALE : Standard declarative configuration, user permissions, bulk data operation, or reporting guidance. Resolvable by Frontline Cloud Success.

RECOMMENDED TROUBLESHOOTING ACTIONS:
  1. Inspect Data Loader Error CSV: examine the 'STATUS' and error description column for failing row numbers.
  2. If 'FIELD_CUSTOM_VALIDATION_EXCEPTION': check Setup > Object Manager > [Object] > Validation Rules. Verify if rule criteria can be temporarily bypassed by a System Admin profile or if incoming data needs cleansing.
  3. If 'INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY': ensure the loading user has read access to lookup parent IDs (e.g., AccountId, ContactId).
========================================================================
```

---

## Author
**Diksha Damahe**  
*B.Tech Computer Science & Engineering (AI & ML), VIT Bhopal University*  
[LinkedIn](https://www.linkedin.com/in/dikshadamahe) • [GitHub](https://github.com/dikshadamahe)

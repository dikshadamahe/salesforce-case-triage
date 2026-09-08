"""Support engineering troubleshooting playbooks and solution recommender.

Provides verified step-by-step diagnostic actions for Salesforce Cloud
administrators and frontline support engineers.
"""

from typing import List, Dict
from src.models import Category


PLAYBOOKS: Dict[Category, List[str]] = {
    Category.USER_MANAGEMENT: [
        "1. Check User Detail page: verify user is Active, not Frozen, and has an active Salesforce User License assigned.",
        "2. Review Login History under Setup > Users: check Login Status (e.g., 'Invalid Password', 'Failed: Computer outside trusted IP range', 'SAML assertion invalid').",
        "3. Inspect Profile and Permission Sets: verify Object-Level (CRUD) and Field-Level Security (FLS) on affected objects.",
        "4. Check Sharing Settings (Setup > Security > Sharing Settings): confirm Org-Wide Defaults (OWD). If Private, check Sharing Rules, Role Hierarchy, or Manual Sharing.",
        "5. If Single Sign-On (SSO): validate Federation ID, IdP Certificate expiration, and SAML Assertion Validator in Setup."
    ],
    Category.DATA_MANAGEMENT: [
        "1. Inspect Data Loader Error CSV: examine the 'STATUS' and error description column for failing row numbers.",
        "2. If 'FIELD_CUSTOM_VALIDATION_EXCEPTION': check Setup > Object Manager > [Object] > Validation Rules. Verify if rule criteria can be temporarily bypassed by a System Admin profile or if incoming data needs cleansing.",
        "3. If 'INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY': ensure the loading user has read access to lookup parent IDs (e.g., AccountId, ContactId).",
        "4. For CSV parsing issues: verify file is encoded in UTF-8 without BOM, dates match 'YYYY-MM-DDTHH:MM:SSZ' format, and 15/18 character Salesforce IDs are exact.",
        "5. If Duplicate Rules block insert: review Setup > Duplicate Management. Check whether rule is configured to 'Block' or 'Alert'."
    ],
    Category.REPORTS_DASHBOARDS: [
        "1. Check Dashboard 'View Dashboard As' setting: determine if dashboard runs as 'Specified User' (fixed security view) or 'Dashboard Viewer' (dynamic dashboard).",
        "2. Review Custom Report Type: if fields are missing in report builder, navigate to Setup > Report Types > [Type] > 'Edit Layout' and ensure new fields are added.",
        "3. For summary formulas: verify grouping levels match formula syntax requirements (e.g. valid use of PARENTGROUPVAL or PREVGROUPVAL).",
        "4. Check Folder Sharing Permissions: verify user has 'View' or 'Manage' access to the report/dashboard parent folder.",
        "5. If dashboard refresh is slow: inspect report filters for unindexed fields or date ranges exceeding recommended limits."
    ],
    Category.INTEGRATION_API: [
        "1. Check Setup > Connected Apps: review OAuth policies, Refresh Token policy, and IP Relaxation settings ('Enforce IP restrictions' vs 'Relax IP restrictions').",
        "2. Inspect API User Profile: ensure 'API Enabled' administrative permission is checked on user profile/permission set.",
        "3. If HTTP 401 Unauthorized: check if session token has expired or if client secret/JWT certificate has expired.",
        "4. Review API Usage in Setup > System Overview: verify org has not breached the 24-hour rolling API request limit.",
        "5. Use Workbench or Postman with standard REST endpoint (/services/data/v60.0/) to isolate client-side network issues from Salesforce platform."
    ],
    Category.CUSTOM_CODE: [
        "1. Collect Developer Console Debug Log: set log level for Apex Code to FINE/FINEST to isolate failing line.",
        "2. If 'System.NullPointerException': check variable initialization and SOQL query result checks before referencing fields.",
        "3. If 'System.LimitException: 101 SOQL queries': verify that SOQL queries are not invoked inside for-loops; advise bulkification best practice.",
        "4. Prepare technical handoff summary and route to Professional Services or Client Developer team."
    ],
    Category.BILLING_LICENSING: [
        "1. Navigate to Setup > Company Information: review User Licenses and Feature Licenses table (Total, Used, Remaining).",
        "2. Navigate to Setup > Storage Usage: inspect Data Storage and File Storage percentages and top consumed objects.",
        "3. Formulate commercial escalation brief with Customer Org ID, current edition, and license shortfall.",
        "4. Route case directly to assigned Salesforce Account Executive (AE) / Customer Success Manager."
    ],
    Category.GENERAL_CONFIG: [
        "1. Reproduce issue in a Sandbox environment to isolate configuration changes from production data.",
        "2. Inspect Setup Audit Trail (Setup > Security > View Setup Audit Trail) to identify recent configuration changes by admins.",
        "3. Check trust.salesforce.com for instance status and scheduled maintenance windows.",
        "4. Consult Salesforce Official Help Documentation and Trailhead best practices."
    ]
}


class SolutionRecommender:
    """Delivers recommended diagnostic steps for support cases."""

    def get_recommendations(self, category: Category) -> List[str]:
        return PLAYBOOKS.get(category, PLAYBOOKS[Category.GENERAL_CONFIG])

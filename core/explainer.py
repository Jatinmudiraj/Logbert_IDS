import re

class AnomalyExplainer:
    def __init__(self):
        # Basic mapping of patterns to MITRE ATT&CK and human-readable reasons
        self.signatures = [
            {
                "pattern": r"failed password",
                "reason": "Repeated authentication failures detected.",
                "technique": "T1110 - Brute Force",
                "severity": "High"
            },
            {
                "pattern": r"invalid user",
                "reason": "Attempt to access system using non-existent usernames.",
                "technique": "T1110.003 - Password Spraying",
                "severity": "High"
            },
            {
                "pattern": r"exploit|overflow",
                "reason": "Suspicious payload or buffer overflow attempt detected.",
                "technique": "T1203 - Exploitation for Client Execution",
                "severity": "Critical"
            },
            {
                "pattern": r"sudo:.*COMMAND=",
                "reason": "Privileged command execution detected.",
                "technique": "T1548.003 - Sudo and Sudo Caching",
                "severity": "Medium"
            },
            {
                "pattern": r"session opened for user root",
                "reason": "Direct root session established.",
                "technique": "T1078 - Valid Accounts",
                "severity": "High"
            }
        ]

    def explain(self, result):
        """
        Takes a detection result and adds explainability fields.
        """
        raw_log = result.get("last_raw", "").lower()
        explanation = {
            "reason": "Contextual anomaly detected by Neural Engine",
            "mitre_technique": "N/A - Contextual Anomaly",
            "evidence": [f"Anomaly Score: {result['score']*100:.1f}%", f"Threshold Exceeded: {result.get('mismatches', 0)} mismatches"],
            "recommended_action": "Inspect log sequence for lateral movement or unusual user behavior."
        }

        # Check for signature matches to provide better reasoning
        for sig in self.signatures:
            if re.search(sig["pattern"], raw_log):
                explanation["reason"] = sig["reason"]
                explanation["mitre_technique"] = sig["technique"]
                explanation["evidence"].append(f"Pattern match: '{sig['pattern']}' found in logs")
                explanation["recommended_action"] = "Immediate investigation required. Check source IP activity."
                break

        return explanation

if __name__ == "__main__":
    explainer = AnomalyExplainer()
    sample_res = {"last_raw": "Failed password for root", "score": 0.85, "mismatches": 5}
    print(explainer.explain(sample_res))

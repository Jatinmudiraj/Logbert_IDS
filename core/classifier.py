import re

class LogClassifier:
    def __init__(self):
        # Known threat patterns based on common Linux logs
        self.rules = {
            "SSH Brute Force": [
                r"Failed password",
                r"Invalid user",
                r"Connection closed by authenticating user"
            ],
            "Unauthorized Access": [
                r"authentication failure",
                r"Permission denied",
                r"NOT in sudoers"
            ],
            "System Exploit Attempt": [
                r"possible SYN flood",
                r"segfault",
                r"Stack overflow",
                r"Possible break-in attempt"
            ],
            "Service Disruption": [
                r"out of memory",
                r"Kill process",
                r"Service failed"
            ]
        }

    def classify(self, log_line):
        for attack_type, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, log_line, re.IGNORECASE):
                    return attack_type
        return "Neural Outlier" # Default for anomalies the model finds but don't match rules

if __name__ == "__main__":
    classifier = LogClassifier()
    print(classifier.classify("Failed password for root from 1.2.3.4"))

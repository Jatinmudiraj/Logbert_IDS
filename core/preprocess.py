import re

def normalize_log(log):
    """
    Standardizes log lines by replacing variable parts with tokens.
    """
    # 1. IP normalization
    log = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP>', log)
    
    # 2. Port normalization
    log = re.sub(r'port \d+', 'port <PORT>', log)
    
    # 3. Number normalization (including PIDs)
    log = re.sub(r'\[\d+\]', '[<NUM>]', log)
    log = re.sub(r'pid=\d+', 'pid=<NUM>', log)
    log = re.sub(r'uid=\d+', 'uid=<NUM>', log)
    log = re.sub(r'euid=\d+', 'euid=<NUM>', log)
    
    # 4. Path normalization
    # Matches common Unix paths
    log = re.sub(r'/[a-zA-Z0-9._/-]+', '<PATH>', log)
    
    # 5. Timestamp removal/normalization
    # Matches common syslog formats: "Apr 25 10:12:33" or "2026-04-25T..."
    log = re.sub(r'[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}', '<TIME>', log)
    log = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?', '<TIME>', log)
    
    # 6. Host normalization (often the second/third word in syslog)
    # This is tricky without a full parser, but we can try to identify patterns
    # For now, we'll focus on obvious hostnames if they follow <TIME>
    log = re.sub(r'(<TIME>)\s+([a-zA-Z0-9-]+)\s+', r'\1 <HOST> ', log)
    
    # 7. User normalization
    # Matches "user admin", "user=root", etc.
    log = re.sub(r'user\s+([a-zA-Z0-9._-]+)', 'user <USER>', log)
    log = re.sub(r'user=([a-zA-Z0-9._-]+)', 'user=<USER>', log)
    
    # 8. Extra cleanup
    log = re.sub(r'\s+', ' ', log).strip()
    
    return log

if __name__ == "__main__":
    test_logs = [
        "Apr 25 10:12:33 ubuntu sshd[1234]: Failed password for invalid user admin from 192.168.20.5 port 55321 ssh2",
        "2017-05-16 00:00:01.001 1234 ERROR nova.api.openstack [req-999] [instance: 1] Exploit attempt: buffer overflow detected"
    ]
    for l in test_logs:
        print(f"Original: {l}")
        print(f"Normalized: {normalize_log(l)}\n")

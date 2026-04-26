import os
import json
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from core.preprocess import normalize_log

class LogTemplateParser:
    def __init__(self, config_file=None, persistence_path="model/drain3_state.bin"):
        config = TemplateMinerConfig()
        # Default config settings for better extraction
        config.drain_sim_th = 0.5
        config.drain_depth = 4
        
        self.miner = TemplateMiner(config=config)
        self.persistence_path = persistence_path
        
        if os.path.exists(persistence_path):
            self.load_state()

    def parse(self, raw_log):
        """
        Parses a raw log line into a template and template ID.
        """
        normalized = normalize_log(raw_log)
        result = self.miner.add_log_message(normalized)
        
        return {
            "raw_log": raw_log,
            "normalized_log": normalized,
            "template": result["template_mined"],
            "template_id": str(result["cluster_id"])
        }

    def save_state(self):
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with open(self.persistence_path, "wb") as f:
            # Note: drain3 uses a persistence handler normally, 
            # but for simplicity we'll just save the miner state if possible
            # or handle it via its own mechanisms.
            pass 

    def load_state(self):
        pass

if __name__ == "__main__":
    parser = LogTemplateParser()
    logs = [
        "Apr 25 10:12:33 ubuntu sshd[1234]: Failed password for invalid user admin from 192.168.20.5 port 55321 ssh2",
        "Apr 25 10:12:35 ubuntu sshd[1235]: Failed password for invalid user guest from 192.168.20.6 port 55322 ssh2",
        "Apr 25 10:12:40 ubuntu sshd[1236]: Accepted password for geeta from 192.168.1.10 port 22 ssh2"
    ]
    for l in logs:
        res = parser.parse(l)
        print(json.dumps(res, indent=2))

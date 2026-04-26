import torch
import os
import json
from core.model import LogBERT
from core.template_parser import LogTemplateParser
from core.preprocess import normalize_log
from core.explainer import AnomalyExplainer

class LogBERTDetectorService:
    def __init__(self, model_path="models/logbert_model.pth", meta_path="models/parser_meta.json"):
        self.model_path = model_path
        self.meta_path = meta_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.parser = LogTemplateParser()
        self.explainer = AnomalyExplainer()
        self.load_model()
        
        # Anomaly configuration
        self.threshold = 0.75 # Default threshold
        self.top_k = 5

    def load_model(self):
        if not os.path.exists(self.meta_path):
            print(f"[!] Meta path not found: {self.meta_path}")
            return
            
        with open(self.meta_path, 'r') as f:
            meta = json.load(f)
        
        self.vocab_size = meta['vocab_size']
        self.template_to_id = meta['template_to_id']
        
        self.model = LogBERT(vocab_size=self.vocab_size, d_model=256, nhead=8, num_layers=4)
        if os.path.exists(self.model_path):
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            print(f"[*] Model loaded from {self.model_path} ({self.device})")
        self.model.to(self.device)
        self.model.eval()

    def get_severity(self, score):
        if score >= 0.90: return "Critical"
        if score >= 0.75: return "High"
        if score >= 0.60: return "Medium"
        if score >= 0.40: return "Low"
        return "Normal"

    def analyze_sequence(self, raw_logs):
        """
        Analyzes a sequence of raw log lines.
        """
        if not raw_logs: return None
        
        parsed_results = [self.parser.parse(l) for l in raw_logs]
        template_ids = [int(res["template_id"]) for res in parsed_results]
        
        seq_tensor = torch.tensor([template_ids]).to(self.device)
        
        with torch.no_grad():
            logits, _ = self.model(seq_tensor)
            
            mismatches = 0
            for i in range(len(template_ids)):
                actual = template_ids[i]
                probs = torch.softmax(logits[0, i], dim=0)
                _, top_indices = torch.topk(probs, k=self.top_k)
                
                if actual not in top_indices:
                    mismatches += 1
            
            # Simple score: ratio of mismatched tokens
            anomaly_score = mismatches / len(template_ids)
            is_anomaly = anomaly_score > 0.15 # 15% mismatch threshold
            
            severity = self.get_severity(anomaly_score)
            
            output = {
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "severity": severity,
                "mismatches": mismatches,
                "templates": [res["template"] for res in parsed_results],
                "template_ids": template_ids,
                "last_raw": raw_logs[-1]
            }
            
            if is_anomaly:
                explanation = self.explainer.explain(output)
                output.update(explanation)
                
            return output

if __name__ == "__main__":
    service = LogBERTDetectorService()
    test_seq = [
        "Apr 25 10:12:33 ubuntu sshd[1234]: Failed password for invalid user admin from 192.168.20.5 port 55321 ssh2",
        "Apr 25 10:12:35 ubuntu sshd[1235]: Failed password for invalid user admin from 192.168.20.5 port 55322 ssh2",
    ]
    result = service.analyze_sequence(test_seq)
    print(json.dumps(result, indent=2))

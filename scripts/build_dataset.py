import os
import json
import random
from core.template_parser import LogTemplateParser

def build_dataset(input_file, output_dir, window_size=20, stride=1):
    parser = LogTemplateParser()
    
    print(f"[*] Reading logs from {input_file}...")
    with open(input_file, 'r', errors='ignore') as f:
        lines = f.readlines()
    
    print(f"[*] Parsing {len(lines)} logs...")
    parsed_logs = []
    for line in lines:
        if not line.strip(): continue
        res = parser.parse(line)
        
        # Heuristic labeling for baseline
        label = 0
        attack_type = "benign"
        
        suspicious_keywords = ["failed", "invalid", "unauthorized", "exploit", "overflow", "break-in", "authentication failure"]
        if any(kw in line.lower() for kw in suspicious_keywords):
            label = 1
            attack_type = "suspicious"
            if "exploit" in line.lower(): attack_type = "exploit"
            if "failed password" in line.lower(): attack_type = "brute_force"

        parsed_logs.append({
            "template_id": res["template_id"],
            "label": label,
            "attack_type": attack_type,
            "raw": line.strip()
        })
    
    print(f"[*] Building sequences (window_size={window_size}, stride={stride})...")
    sequences = []
    for i in range(0, len(parsed_logs) - window_size + 1, stride):
        window = parsed_logs[i : i + window_size]
        
        # Sequence label is 1 if ANY log in window is an attack
        seq_label = 1 if any(log["label"] == 1 for log in window) else 0
        
        # Major attack type in window
        attack_types = [log["attack_type"] for log in window if log["label"] == 1]
        seq_attack_type = max(set(attack_types), key=attack_types.count) if attack_types else "benign"
        
        sequences.append({
            "sequence_id": len(sequences),
            "sequence": [log["template_id"] for log in window],
            "label": seq_label,
            "attack_type": seq_attack_type,
            "raw_logs": [log["raw"] for log in window]
        })
    
    random.shuffle(sequences)
    
    train_split = int(0.7 * len(sequences))
    val_split = int(0.85 * len(sequences))
    
    train_seqs = sequences[:train_split]
    val_seqs = sequences[train_split:val_split]
    test_seqs = sequences[val_split:]
    
    os.makedirs(output_dir, exist_ok=True)
    
    def save_jsonl(data, filename):
        path = os.path.join(output_dir, filename)
        with open(path, 'w') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
        print(f"[+] Saved {len(data)} sequences to {path}")

    save_jsonl(train_seqs, "train_mixed.jsonl")
    save_jsonl(val_seqs, "val_mixed.jsonl")
    save_jsonl(test_seqs, "test_mixed.jsonl")

if __name__ == "__main__":
    input_log = "/raid/home/geeta/IDS/test_logs.txt"
    output_dir = "/raid/home/geeta/Logbert_IDS/data/processed"
    build_dataset(input_log, output_dir)

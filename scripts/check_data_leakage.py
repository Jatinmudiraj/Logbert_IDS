import json
import os

def check_leakage(processed_dir="data/processed"):
    splits = ["train_mixed.jsonl", "val_mixed.jsonl", "test_mixed.jsonl"]
    data = {}
    
    print("[*] Loading datasets for leakage check...")
    for split in splits:
        path = os.path.join(processed_dir, split)
        if not os.path.exists(path):
            print(f"[!] Split not found: {path}")
            continue
            
        with open(path, 'r') as f:
            # We use the sequence string (template IDs) as a hashable key
            data[split] = [json.loads(line) for line in f]
            
    print("\n=== Data Leakage Report ===")
    
    # 1. Exact Sequence Overlap
    seq_sets = {split: set(tuple(item['sequence']) for item in data[split]) for split in splits}
    
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            s1, s2 = splits[i], splits[j]
            overlap = seq_sets[s1].intersection(seq_sets[s2])
            overlap_pct1 = (len(overlap) / len(seq_sets[s1])) * 100 if len(seq_sets[s1]) > 0 else 0
            overlap_pct2 = (len(overlap) / len(seq_sets[s2])) * 100 if len(seq_sets[s2]) > 0 else 0
            
            print(f"Overlap between {s1} and {s2}:")
            print(f"  - Common Sequences: {len(overlap)}")
            print(f"  - % of {s1}: {overlap_pct1:.2f}%")
            print(f"  - % of {s2}: {overlap_pct2:.2f}%")

    # 2. Raw Log Overlap (approximate)
    log_sets = {split: set(tuple(item['raw_logs']) for item in data[split]) for split in splits}
    print("\n--- Raw Log Content Overlap ---")
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            s1, s2 = splits[i], splits[j]
            overlap = log_sets[s1].intersection(log_sets[s2])
            print(f"Overlap between {s1} and {s2}: {len(overlap)} windows")

    # 3. Label Distribution
    print("\n--- Class Distribution ---")
    for split in splits:
        labels = [item['label'] for item in data[split]]
        normals = labels.count(0)
        attacks = labels.count(1)
        print(f"{split}:")
        print(f"  - Normal: {normals} ({normals/len(labels)*100:.1f}%)")
        print(f"  - Attack: {attacks} ({attacks/len(labels)*100:.1f}%)")

if __name__ == "__main__":
    check_leakage()

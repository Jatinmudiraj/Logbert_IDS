import os
import json
import torch
from core.model import LogBERT

def generate_attack_report(test_data_path="data/processed/test_mixed.jsonl"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    meta_path = os.path.join(project_root, 'models', 'parser_meta.json')
    model_path = os.path.join(project_root, 'models', 'logbert_model.pth')
    
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    vocab_size = meta['vocab_size']
    
    model = LogBERT(vocab_size=vocab_size, d_model=256, nhead=8, num_layers=4)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()

    attack_stats = {} # attack_type -> {tp, fn, total}

    print(f"[*] Analyzing performance per attack type on {test_data_path}...")
    
    with open(test_data_path, 'r') as f:
        for line in f:
            item = json.loads(line)
            attack_type = item.get('attack_type', 'unknown')
            true_label = item['label']
            seq_ids = [int(tid) for tid in item['sequence']]
            
            if attack_type not in attack_stats:
                attack_stats[attack_type] = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "total": 0}
            
            attack_stats[attack_type]["total"] += 1
            
            seq_tensor = torch.tensor([seq_ids])
            with torch.no_grad():
                logits, _ = model(seq_tensor)
                mismatches = 0
                for i in range(len(seq_ids)):
                    actual = seq_ids[i]
                    probs = torch.softmax(logits[0, i], dim=0)
                    _, top_indices = torch.topk(probs, k=5)
                    if actual not in top_indices:
                        mismatches += 1
                
                pred_label = 1 if mismatches > 2 else 0
                
                if true_label == 1:
                    if pred_label == 1: attack_stats[attack_type]["tp"] += 1
                    else: attack_stats[attack_type]["fn"] += 1
                else:
                    if pred_label == 1: attack_stats[attack_type]["fp"] += 1
                    else: attack_stats[attack_type]["tn"] += 1

    print("\n" + "="*50)
    print(f"{'Attack Type':<20} | {'Precision':<10} | {'Recall':<10} | {'F1':<10}")
    print("-" * 50)
    
    for atype, stats in attack_stats.items():
        tp = stats["tp"]
        fn = stats["fn"]
        fp = stats["fp"]
        tn = stats["tn"]
        
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0 # If no fp, precision is 1
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        if atype == "benign":
            # For benign, we care about TNR
            tnr = tn / (tn + fp) if (tn + fp) > 0 else 0
            print(f"{atype:<20} | {'N/A':<10} | {tnr*100:<9.2f}% (TNR)")
        else:
            print(f"{atype:<20} | {precision*100:<9.2f}% | {recall*100:<9.2f}% | {f1*100:<9.2f}%")
    print("="*50)

if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd())
    generate_attack_report()

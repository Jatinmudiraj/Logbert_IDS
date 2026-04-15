import torch
import json
import os
from logbert_model import LogBERT
from log_dataset import LogSequenceDataset, DataLoader, collate_fn
from log_parser import LogParser

def analyze_false_positives(log_file):
    base_dir = '/home/geeta/ids/Logbert_IDS'
    meta_path = os.path.join(base_dir, 'parser_meta.json')
    model_path = os.path.join(base_dir, 'logbert_model.pth')
    
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    
    template_to_id = meta['template_to_id']
    vocab_size = meta['vocab_size']
    dist_token = template_to_id['[DIST]']
    
    model = LogBERT(vocab_size=vocab_size)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    
    def clean_log(log):
        import re
        log = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', log)
        log = re.sub(r'\d+', '<NUM>', log)
        log = re.sub(r' +', ' ', log).strip()
        return log

    with open(log_file, 'r', errors='ignore') as f:
        logs = f.readlines()
    
    log_ids = [template_to_id.get(clean_log(l), 0) for l in logs]
    dataset = LogSequenceDataset(log_ids, window_size=10, mask_ratio=0.15, dist_token=dist_token)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=collate_fn)
    
    print(f"[*] Analyzing {len(logs)} lines from {log_file}...")
    fp_details = []
    for i, (seq, labels) in enumerate(dataloader):
        with torch.no_grad():
            logits, dist_h = model(seq)
            mask_indices = (seq == 0).nonzero(as_tuple=True)
            if mask_indices[0].numel() == 0: continue
            
            masked_logits = logits[mask_indices]
            actual_labels = labels[mask_indices]
            
            # Probability distribution
            probs = torch.softmax(masked_logits, dim=1)
            top_probs, top_g_indices = torch.topk(probs, k=5, dim=1)
            
            for j in range(len(actual_labels)):
                actual = actual_labels[j].item()
                if actual not in top_g_indices[j]:
                    # This is an "anomaly" according to current logic
                    # Capture the log line (approximate index)
                    log_line = logs[i+j] if i+j < len(logs) else "unknown"
                    fp_details.append({
                        "sequence": i,
                        "line": log_line.strip(),
                        "actual_token": actual,
                        "top_candidates": top_g_indices[j].tolist(),
                        "top_probs": top_probs[j].tolist(),
                        "actual_prob": probs[j, actual].item() if actual != 0 else 0
                    })
                    
    # Print the first 10 "Anomalies" to understand why
    print("\n[!] Top 10 Anomalies found (Potential False Positives if this is normal data):")
    for fp in fp_details[:10]:
        print(f"Seq {fp['sequence']}: {fp['line']}")
        print(f"  Actual Prob: {fp['actual_prob']:.6f}")
        print(f"  Top Candidates: {fp['top_candidates']} with Probs {fp['top_probs']}")
        print("-" * 20)

if __name__ == "__main__":
    analyze_false_positives('/home/geeta/logs/ubuntu1/log/auth.log.1')

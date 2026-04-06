import os
import torch
import torch.nn as nn
import json
import argparse
from logbert_model import LogBERT
from log_dataset import LogSequenceDataset, DataLoader, collate_fn
from log_parser import LogParser

def detect_anomalies(log_file, g=5, r=1):
    # Use relative paths for portability
    base_dir = os.path.dirname(os.path.abspath(__file__))
    meta_path = os.path.join(base_dir, 'parser_meta.json')
    model_path = os.path.join(base_dir, 'logbert_model.pth')

    # Load Parser from saved metadata
    if not os.path.exists(meta_path):
        print(f"[!] Metadata file not found at: {meta_path}")
        return
        
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    
    template_to_id = meta['template_to_id']
    templates = meta['templates']
    vocab_size = meta['vocab_size']
    dist_token = template_to_id['[DIST]']
    
    # Load Model
    model = LogBERT(vocab_size=vocab_size)
    if not os.path.exists(model_path):
        print(f"[!] Model weights not found at: {model_path}")
        return
        
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    
    # Load Logs to test
    if not os.path.exists(log_file):
        print(f"[!] Log file not found at: {log_file}")
        return
        
    with open(log_file, 'r', errors='ignore') as f:
        logs = f.readlines()
    
    # Use same parser logic to convert to IDs
    def clean_log(log):
        import re
        log = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', log)
        log = re.sub(r'\d+', '<NUM>', log)
        log = re.sub(r' +', ' ', log).strip()
        return log

    log_ids = [template_to_id.get(clean_log(l), 0) for l in logs]
    
    # Dataset processing
    dataset = LogSequenceDataset(log_ids, window_size=10, mask_ratio=0.15, dist_token=dist_token)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=collate_fn)
    
    anomalies_found = 0
    total_sequences = 0
    
    print(f"[*] Started Anomaly Detection on {log_file}...")
    for i, (seq, labels) in enumerate(dataloader):
        total_sequences += 1
        with torch.no_grad():
            logits, _ = model(seq)
            mask_indices = (seq == 0).nonzero(as_tuple=True)
            if mask_indices[0].numel() == 0: continue
            masked_logits = logits[mask_indices]
            actual_labels = labels[mask_indices]
            _, top_g_indices = torch.topk(masked_logits, k=g, dim=1)
            
            mismatches = 0
            for j in range(len(actual_labels)):
                if actual_labels[j] not in top_g_indices[j]:
                    mismatches += 1
            if mismatches > r:
                anomalies_found += 1
                # Only print the first few anomalies to avoid spamming the terminal
                if anomalies_found < 10:
                    print(f"[ALERT] Seq {i} ANOMALOUS (Mismatches: {mismatches})")
                
    print(f"\n[+] Analysis Complete: {anomalies_found} anomalies in {total_sequences} sequences.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LogBERT Detection')
    parser.add_argument('--file', type=str, required=True, help='Path to log file')
    args = parser.parse_args()
    
    detect_anomalies(args.file, g=5, r=1)

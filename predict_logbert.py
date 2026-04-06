import os
import torch
import torch.nn as nn
import json
import argparse
import time
from logbert_model import LogBERT
from log_dataset import LogSequenceDataset, DataLoader, collate_fn
from log_parser import LogParser

def clean_log(log):
    import re
    log = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', log)
    log = re.sub(r'\d+', '<NUM>', log)
    log = re.sub(r' +', ' ', log).strip()
    return log

def detect_anomalies(log_file, g=5, r=1, live=False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    meta_path = os.path.join(base_dir, 'parser_meta.json')
    model_path = os.path.join(base_dir, 'logbert_model.pth')

    if not os.path.exists(meta_path):
        print(f"[!] Metadata file not found at: {meta_path}")
        return
        
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    
    template_to_id = meta['template_to_id']
    vocab_size = meta['vocab_size']
    dist_token = template_to_id['[DIST]']
    
    model = LogBERT(vocab_size=vocab_size)
    if not os.path.exists(model_path):
        print(f"[!] Model weights not found at: {model_path}")
        return
        
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    
    if not os.path.exists(log_file):
        print(f"[!] Log file not found at: {log_file}")
        return

    # Buffer for sequence window (10 logs)
    sequence_buffer = []

    if live:
        print(f"[*] ENTERING LIVE MODE: Monitoring {log_file} in real-time...")
        with open(log_file, 'r', errors='ignore') as f:
            # Go to end of file to start monitoring new logs
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line or line.strip() == "":
                    time.sleep(0.5)
                    continue
                
                # Process the new line
                log_id = template_to_id.get(clean_log(line), 0)
                sequence_buffer.append(log_id)
                
                if len(sequence_buffer) >= 10:
                    # Create sequence with [DIST] token
                    seq = [dist_token] + sequence_buffer[-10:]
                    seq_tensor = torch.tensor([seq])
                    
                    with torch.no_grad():
                        # In live mode, we mask the last token to predict what should be there
                        # but simple cross-entropy checks are faster.
                        # Masking the last token (index 10)
                        masked_seq = seq_tensor.clone()
                        masked_seq[0, -1] = 0 # 0 is [MASK]
                        
                        logits, _ = model(masked_seq)
                        last_token_logits = logits[0, -1]
                        _, top_g_indices = torch.topk(last_token_logits, k=g)
                        
                        actual_token = sequence_buffer[-1]
                        if actual_token not in top_g_indices:
                            print(f"[LIVE ALERT] {time.strftime('%H:%M:%S')} - Anomalous activity detected!")
                            print(f"   Log Line: {line.strip()}")
                
                # Keep buffer at manageable size
                if len(sequence_buffer) > 20:
                    sequence_buffer = sequence_buffer[-10:]

    else:
        # Static Analysis (same as before)
        with open(log_file, 'r', errors='ignore') as f:
            logs = f.readlines()
        log_ids = [template_to_id.get(clean_log(l), 0) for l in logs]
        dataset = LogSequenceDataset(log_ids, window_size=10, mask_ratio=0.15, dist_token=dist_token)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=collate_fn)
        
        print(f"[*] Static Analysis: Analyzing {len(logs)} lines from {log_file}...")
        anomalies = 0
        for i, (seq, labels) in enumerate(dataloader):
            with torch.no_grad():
                logits, _ = model(seq)
                mask_indices = (seq == 0).nonzero(as_tuple=True)
                if mask_indices[0].numel() == 0: continue
                masked_logits = logits[mask_indices]
                actual_labels = labels[mask_indices]
                _, top_g_indices = torch.topk(masked_logits, k=g, dim=1)
                for j in range(len(actual_labels)):
                    if actual_labels[j] not in top_g_indices[j]:
                        anomalies += 1
                        if anomalies < 20: print(f"[ALERT] Sequence {i} is anomalous.")
                        break
        print(f"[+] Static Analysis Complete: {anomalies} anomalies detected.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LogBERT Detection')
    parser.add_argument('--file', type=str, required=True, help='Path to log file')
    parser.add_argument('--live', action='store_true', help='Enable real-time tailing mode')
    args = parser.parse_args()
    
    detect_anomalies(args.file, g=5, r=1, live=args.live)

import torch
import json
from logbert_model import LogBERT
from log_dataset import LogSequenceDataset, DataLoader, collate_fn
from log_parser import LogParser
import random

def detect_anomalies(log_file, g=5, r=1):
    # Load Parser from saved metadata
    with open('/raid/home/geeta/geeta/LogBERT_IDS/parser_meta.json', 'r') as f:
        meta = json.load(f)
    template_to_id = meta['template_to_id']
    templates = meta['templates']
    vocab_size = meta['vocab_size']
    dist_token = template_to_id['[DIST]']
    
    # Load Model
    model = LogBERT(vocab_size=vocab_size)
    model.load_state_dict(torch.load('/raid/home/geeta/geeta/LogBERT_IDS/logbert_model.pth'))
    model.eval()
    
    # Load Logs to test
    with open(log_file, 'r', errors='ignore') as f:
        logs = f.readlines()
    
    # Use same parser logic to convert to IDs
    # Manual conversion because parser object isn't pickled
    def clean_log(log):
        import re
        log = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', log)
        log = re.sub(r'\d+', '<NUM>', log)
        log = re.sub(r' +', ' ', log).strip()
        return log

    log_ids = [template_to_id.get(clean_log(l), 0) for l in logs]
    
    # Dataset and Dataloader
    # In prediction, we mask tokens one by one or randomly as per the strategy
    dataset = LogSequenceDataset(log_ids, window_size=10, mask_ratio=0.15, dist_token=dist_token)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=collate_fn)
    
    anomalies_found = 0
    total_sequences = 0
    
    for i, (seq, labels) in enumerate(dataloader):
        total_sequences += 1
        with torch.no_grad():
            logits, _ = model(seq) # (1, seq_len, vocab)
            
            # Find masked tokens (0)
            mask_indices = (seq == 0).nonzero(as_tuple=True)
            if mask_indices[0].numel() == 0:
                continue
                
            masked_logits = logits[mask_indices] # (num_mask, vocab)
            actual_labels = labels[mask_indices] # (num_mask)
            
            # Top-g candidates
            top_g_probs, top_g_indices = torch.topk(masked_logits, k=g, dim=1)
            
            # Check if actual label is in top-g
            mismatches = 0
            for j in range(len(actual_labels)):
                if actual_labels[j] not in top_g_indices[j]:
                    mismatches += 1
            
            if mismatches > r:
                # Sequence is anomalous!
                anomalies_found += 1
                print(f"Sequence {i} identified as ANOMALOUS (Mismatches: {mismatches})")
                
    print(f"Prediction Complete: {anomalies_found} Anomalous Sequences out of {total_sequences} total sequences.")

if __name__ == "__main__":
    detect_anomalies('/raid/home/geeta/geeta/all_logs_consolidated/ssh.log', g=5, r=1)

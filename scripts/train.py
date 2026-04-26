import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import json
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.model import LogBERT
from core.dataset import LogSequenceDataset, DataLoader, collate_fn
from core.parser import LogParser
import json

def train_logbert(train_file, epochs=5, batch_size=32, lr=0.001):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    model_path = os.path.join(project_root, 'models', 'logbert_model.pth')
    meta_path = os.path.join(project_root, 'models', 'parser_meta.json')
    
    if not os.path.exists(train_file):
        print(f"[!] Train file not found: {train_file}")
        return
        
    print(f"[*] Loading sequences from {train_file}...")
    log_ids_list = []
    with open(train_file, 'r') as f:
        for line in f:
            item = json.loads(line)
            # Only train on normal sequences if we want to follow anomaly detection best practices
            # But for this script, we'll take all provided training data.
            if item.get('label', 0) == 0:
                log_ids_list.append([int(tid) for tid in item['sequence']])
    
    if not log_ids_list:
        print("[!] No normal sequences found for training.")
        return

    # Flatten for parser if needed, but here we already have IDs.
    # We need vocab_size from meta if it exists, or calculate it.
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    vocab_size = meta['vocab_size']
    dist_token = meta['template_to_id'].get('[DIST]', 0)
    
    # Dataset and Dataloader
    # Note: LogSequenceDataset in core/dataset.py might expect a flat list of IDs.
    # I'll need to check core/dataset.py.
    # If it's already sequences, I might need a different Dataset class.
    
    # Let's check core/dataset.py
    from core.dataset import LogSequenceDataset, DataLoader, collate_fn
    
    # If LogSequenceDataset expects a flat list, we flatten our normal sequences
    flat_ids = [tid for seq in log_ids_list for tid in seq]
    
    dataset = LogSequenceDataset(flat_ids, window_size=20, mask_ratio=0.15, dist_token=dist_token)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    
    # Model
    model = LogBERT(vocab_size=vocab_size, d_model=256, nhead=8, num_layers=4)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    ce_loss = nn.CrossEntropyLoss()
    
    model.train()
    print(f"[*] Starting training on {len(log_ids_list)} normal sequences...")
    for epoch in range(epochs):
        total_loss = 0
        for i, (seq, labels) in enumerate(dataloader):
            optimizer.zero_grad()
            logits, dist_h = model(seq)
            mask_indices = (seq == 0).nonzero(as_tuple=True)
            if mask_indices[0].numel() > 0:
                masked_logits = logits[mask_indices]
                masked_labels = labels[mask_indices]
                loss_mlkp = ce_loss(masked_logits, masked_labels)
            else:
                loss_mlkp = torch.tensor(0.0, requires_grad=True)
            
            loss_vhm = model.get_vhm_loss(dist_h)
            loss = loss_mlkp + 0.1 * loss_vhm
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")
        
    torch.save(model.state_dict(), model_path)
    print(f"Training Complete! Model saved at {model_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='LogBERT Training')
    parser.add_argument('--file', type=str, help='Path to training jsonl file')
    args = parser.parse_args()
    
    train_file = args.file if args.file else "data/processed/train_mixed.jsonl"
    train_logbert(train_file)

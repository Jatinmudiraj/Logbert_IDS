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

def calibrate_on_local(normal_log_file, epochs=2):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    model_path = os.path.join(project_root, 'models', 'logbert_model.pth')
    meta_path = os.path.join(project_root, 'models', 'parser_meta.json')
    
    # 1. Load Current State
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    vocab_size = meta['vocab_size']
    template_to_id = meta['template_to_id']
    dist_token = template_to_id['[DIST]']
    
    model = LogBERT(vocab_size=vocab_size)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    
    # 2. Prepare Local Data
    print(f"[*] Reading local 'normal' logs from {normal_log_file}...")
    with open(normal_log_file, 'r', errors='ignore') as f:
        logs = f.readlines()
    
    def clean_log(log):
        import re
        log = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', log)
        log = re.sub(r'\d+', '<NUM>', log)
        log = re.sub(r' +', ' ', log).strip()
        return log

    log_ids = [template_to_id.get(clean_log(l), 0) for l in logs]
    dataset = LogSequenceDataset(log_ids, window_size=10, mask_ratio=0.15, dist_token=dist_token)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True, collate_fn=collate_fn)
    
    # 3. Fine-tuning Loop
    print(f"[*] Calibrating model to local environment patterns...")
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    ce_loss = nn.CrossEntropyLoss()
    
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for seq, labels in dataloader:
            optimizer.zero_grad()
            logits, dist_h = model(seq)
            
            # MLKP Loss
            mask_indices = (seq == 0).nonzero(as_tuple=True)
            if mask_indices[0].numel() > 0:
                loss_mlkp = ce_loss(logits[mask_indices], labels[mask_indices])
            else:
                loss_mlkp = 0
            
            # VHM Loss (Crucial for confidence)
            loss_vhm = model.get_vhm_loss(dist_h)
            
            loss = loss_mlkp + 0.1 * loss_vhm
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"      Epoch {epoch+1}/{epochs} - Stability: {total_loss/len(dataloader):.4f}")
    
    # 4. Re-calculate Hypersphere Center and Average Distance
    model.eval()
    all_dists = []
    new_center = torch.zeros_like(model.center)
    count = 0
    with torch.no_grad():
        for seq, _ in dataloader:
            _, dist_h = model(seq)
            new_center += torch.sum(dist_h, dim=0)
            count += dist_h.size(0)
    
    model.center.data = new_center / count
    
    with torch.no_grad():
        for seq, _ in dataloader:
            _, dist_h = model(seq)
            dists = torch.sum((dist_h - model.center)**2, dim=1)
            all_dists.extend(dists.tolist())
    
    suggested_threshold = float(torch.quantile(torch.tensor(all_dists), 0.99).item())
    
    # 5. Save Improved Model
    torch.save(model.state_dict(), model_path)
    print(f"[+] Calibration Complete!")
    print(f"[+] Optimal Distance Threshold for this machine: {suggested_threshold:.4f}")
    print(f"[+] Accuracy and Confidence should now be significantly higher.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Calibrate LogBERT to current machine')
    parser.add_argument('--file', type=str, required=True, help='Path to a normal log file representative of this machine')
    args = parser.parse_args()
    
    calibrate_on_local(args.file)

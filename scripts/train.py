import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.model import LogBERT
from core.dataset import LogSequenceDataset, DataLoader, collate_fn
from core.parser import LogParser
import json

def train_logbert(log_file, epochs=5, batch_size=32, lr=0.001):
    # Use relative paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    model_path = os.path.join(project_root, 'models', 'logbert_model.pth')
    meta_path = os.path.join(project_root, 'models', 'parser_meta.json')
    
    # Load Logs
    if not os.path.exists(log_file):
        print(f"[!] Log file not found: {log_file}")
        return
        
    with open(log_file, 'r', errors='ignore') as f:
        logs = f.readlines()
    
    # Parse Logs to get Vocabulary and IDs
    parser = LogParser(threshold=2)
    parser.fit(logs)
    log_ids = parser.transform(logs)
    
    vocab_size = parser.get_vocab_size()
    dist_token = parser.template_to_id['[DIST]']
    
    # Dataset and Dataloader
    dataset = LogSequenceDataset(log_ids, window_size=10, mask_ratio=0.15, dist_token=dist_token)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    
    # Model
    model = LogBERT(vocab_size=vocab_size, d_model=256, nhead=8, num_layers=4)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Losses
    ce_loss = nn.CrossEntropyLoss()
    
    # Training Loop
    model.train()
    print(f"[*] Starting training on {log_file} for {epochs} epochs...")
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
        
    # Save Model and Parser metadata
    torch.save(model.state_dict(), model_path)
    with open(meta_path, 'w') as f:
        json.dump({
            "templates": parser.templates,
            "template_to_id": parser.template_to_id,
            "vocab_size": vocab_size
        }, f)
        
    print(f"Training Complete! Model saved at {model_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='LogBERT Training')
    parser.add_argument('--file', type=str, required=True, help='Path to training log file')
    args = parser.parse_args()
    
    train_logbert(args.file)

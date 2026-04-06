import torch
import torch.nn as nn
import torch.optim as optim
from logbert_model import LogBERT
from log_dataset import LogSequenceDataset, DataLoader, collate_fn
from log_parser import LogParser
import json

def train_logbert(log_file, epochs=10, batch_size=32, lr=0.001):
    # Load Logs
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
    for epoch in range(epochs):
        total_loss = 0
        for i, (seq, labels) in enumerate(dataloader):
            optimizer.zero_grad()
            
            # Forward pass
            logits, dist_h = model(seq) # logits: (batch, seq, vocab), dist_h: (batch, d_model)
            
            # MLKP Loss: Only for masked items (mask token is 0)
            # Find indices where seq is 0
            mask_indices = (seq == 0).nonzero(as_tuple=True)
            if mask_indices[0].numel() > 0:
                masked_logits = logits[mask_indices] # (num_mask, vocab)
                masked_labels = labels[mask_indices] # (num_mask)
                loss_mlkp = ce_loss(masked_logits, masked_labels)
            else:
                loss_mlkp = torch.tensor(0.0, requires_grad=True)
                
            # VHM Loss
            loss_vhm = model.get_vhm_loss(dist_h)
            
            # Combine Losses
            loss = loss_mlkp + 0.1 * loss_vhm
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")
        
    # Save Model and Parser metadata
    torch.save(model.state_dict(), '/raid/home/geeta/geeta/LogBERT_IDS/logbert_model.pth')
    with open('/raid/home/geeta/geeta/LogBERT_IDS/parser_meta.json', 'w') as f:
        json.dump({
            "templates": parser.templates,
            "template_to_id": parser.template_to_id,
            "vocab_size": vocab_size
        }, f)
        
    print("Training Complete! Saved model and parser metadata.")

if __name__ == "__main__":
    train_logbert('/raid/home/geeta/geeta/all_logs_consolidated/ssh.log', epochs=5)

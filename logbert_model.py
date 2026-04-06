import torch
import torch.nn as nn
from transformers import BertConfig, BertModel

class LogBERT(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_layers=4, dropout=0.1):
        super(LogBERT, self).__init__()
        # Use a lightweight BERT architecture for log sequences
        config = BertConfig(
            vocab_size=vocab_size,
            hidden_size=d_model,
            num_hidden_layers=num_layers,
            num_attention_heads=nhead,
            intermediate_size=d_model*4,
            hidden_dropout_prob=dropout,
            attention_probs_dropout_prob=dropout,
            max_position_embeddings=512, # Max sequence length
        )
        self.bert = BertModel(config)
        
        # MLKP Head
        self.mlkp_head = nn.Linear(d_model, vocab_size)
        
        # VHM Head - Distance calculation
        # The center c of the hypersphere is usually calculated after training or maintained online.
        self.center = nn.Parameter(torch.randn(d_model)) 
        
    def forward(self, x):
        # x shape: (batch_size, seq_len)
        output = self.bert(x)
        hidden_states = output.last_hidden_state # shape: (batch_size, seq_len, d_model)
        
        # Prediction for each token (MLKP)
        logits = self.mlkp_head(hidden_states)
        
        # Dist token representation is the first token of each sequence
        dist_h = hidden_states[:, 0, :] # (batch_size, d_model)
        
        return logits, dist_h

    def get_vhm_loss(self, dist_h):
        # Loss based on distance between the dist_h and center c
        loss = torch.mean(torch.sum((dist_h - self.center)**2, dim=1))
        return loss

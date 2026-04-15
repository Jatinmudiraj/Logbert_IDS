import torch
from torch.utils.data import Dataset, DataLoader
import random

class LogSequenceDataset(Dataset):
    def __init__(self, log_ids, window_size=5, step_size=1, mask_ratio=0.15, dist_token=None, pad_token=-1):
        self.sequences = []
        self.window_size = window_size
        self.mask_ratio = mask_ratio
        self.dist_token = dist_token
        self.pad_token = pad_token

        # Create sliding window sequences
        for i in range(0, len(log_ids) - window_size, step_size):
            seq = log_ids[i:i+window_size]
            # Add [DIST] token at the beginning as per LogBERT paper
            if dist_token is not None:
                seq = [dist_token] + seq
            self.sequences.append(torch.tensor(seq))

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx].clone()
        labels = seq.clone()
        
        # Masking logic
        # Skip [DIST] and [PAD] for masking
        mask_indices = []
        for i in range(len(seq)):
            if seq[i] != self.dist_token and seq[i] != self.pad_token:
                if random.random() < self.mask_ratio:
                    mask_indices.append(i)
        
        for i in mask_indices:
            # In BERT, [MASK] token index is 0
            seq[i] = 0
            
        return seq, labels

def collate_fn(batch):
    sequences, labels = zip(*batch)
    return torch.stack(sequences), torch.stack(labels)

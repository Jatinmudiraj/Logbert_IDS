import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.model import LogBERT
from core.dataset import LogSequenceDataset, DataLoader, collate_fn
from core.parser import LogParser

def evaluate_and_save():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    meta_path = os.path.join(project_root, 'models', 'parser_meta.json')
    model_path = os.path.join(project_root, 'models', 'logbert_model.pth')
    
    import json # Ensure json is imported
    # Load metadata
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    template_to_id = meta['template_to_id']
    vocab_size = meta['vocab_size']
    dist_token = template_to_id.get('[DIST]', 0)
    
    # Load model
    model = LogBERT(vocab_size=vocab_size, d_model=256, nhead=8, num_layers=4)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()

    # Load test labeled data (using a default placeholder if not provided)
    test_data_path = os.path.join(project_root, 'data', 'test_labeled.json')
    if not os.path.exists(test_data_path):
        print(f"[!] Warning: Test labeled data not found at {test_data_path}")
        return
    with open(test_data_path, 'r') as f:
        test_data = json.load(f)

    # Clean function matching parser
    def clean_log(log):
        import re
        log = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', log)
        log = re.sub(r'\d+', '<NUM>', log)
        log = re.sub(r' +', ' ', log).strip()
        return log

    output_lines = []
    output_lines.append("=== LogBERT IDS Final Evaluation Results ===")
    
    total_tp = 0
    total_fn = 0
    total_fp = 0
    total_tn = 0
    
    for label_type, target_label in [("Normal", 0), ("Attack", 1)]:
        lines = [item['log'] for item in test_data if item['label'] == target_label]
        # Convert lines to mapped IDs
        log_ids = [template_to_id.get(clean_log(l), 0) for l in lines]
        
        if not log_ids:
            continue
            
        dataset = LogSequenceDataset(log_ids, window_size=10, mask_ratio=0.15, dist_token=dist_token)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=collate_fn)
        
        anomalies_found = 0
        total_sequences = 0
        
        for seq, labels in dataloader:
            total_sequences += 1
            with torch.no_grad():
                logits, _ = model(seq) # logits: (batch, seq, vocab)
                
                # Find masked items
                mask_indices = (seq == 0).nonzero(as_tuple=True)
                if mask_indices[0].numel() == 0:
                    continue
                
                masked_logits = logits[mask_indices]
                actual_labels = labels[mask_indices]
                
                # Top-5 items
                _, top_g_indices = torch.topk(masked_logits, k=5, dim=1)
                
                mismatches = sum(1 for j in range(len(actual_labels)) if actual_labels[j] not in top_g_indices[j])
                
                if mismatches > 1: # anomaly threshold r=1
                    anomalies_found += 1
                    
        if total_sequences > 0:
            anomaly_rate = anomalies_found / total_sequences
            output_lines.append(f"\n[{label_type} Set Evaluation]")
            output_lines.append(f"Evaluated Sequences: {total_sequences}")
            output_lines.append(f"Detected as Anomalous (Attack): {anomalies_found}")
            
            if target_label == 1:
                total_tp = anomalies_found
                total_fn = total_sequences - anomalies_found
                output_lines.append(f"-> True Positive Rate (Recall/Sensitivity): {anomaly_rate*100:.2f}%")
            else:
                total_fp = anomalies_found
                total_tn = total_sequences - anomalies_found
                output_lines.append(f"-> False Positive Rate: {anomaly_rate*100:.2f}%")
                output_lines.append(f"-> True Negative Rate (Specificity): {(1-anomaly_rate)*100:.2f}%")
                
    accuracy = (total_tp + total_tn) / (total_tp + total_tn + total_fp + total_fn) if (total_tp + total_tn + total_fp + total_fn) > 0 else 0
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    output_lines.append("\n=== Overall Metrics ===")
    output_lines.append(f"Overall Accuracy: {accuracy*100:.2f}%")
    output_lines.append(f"Precision: {precision*100:.2f}%")
    output_lines.append(f"Recall: {recall*100:.2f}%")
    output_lines.append(f"F1-Score: {f1*100:.2f}%")
    
    result_path = os.path.join(project_root, 'backup', 'result.txt')
    with open(result_path, 'w') as f:
        f.write("\n".join(output_lines) + "\n")
        
    print("Results saved successfully.")

if __name__ == '__main__':
    evaluate_and_save()

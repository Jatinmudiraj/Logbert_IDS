import os
import sys
import torch
import json
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.model import LogBERT
from core.dataset import LogSequenceDataset, DataLoader, collate_fn
from core.parser import LogParser

def evaluate_and_save(test_data_path=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    meta_path = os.path.join(project_root, 'models', 'parser_meta.json')
    model_path = os.path.join(project_root, 'models', 'logbert_model.pth')
    
    if test_data_path is None:
        test_data_path = os.path.join(project_root, 'data', 'processed', 'test_mixed.jsonl')
    
    if not os.path.exists(test_data_path):
        print(f"[!] Test data not found: {test_data_path}")
        return

    # Load metadata
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    template_to_id = meta['template_to_id']
    vocab_size = meta['vocab_size']
    dist_token = template_to_id.get('[DIST]', 0)
    
    # Load model
    model = LogBERT(vocab_size=vocab_size, d_model=256, nhead=8, num_layers=4)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        print(f"[*] Loaded model from {model_path}")
    else:
        print(f"[!] Model file not found: {model_path}")
        return
    model.eval()

    print(f"[*] Evaluating on {test_data_path}...")
    
    total_tp, total_fn, total_fp, total_tn = 0, 0, 0, 0
    output_lines = ["=== LogBERT IDS Final Evaluation Results ==="]

    with open(test_data_path, 'r') as f:
        for line in f:
            item = json.loads(line)
            # template_ids are already strings in build_dataset, convert to int for model
            seq_ids = [int(tid) for tid in item['sequence']]
            true_label = item['label']
            
            # Prepare sequence for model
            seq_tensor = torch.tensor([seq_ids])
            
            with torch.no_grad():
                logits, _ = model(seq_tensor)
                
                # For anomaly detection, we often check prediction loss or mismatches
                # Here we use a simple placeholder logic for baseline: 
                # if loss > threshold or mismatches > R
                # For now, let's just use the existing mismatch logic on the whole sequence
                # or a subset. Since it's a baseline, we'll try to predict each token.
                
                anomalies_found = 0
                for i in range(len(seq_ids)):
                    actual = seq_ids[i]
                    # Simulate masking this token
                    # In a real LogBERT evaluation, we'd mask and predict.
                    # Here we check if the model's top-k includes the actual token.
                    probs = torch.softmax(logits[0, i], dim=0)
                    _, top_indices = torch.topk(probs, k=5)
                    
                    if actual not in top_indices:
                        anomalies_found += 1
                
                # Threshold for sequence anomaly
                pred_label = 1 if anomalies_found > 2 else 0 # threshold R=2
                
                if true_label == 1:
                    if pred_label == 1: total_tp += 1
                    else: total_fn += 1
                else:
                    if pred_label == 1: total_fp += 1
                    else: total_tn += 1

    accuracy = (total_tp + total_tn) / (total_tp + total_tn + total_fp + total_fn) if (total_tp + total_tn + total_fp + total_fn) > 0 else 0
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    fpr = total_fp / (total_fp + total_tn) if (total_fp + total_tn) > 0 else 0
    fnr = total_fn / (total_fn + total_tp) if (total_fn + total_tp) > 0 else 0

    output_lines.append("\n=== Overall Metrics ===")
    output_lines.append(f"Overall Accuracy: {accuracy*100:.2f}%")
    output_lines.append(f"Precision: {precision*100:.2f}%")
    output_lines.append(f"Recall: {recall*100:.2f}%")
    output_lines.append(f"F1-Score: {f1*100:.2f}%")
    output_lines.append(f"False Positive Rate: {fpr*100:.2f}%")
    output_lines.append(f"False Negative Rate: {fnr*100:.2f}%")
    
    result_path = os.path.join(project_root, 'backup', 'result.txt')
    with open(result_path, 'w') as f:
        f.write("\n".join(output_lines) + "\n")
        
    # Save as JSON for baseline
    metrics = {
        "total_sequences": total_tp + total_tn + total_fp + total_fn,
        "anomalous_sequences": total_tp + total_fp,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "accuracy": accuracy
    }
    
    json_path = os.path.join(project_root, 'results', 'baseline_eval.json')
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Results saved to {result_path} and {json_path}")

if __name__ == '__main__':
    evaluate_and_save()

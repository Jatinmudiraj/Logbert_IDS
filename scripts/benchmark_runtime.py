import time
import torch
import os
import json
from core.detector_service import LogBERTDetectorService

def benchmark(iterations=100, window_size=20):
    print(f"[*] Starting Performance Benchmark ({iterations} iterations)...")
    
    service = LogBERTDetectorService()
    
    # Sample log sequence
    sample_logs = [
        "Apr 25 10:12:33 ubuntu sshd[1234]: Failed password for invalid user admin from 192.168.20.5 port 55321 ssh2"
    ] * window_size
    
    # 1. Measurement: Inference Latency
    start_time = time.time()
    for _ in range(iterations):
        _ = service.analyze_sequence(sample_logs)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_latency = (total_time / iterations) * 1000 # ms
    throughput = iterations / total_time # sequences/sec
    
    print("\n=== Runtime Benchmark Results ===")
    print(f"Average Inference Latency: {avg_latency:.2f} ms/sequence")
    print(f"Throughput: {throughput:.2f} sequences/sec")
    print(f"Device: {service.device}")
    
    # 2. Resource usage (rough estimate)
    if torch.cuda.is_available():
        memory_allocated = torch.cuda.memory_allocated() / (1024 * 1024) # MB
        print(f"GPU Memory Allocated: {memory_allocated:.2f} MB")
        
    # Save results
    results = {
        "avg_latency_ms": avg_latency,
        "throughput_seq_sec": throughput,
        "device": str(service.device),
        "iterations": iterations,
        "window_size": window_size
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/benchmark.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\n[+] Benchmark saved to results/benchmark.json")

if __name__ == "__main__":
    benchmark()

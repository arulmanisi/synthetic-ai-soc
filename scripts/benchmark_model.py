import sys
import os
import json
import requests

# Add project root to path to import simulator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulator.sim_generator import generate_event, inject_anomaly


def generate_test_dataset(n_normal=100, n_anomaly=50):
    """Generate a labeled test dataset."""
    test_data = []
    
    # Generate normal events
    for _ in range(n_normal):
        event = generate_event()
        # Remove any injected anomalies from the normal set
        if "exfiltration" not in event.get("action", ""):
            test_data.append({
                "event": event,
                "is_anomaly": False
            })
    
    # Generate anomalous events
    for _ in range(n_anomaly):
        event = generate_event()
        event = inject_anomaly(event)
        test_data.append({
            "event": event,
            "is_anomaly": True
        })
    
    return test_data


def benchmark_model():
    print("Generating test dataset...")
    test_data = generate_test_dataset(n_normal=100, n_anomaly=50)
    print(f"Generated {len(test_data)} test events")
    
    print("\nEvaluating model...")
    try:
        response = requests.post("http://localhost:8001/evaluate", json=test_data)
        if response.status_code == 200:
            metrics = response.json()
            
            print("\n" + "="*50)
            print("BENCHMARK RESULTS")
            print("="*50)
            print(f"Precision: {metrics['precision']:.3f}")
            print(f"Recall:    {metrics['recall']:.3f}")
            print(f"F1 Score:  {metrics['f1']:.3f}")
            if metrics['roc_auc'] is not None:
                print(f"ROC-AUC:   {metrics['roc_auc']:.3f}")
            
            print("\nConfusion Matrix:")
            cm = metrics['confusion_matrix']
            print(f"  True Negatives:  {cm['true_negatives']}")
            print(f"  False Positives: {cm['false_positives']}")
            print(f"  False Negatives: {cm['false_negatives']}")
            print(f"  True Positives:  {cm['true_positives']}")
            print("="*50)
        else:
            print(f"Evaluation failed: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to anomaly-service at http://localhost:8001")
        print("Make sure the service is running.")


if __name__ == "__main__":
    benchmark_model()

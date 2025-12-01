import json
import os
import sys
from collections import defaultdict
from typing import Dict, List

import requests

# Add project root to path to import simulator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulator.sim_generator import generate_event, inject_anomaly
from mitre.mapping import mitre_hints_for_action


def generate_test_dataset(n_normal=100, n_anomaly=50, model_name=None):
    """Generate a labeled test dataset."""
    test_data = []
    
    # Generate normal events
    for _ in range(n_normal):
        event = generate_event()
        # Remove any injected anomalies from the normal set
        if "exfiltration" not in event.get("action", ""):
            entry = {"event": event, "is_anomaly": False}
            if model_name:
                entry["model"] = model_name
            test_data.append(entry)
    
    # Generate anomalous events
    for _ in range(n_anomaly):
        event = generate_event()
        event = inject_anomaly(event)
        entry = {"event": event, "is_anomaly": True}
        if model_name:
            entry["model"] = model_name
        test_data.append(entry)
    
    return test_data


def per_technique_metrics(test_data: List[Dict], predictions: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Compute precision/recall per technique based on MITRE tags present in events."""
    buckets: Dict[str, Dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for item, pred in zip(test_data, predictions):
        event = item["event"]
        true_label = item["is_anomaly"]
        predicted_label = pred.get("is_anomaly", False)
        techniques = event.get("mitre_techniques") or mitre_hints_for_action(event.get("action", "")).get("techniques", [])
        if not techniques:
            continue
        for tech in techniques:
            if predicted_label and true_label:
                buckets[tech]["tp"] += 1
            elif predicted_label and not true_label:
                buckets[tech]["fp"] += 1
            elif (not predicted_label) and true_label:
                buckets[tech]["fn"] += 1

    metrics: Dict[str, Dict[str, float]] = {}
    for tech, counts in buckets.items():
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        metrics[tech] = {"precision": precision, "recall": recall}
    return metrics


def benchmark_model():
    print("Generating test dataset...")
    model_name = os.getenv("MODEL", "isolation-forest")
    test_data = generate_test_dataset(n_normal=100, n_anomaly=50, model_name=model_name)
    print(f"Generated {len(test_data)} test events")
    
    print("\nEvaluating model...")
    try:
        response = requests.post("http://localhost:8001/evaluate", json=test_data)
        if response.status_code == 200:
            metrics = response.json()
            predictions = metrics.get("predictions", [])
            
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

            if predictions:
                per_tech = per_technique_metrics(test_data, predictions)
                if per_tech:
                    print("\nPer-technique metrics:")
                    for tech, vals in per_tech.items():
                        print(f"  {tech}: precision={vals['precision']:.2f}, recall={vals['recall']:.2f}")
        else:
            print(f"Evaluation failed: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to anomaly-service at http://localhost:8001")
        print("Make sure the service is running.")


if __name__ == "__main__":
    benchmark_model()

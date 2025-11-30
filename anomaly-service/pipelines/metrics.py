from typing import Dict, List
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)


def calculate_metrics(
    y_true: List[int], y_pred: List[int], y_scores: List[float]
) -> Dict:
    """
    Calculate standard ML metrics for anomaly detection.
    
    Args:
        y_true: Ground truth labels (1 for anomaly, 0 for normal)
        y_pred: Predicted labels (1 for anomaly, 0 for normal)
        y_scores: Anomaly scores (continuous values)
    
    Returns:
        Dictionary with precision, recall, F1, ROC-AUC, and confusion matrix
    """
    metrics = {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    
    # ROC-AUC requires at least one positive and one negative sample
    if len(set(y_true)) > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_scores))
    else:
        metrics["roc_auc"] = None
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = {
        "true_negatives": int(cm[0, 0]) if cm.shape[0] > 0 else 0,
        "false_positives": int(cm[0, 1]) if cm.shape[0] > 1 else 0,
        "false_negatives": int(cm[1, 0]) if cm.shape[0] > 1 else 0,
        "true_positives": int(cm[1, 1]) if cm.shape[0] > 1 else 0,
    }
    
    return metrics

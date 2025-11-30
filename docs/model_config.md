# Model Configuration

## Default Model: Isolation Forest

The anomaly service now uses **Isolation Forest** as the default and primary model based on extensive benchmarking.

### Performance Summary
- **F1 Score**: 0.532
- **Recall**: 74%
- **Precision**: 41.6%
- **ROC-AUC**: 0.695

## Available Models

While Isolation Forest is the default, other models are available if needed:

| Model | Status | Performance | Use Case |
|-------|--------|-------------|----------|
| `isolation-forest` | ✅ Default | F1=0.532 | General anomaly detection |
| `lof` | 🟡 Available | F1=0.000 | Experimental/research |
| `one-class-svm` | 🟡 Available | F1=0.000 | Experimental/research |
| `ensemble` | 🟡 Available | F1=0.000 | Experimental/research |

## Using Alternative Models

### Via API
```bash
# Use LOF model
curl -X POST http://localhost:8001/score \
  -H "Content-Type: application/json" \
  -d '{
    "event": {"user": "alice", "action": "login"},
    "model": "lof"
  }'
```

### Via Environment Variable
```bash
export ANOMALY_DEFAULT_MODEL=lof
python -m uvicorn app:app
```

## Lazy Loading

For performance, only Isolation Forest is initialized at startup. Other models are loaded on-demand when first requested.

## Recommendation

**Stick with Isolation Forest** unless you have specific requirements for alternative models.

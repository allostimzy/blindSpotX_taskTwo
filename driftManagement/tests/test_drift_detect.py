import pytest
import numpy as np
from drift_detect import DriftDetector, DriftSeverity

@pytest.fixture
def drift_detector():
    return DriftDetector(tolerance=0.1)

def test_normalize_data(drift_detector):
    data = [1, 2, 3, 4, 5]
    normalized = drift_detector.normalize_data(data)
    assert len(normalized) == len(data)
    assert np.isclose(np.mean(normalized), 0, atol=1e-10)
    assert np.isclose(np.std(normalized), 1, atol=1e-10)

def test_calculate_drift_score_no_drift(drift_detector):
    baseline = [1, 2, 3, 4, 5]
    current = [1, 2, 3, 4, 5]
    score = drift_detector.calculate_drift_score(baseline, current)
    assert score == 0.0

def test_calculate_drift_score_with_drift(drift_detector):
    baseline = [1, 2, 3, 4, 5]
    current = [5, 4, 3, 2, 1]
    score = drift_detector.calculate_drift_score(baseline, current)
    assert score > 0

def test_determine_severity(drift_detector):
    assert drift_detector.determine_severity(0.9) == "CRITICAL"
    assert drift_detector.determine_severity(0.7) == "HIGH"
    assert drift_detector.determine_severity(0.5) == "MEDIUM"
    assert drift_detector.determine_severity(0.1) == "LOW"

def test_detect_drift(drift_detector):
    baseline = [1, 2, 3, 4, 5]
    current = [5, 4, 3, 2, 1]
    result = drift_detector.detect_drift(baseline, current)
    
    assert "timestamp" in result
    assert "drift_score" in result
    assert "severity" in result
    assert "baseline_size" in result
    assert "current_size" in result
    assert "tolerance" in result
    assert result["baseline_size"] == len(baseline)
    assert result["current_size"] == len(current)

def test_get_drift_summary(drift_detector):
    drift_results = [
        {"severity": "CRITICAL", "drift_score": 0.9},
        {"severity": "HIGH", "drift_score": 0.7},
        {"severity": "MEDIUM", "drift_score": 0.5},
        {"severity": "LOW", "drift_score": 0.1}
    ]
    
    summary = drift_detector.get_drift_summary(drift_results)
    
    assert summary["total_detections"] == 4
    assert summary["severity_distribution"]["CRITICAL"] == 1
    assert summary["severity_distribution"]["HIGH"] == 1
    assert summary["severity_distribution"]["MEDIUM"] == 1
    assert summary["severity_distribution"]["LOW"] == 1
    assert "average_drift_score" in summary
    assert "timestamp" in summary

def test_empty_data_handling(drift_detector):
    empty_result = drift_detector.detect_drift([], [])
    assert empty_result["drift_score"] == 0.0
    assert empty_result["severity"] == "LOW" 
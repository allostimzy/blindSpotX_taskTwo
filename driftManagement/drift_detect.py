import logging
import json
from datetime import datetime
from typing import Dict, Any, List
import numpy as np
from dataclasses import dataclass

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drift_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DriftSeverity:
    CRITICAL: float = 0.8
    HIGH: float = 0.6
    MEDIUM: float = 0.4
    LOW: float = 0.2

class DriftDetector:
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance
        self.severity_levels = DriftSeverity()
        logger.info("Initialized DriftDetector with tolerance: %f", tolerance)

    def normalize_data(self, data: List[float]) -> List[float]:
        """Normalize data to handle noisy inputs."""
        if not data:
            return []
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return [0] * len(data)
        return [(x - mean) / std for x in data]

    def calculate_drift_score(self, baseline: List[float], current: List[float]) -> float:
        """Calculate drift score with noise tolerance."""
        if not baseline or not current:
            return 0.0

        baseline_norm = self.normalize_data(baseline)
        current_norm = self.normalize_data(current)
        
        # Calculate KL divergence
        kl_div = np.sum(np.where(current_norm != 0, 
                                current_norm * np.log(current_norm / baseline_norm), 0))
        
        # Apply noise tolerance
        drift_score = max(0, kl_div - self.tolerance)
        logger.debug("Calculated drift score: %f", drift_score)
        return float(drift_score)

    def determine_severity(self, drift_score: float) -> str:
        """Determine severity level based on drift score."""
        if drift_score >= self.severity_levels.CRITICAL:
            return "CRITICAL"
        elif drift_score >= self.severity_levels.HIGH:
            return "HIGH"
        elif drift_score >= self.severity_levels.MEDIUM:
            return "MEDIUM"
        else:
            return "LOW"

    def detect_drift(self, baseline_data: List[float], current_data: List[float]) -> Dict[str, Any]:
        """Detect drift with severity ranking and structured logging."""
        try:
            drift_score = self.calculate_drift_score(baseline_data, current_data)
            severity = self.determine_severity(drift_score)
            
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "drift_score": drift_score,
                "severity": severity,
                "baseline_size": len(baseline_data),
                "current_size": len(current_data),
                "tolerance": self.tolerance
            }
            
            logger.info("Drift detection completed", extra=result)
            return result
            
        except Exception as e:
            logger.error("Error in drift detection: %s", str(e), exc_info=True)
            raise

    def get_drift_summary(self, drift_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of drift detection results."""
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        total_drift_score = 0
        
        for result in drift_results:
            severity_counts[result["severity"]] += 1
            total_drift_score += result["drift_score"]
        
        summary = {
            "total_detections": len(drift_results),
            "severity_distribution": severity_counts,
            "average_drift_score": total_drift_score / len(drift_results) if drift_results else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("Generated drift summary", extra=summary)
        return summary

if __name__ == "__main__":
    detect_drift()

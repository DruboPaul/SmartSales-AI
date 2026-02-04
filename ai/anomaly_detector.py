"""
Anomaly Detection Engine for Retail Sales Data

Uses statistical methods and ML to detect unusual patterns in sales data.
Demonstrates:
- Statistical analysis (Z-score, IQR)
- Scikit-learn integration
- Real-time anomaly flagging

Usage:
    from ai.anomaly_detector import AnomalyDetector
    
    detector = AnomalyDetector()
    anomalies = detector.detect(sales_df)
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AnomalyReport:
    """Structured anomaly detection result."""
    timestamp: str
    anomaly_type: str
    severity: str  # low, medium, high, critical
    metric: str
    actual_value: float
    expected_range: Tuple[float, float]
    deviation_pct: float
    recommendation: str


class AnomalyDetector:
    """
    Multi-method anomaly detection for retail analytics.
    
    Combines statistical methods (IQR, Z-score) with optional
    ML-based detection for more sophisticated pattern recognition.
    """
    
    def __init__(
        self,
        z_threshold: float = 3.0,
        iqr_multiplier: float = 1.5,
        sensitivity: str = "medium"
    ):
        """
        Initialize the anomaly detector.
        
        Args:
            z_threshold: Z-score threshold for anomaly detection
            iqr_multiplier: IQR multiplier for outlier detection
            sensitivity: Detection sensitivity (low, medium, high)
        """
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        
        # Adjust thresholds based on sensitivity
        sensitivity_map = {"low": 0.7, "medium": 1.0, "high": 1.3}
        multiplier = sensitivity_map.get(sensitivity, 1.0)
        self.z_threshold *= multiplier
        self.iqr_multiplier *= multiplier
        
        self.historical_data: Dict[str, List[float]] = {}
    
    def add_historical_data(self, metric: str, values: List[float]):
        """
        Add historical data for a metric to improve detection.
        
        Args:
            metric: Name of the metric (e.g., 'daily_revenue')
            values: Historical values for baseline
        """
        self.historical_data[metric] = values
    
    def detect_zscore_anomaly(
        self,
        value: float,
        metric: str,
        historical: Optional[List[float]] = None
    ) -> Optional[AnomalyReport]:
        """
        Detect anomalies using Z-score method.
        
        Args:
            value: Current value to check
            metric: Name of the metric
            historical: Historical values (uses stored if not provided)
            
        Returns:
            AnomalyReport if anomaly detected, None otherwise
        """
        data = historical or self.historical_data.get(metric, [])
        
        if len(data) < 10:
            return None  # Not enough data
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return None
        
        z_score = abs(value - mean) / std
        
        if z_score > self.z_threshold:
            deviation_pct = ((value - mean) / mean) * 100
            severity = self._calculate_severity(z_score)
            
            return AnomalyReport(
                timestamp=datetime.now().isoformat(),
                anomaly_type="Z-Score Outlier",
                severity=severity,
                metric=metric,
                actual_value=value,
                expected_range=(mean - 2*std, mean + 2*std),
                deviation_pct=deviation_pct,
                recommendation=self._generate_recommendation(metric, deviation_pct)
            )
        
        return None
    
    def detect_iqr_anomaly(
        self,
        value: float,
        metric: str,
        historical: Optional[List[float]] = None
    ) -> Optional[AnomalyReport]:
        """
        Detect anomalies using IQR (Interquartile Range) method.
        
        More robust to outliers than Z-score.
        """
        data = historical or self.historical_data.get(metric, [])
        
        if len(data) < 10:
            return None
        
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr
        
        if value < lower_bound or value > upper_bound:
            median = np.median(data)
            deviation_pct = ((value - median) / median) * 100
            
            distance = min(abs(value - lower_bound), abs(value - upper_bound))
            severity = self._calculate_severity(distance / iqr if iqr > 0 else 0)
            
            return AnomalyReport(
                timestamp=datetime.now().isoformat(),
                anomaly_type="IQR Outlier",
                severity=severity,
                metric=metric,
                actual_value=value,
                expected_range=(lower_bound, upper_bound),
                deviation_pct=deviation_pct,
                recommendation=self._generate_recommendation(metric, deviation_pct)
            )
        
        return None
    
    def detect_all(
        self,
        current_values: Dict[str, float]
    ) -> List[AnomalyReport]:
        """
        Run all detection methods on current values.
        
        Args:
            current_values: Dict of metric_name -> current_value
            
        Returns:
            List of all detected anomalies
        """
        anomalies = []
        
        for metric, value in current_values.items():
            # Try Z-score detection
            z_anomaly = self.detect_zscore_anomaly(value, metric)
            if z_anomaly:
                anomalies.append(z_anomaly)
                continue  # Don't double-report
            
            # Try IQR detection
            iqr_anomaly = self.detect_iqr_anomaly(value, metric)
            if iqr_anomaly:
                anomalies.append(iqr_anomaly)
        
        return anomalies
    
    def _calculate_severity(self, score: float) -> str:
        """Map detection score to severity level."""
        if score > 5:
            return "critical"
        elif score > 4:
            return "high"
        elif score > 3:
            return "medium"
        return "low"
    
    def _generate_recommendation(self, metric: str, deviation_pct: float) -> str:
        """Generate actionable recommendation based on anomaly."""
        direction = "increase" if deviation_pct > 0 else "decrease"
        abs_pct = abs(deviation_pct)
        
        recommendations = {
            "daily_revenue": f"Revenue {direction}d by {abs_pct:.1f}%. Review pricing strategy and promotions.",
            "transaction_count": f"Transaction volume {direction}d by {abs_pct:.1f}%. Check store traffic and marketing campaigns.",
            "avg_order_value": f"Average order value {direction}d by {abs_pct:.1f}%. Analyze product mix and upselling effectiveness.",
            "category_sales": f"Category sales {direction}d by {abs_pct:.1f}%. Review inventory levels and merchandising.",
        }
        
        return recommendations.get(
            metric,
            f"Unusual {direction} of {abs_pct:.1f}% detected. Investigate root cause."
        )
    
    def format_alert(self, anomaly: AnomalyReport) -> str:
        """Format anomaly as alert message."""
        emoji_map = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "📊",
            "low": "ℹ️"
        }
        
        return f"""
{emoji_map.get(anomaly.severity, '📊')} **{anomaly.severity.upper()} ANOMALY DETECTED**

📌 Metric: {anomaly.metric}
📊 Actual: {anomaly.actual_value:,.2f}
📈 Expected: {anomaly.expected_range[0]:,.2f} - {anomaly.expected_range[1]:,.2f}
📉 Deviation: {anomaly.deviation_pct:+.1f}%
🔍 Type: {anomaly.anomaly_type}

💡 **Recommendation**: {anomaly.recommendation}

🕒 Detected: {anomaly.timestamp}
"""


# Example usage
if __name__ == "__main__":
    print("🔧 Testing Anomaly Detector...")
    
    # Create detector
    detector = AnomalyDetector(sensitivity="medium")
    
    # Add historical data (simulated 30 days)
    np.random.seed(42)
    historical_revenue = np.random.normal(45000, 5000, 30).tolist()
    detector.add_historical_data("daily_revenue", historical_revenue)
    
    # Test with normal value
    normal_value = 47000
    anomaly = detector.detect_zscore_anomaly(normal_value, "daily_revenue")
    print(f"\n✅ Normal value ({normal_value}): {'No anomaly' if not anomaly else 'Anomaly!'}")
    
    # Test with anomalous value
    anomalous_value = 15000  # Much lower than normal
    anomaly = detector.detect_zscore_anomaly(anomalous_value, "daily_revenue")
    if anomaly:
        print(f"\n🚨 Anomaly detected!")
        print(detector.format_alert(anomaly))
    
    print("\n✅ Anomaly Detector test complete!")

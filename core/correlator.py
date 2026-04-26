import time
from collections import defaultdict

class AlertCorrelator:
    def __init__(self, time_window=300):
        self.time_window = time_window # 5 minutes
        self.incidents = defaultdict(list)

    def correlate(self, anomaly_result):
        """
        Groups anomalies into incidents based on source host and time window.
        """
        host = anomaly_result.get("host", "localhost")
        current_time = time.time()
        
        # Simple correlation: same host within same time window
        incident_id = f"INC-{host}-{int(current_time // self.time_window)}"
        
        self.incidents[incident_id].append({
            "timestamp": current_time,
            "result": anomaly_result
        })
        
        # Cleanup old incidents
        self._cleanup(current_time)
        
        return {
            "incident_id": incident_id,
            "incident_size": len(self.incidents[incident_id]),
            "is_multi_stage": len(self.incidents[incident_id]) > 3
        }

    def _cleanup(self, current_time):
        to_delete = []
        for inc_id, alerts in self.incidents.items():
            if current_time - alerts[-1]["timestamp"] > self.time_window * 2:
                to_delete.append(inc_id)
        
        for inc_id in to_delete:
            del self.incidents[inc_id]

if __name__ == "__main__":
    correlator = AlertCorrelator()
    res = {"host": "UB2", "score": 0.9}
    print(correlator.correlate(res))
    print(correlator.correlate(res))

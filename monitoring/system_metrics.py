# monitoring/system_metrics.py
import time
import psutil
import threading
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class SystemMetricsCollector:
    """
    Collects system-level metrics: CPU, memory, disk, and API request stats.
    Runs a background thread to sample system metrics periodically.
    """
    
    def __init__(self, storage_dir: str = "monitoring/data", 
                 sample_interval_sec: int = 60):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.sample_interval = sample_interval_sec
        self.system_metrics_file = self.storage_dir / "system_metrics.csv"
        self.api_metrics_file = self.storage_dir / "api_metrics.csv"
        
        # For API metrics
        self.request_times = deque(maxlen=1000)  # last 1000 request durations (seconds)
        self.request_counts = 0
        self.error_counts = 0
        self.lock = threading.Lock()
        
        # Start background sampling
        self._stop_event = threading.Event()
        self._sampler_thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._sampler_thread.start()
    
    def _sample_loop(self):
        """Background thread to collect system metrics periodically."""
        while not self._stop_event.is_set():
            self._collect_system_metrics()
            time.sleep(self.sample_interval)
    
    def _collect_system_metrics(self):
        """Sample CPU, memory, disk."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "load_avg": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
        }
        # Append to CSV
        import pandas as pd
        df_new = pd.DataFrame([record])
        if self.system_metrics_file.exists():
            df_existing = pd.read_csv(self.system_metrics_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        df_combined.to_csv(self.system_metrics_file, index=False)
    
    def record_request(self, duration_seconds: float, is_error: bool = False):
        """Call this for each API request (e.g., in middleware)."""
        with self.lock:
            self.request_times.append(duration_seconds)
            self.request_counts += 1
            if is_error:
                self.error_counts += 1
    
    def get_api_metrics(self) -> Dict:
        """Return aggregated API metrics."""
        with self.lock:
            total_requests = self.request_counts
            error_count = self.error_counts
            error_rate = error_count / total_requests if total_requests > 0 else 0
            avg_latency = sum(self.request_times) / len(self.request_times) if self.request_times else 0
            p95_latency = sorted(self.request_times)[int(0.95 * len(self.request_times))] if self.request_times else 0
            throughput = total_requests / (self.sample_interval * (self.request_counts / max(1, len(self.request_times))))  # rough
            return {
                "total_requests": total_requests,
                "error_count": error_count,
                "error_rate": error_rate,
                "avg_latency_sec": avg_latency,
                "p95_latency_sec": p95_latency,
                "throughput_rps": throughput
            }
    
    def get_system_health(self) -> Dict:
        """Get latest system metrics."""
        if not self.system_metrics_file.exists():
            return {"status": "no_data"}
        import pandas as pd
        df = pd.read_csv(self.system_metrics_file)
        latest = df.iloc[-1].to_dict()
        return {
            "status": "healthy" if latest.get('cpu_percent', 0) < 80 else "high_cpu",
            "cpu_percent": latest.get('cpu_percent'),
            "memory_percent": latest.get('memory_percent'),
            "disk_usage_percent": latest.get('disk_usage_percent'),
            "timestamp": latest.get('timestamp')
        }
    
    def stop(self):
        self._stop_event.set()
        self._sampler_thread.join(timeout=2)


# FastAPI middleware integration example (you can place this in api/middleware/logging.py)
from fastapi import Request
import time

async def system_metrics_middleware(request: Request, call_next):
    collector = get_system_collector()
    start = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start
        collector.record_request(duration, is_error=(response.status_code >= 500))
        return response
    except Exception as e:
        duration = time.time() - start
        collector.record_request(duration, is_error=True)
        raise e

_system_collector = None

def get_system_collector() -> SystemMetricsCollector:
    global _system_collector
    if _system_collector is None:
        _system_collector = SystemMetricsCollector()
    return _system_collector
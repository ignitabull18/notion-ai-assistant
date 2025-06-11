"""
Production monitoring, metrics, and health checks
"""
import time
import asyncio
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import logging
from enum import Enum


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: Optional[float] = None
    last_checked: Optional[datetime] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collect and store application metrics"""
    
    def __init__(self, max_points_per_metric: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points_per_metric))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def increment(self, metric_name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric"""
        with self._lock:
            key = self._make_key(metric_name, tags)
            self.counters[key] += value
            self._add_point(metric_name, self.counters[key], tags)
    
    def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric"""
        with self._lock:
            key = self._make_key(metric_name, tags)
            self.gauges[key] = value
            self._add_point(metric_name, value, tags)
    
    def timing(self, metric_name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timing metric"""
        with self._lock:
            key = self._make_key(metric_name, tags)
            self.timers[key].append(duration_ms)
            
            # Keep only last 100 timings to prevent memory issues
            if len(self.timers[key]) > 100:
                self.timers[key] = self.timers[key][-100:]
            
            self._add_point(metric_name, duration_ms, tags)
    
    def timer(self, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations"""
        return TimingContext(self, metric_name, tags)
    
    def _make_key(self, metric_name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create unique key for metric with tags"""
        if not tags:
            return metric_name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric_name}[{tag_str}]"
    
    def _add_point(self, metric_name: str, value: float, tags: Optional[Dict[str, str]]) -> None:
        """Add a metric point to history"""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {}
        )
        self.metrics[metric_name].append(point)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        with self._lock:
            summary = {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "timers": {}
            }
            
            # Calculate timer statistics
            for key, values in self.timers.items():
                if values:
                    summary["timers"][key] = {
                        "count": len(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": self._percentile(values, 95),
                        "p99": self._percentile(values, 99)
                    }
            
            return summary
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]


class TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, tags: Optional[Dict[str, str]]):
        self.collector = collector
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.timing(self.metric_name, duration_ms, self.tags)


class HealthMonitor:
    """Monitor application health"""
    
    def __init__(self, check_interval: int = 30):
        self.checks: Dict[str, Callable[[], HealthCheck]] = {}
        self.last_results: Dict[str, HealthCheck] = {}
        self.check_interval = check_interval
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__)
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheck]) -> None:
        """Register a health check function"""
        self.checks[name] = check_func
        self.logger.info(f"Registered health check: {name}")
    
    async def start_monitoring(self) -> None:
        """Start background health monitoring"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self.running:
            try:
                await self.run_all_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                result = await asyncio.get_event_loop().run_in_executor(None, check_func)
                result.response_time_ms = (time.time() - start_time) * 1000
                result.last_checked = datetime.utcnow()
                results[name] = result
                self.last_results[name] = result
            except Exception as e:
                self.logger.error(f"Health check '{name}' failed: {e}", exc_info=True)
                results[name] = HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    last_checked=datetime.utcnow()
                )
                self.last_results[name] = results[name]
        
        return results
    
    def get_overall_health(self) -> HealthCheck:
        """Get overall application health"""
        if not self.last_results:
            return HealthCheck(
                name="overall",
                status=HealthStatus.UNHEALTHY,
                message="No health checks have been run"
            )
        
        statuses = [check.status for check in self.last_results.values()]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
            message = "All systems healthy"
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            overall_status = HealthStatus.UNHEALTHY
            unhealthy_checks = [
                name for name, check in self.last_results.items()
                if check.status == HealthStatus.UNHEALTHY
            ]
            message = f"Unhealthy systems: {', '.join(unhealthy_checks)}"
        else:
            overall_status = HealthStatus.DEGRADED
            degraded_checks = [
                name for name, check in self.last_results.items()
                if check.status == HealthStatus.DEGRADED
            ]
            message = f"Degraded systems: {', '.join(degraded_checks)}"
        
        return HealthCheck(
            name="overall",
            status=overall_status,
            message=message,
            last_checked=datetime.utcnow(),
            details={"individual_checks": len(self.last_results)}
        )


# Global instances
metrics = MetricsCollector()
health_monitor = HealthMonitor()


# Common health check functions
def create_database_health_check(db_connection_func: Callable) -> Callable[[], HealthCheck]:
    """Create a database health check"""
    def check() -> HealthCheck:
        try:
            start_time = time.time()
            db_connection_func()  # Test database connection
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                response_time_ms=response_time
            )
        except Exception as e:
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}"
            )
    
    return check


def create_api_health_check(api_name: str, test_func: Callable) -> Callable[[], HealthCheck]:
    """Create an API health check"""
    def check() -> HealthCheck:
        try:
            start_time = time.time()
            test_func()  # Test API connection
            response_time = (time.time() - start_time) * 1000
            
            if response_time > 5000:  # 5 seconds
                status = HealthStatus.DEGRADED
                message = f"{api_name} API responding slowly ({response_time:.0f}ms)"
            else:
                status = HealthStatus.HEALTHY
                message = f"{api_name} API healthy"
            
            return HealthCheck(
                name=f"{api_name.lower()}_api",
                status=status,
                message=message,
                response_time_ms=response_time
            )
        except Exception as e:
            return HealthCheck(
                name=f"{api_name.lower()}_api",
                status=HealthStatus.UNHEALTHY,
                message=f"{api_name} API failed: {str(e)}"
            )
    
    return check
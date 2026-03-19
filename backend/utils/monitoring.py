"""
Performance monitoring and metrics collection for the Universal Query Dashboard.
Tracks system performance, agent efficiency, and user interaction patterns.
"""

import time
import threading
import psutil
import sqlite3
from typing import Dict, List, Any, Optional, DefaultDict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import os

@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""
    query_id: str
    session_id: str
    question: str
    table_name: str
    is_csv: bool
    agent_steps: int
    execution_time_ms: float
    result_count: int
    success: bool
    error_type: Optional[str]
    timestamp: datetime
    memory_usage_mb: float
    cpu_usage_percent: float

@dataclass
class SystemMetrics:
    """System-level performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    active_connections: int
    queries_per_minute: float

class MetricsCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self.query_history = deque(maxlen=1000)  # Keep last 1000 queries
        self.system_history = deque(maxlen=1000)  # Keep last 1000 system snapshots
        self._init_database()
        
        # Performance tracking
        # Performance tracking
        self._active_queries: Dict[str, Dict[str, Any]] = {}
        self._query_count_1min: deque = deque(maxlen=60)  # 1 minute window
        self._monitoring_active: bool = False
        self._monitor_thread: Optional[threading.Thread] = None
        
    def _init_database(self):
        """Initialize the metrics database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id TEXT,
                    session_id TEXT,
                    question TEXT,
                    table_name TEXT,
                    is_csv BOOLEAN,
                    agent_steps INTEGER,
                    execution_time_ms REAL,
                    result_count INTEGER,
                    success BOOLEAN,
                    error_type TEXT,
                    timestamp DATETIME,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used_mb REAL,
                    memory_total_mb REAL,
                    disk_usage_percent REAL,
                    active_connections INTEGER,
                    queries_per_minute REAL
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_timestamp ON query_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)")
            conn.commit()
    
    def start_monitoring(self, interval: int = 30):
        """Start background system monitoring."""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self._monitor_thread = thread
        thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self._monitoring_active = False
        thread = self._monitor_thread
        if thread:
            thread.join(timeout=5)
    
    def _monitor_loop(self, interval: int):
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self.record_system_metrics(metrics)
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        # Active connections (approximation)
        active_connections = len(psutil.net_connections())
        
        # Queries per minute
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        recent_queries = [q for q in self.query_history if q.timestamp > one_minute_ago]
        queries_per_minute = len(recent_queries)
        
        return SystemMetrics(
            timestamp=now,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_total_mb=memory_total_mb,
            disk_usage_percent=disk_usage_percent,
            active_connections=active_connections,
            queries_per_minute=queries_per_minute
        )
    
    def record_query_start(self, query_id: str, session_id: str, question: str, table_name: str, is_csv: bool):
        """Record the start of a query."""
        self._active_queries[query_id] = {
            'start_time': time.time(),
            'session_id': session_id,
            'question': question,
            'table_name': table_name,
            'is_csv': is_csv,
            'start_memory': psutil.Process().memory_info().rss / (1024 * 1024),
            'start_cpu': psutil.Process().cpu_percent()
        }
        
        # Track query count for rate limiting
        self._query_count_1min.append(time.time())
    
    def record_query_end(self, query_id: str, agent_steps: int, result_count: int, success: bool, error_type: Optional[str] = None):
        """Record the completion of a query."""
        if query_id not in self._active_queries:
            return
            
        query_data = self._active_queries.pop(query_id)
        execution_time = (time.time() - float(query_data['start_time'])) * 1000
        memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)
        cpu_usage = psutil.Process().cpu_percent()
        
        metrics = QueryMetrics(
            query_id=query_id,
            session_id=str(query_data['session_id']),
            question=str(query_data['question']),
            table_name=str(query_data['table_name']),
            is_csv=bool(query_data['is_csv']),
            agent_steps=agent_steps,
            execution_time_ms=execution_time,
            result_count=result_count,
            success=success,
            error_type=error_type,
            timestamp=datetime.now(),
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
        
        self.record_query_metrics(metrics)
    
    def record_query_metrics(self, metrics: QueryMetrics):
        """Record query metrics to database and in-memory history."""
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO query_metrics 
                (query_id, session_id, question, table_name, is_csv, agent_steps, 
                 execution_time_ms, result_count, success, error_type, timestamp, 
                 memory_usage_mb, cpu_usage_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.query_id, metrics.session_id, metrics.question, 
                metrics.table_name, metrics.is_csv, metrics.agent_steps,
                metrics.execution_time_ms, metrics.result_count, metrics.success,
                metrics.error_type, metrics.timestamp, metrics.memory_usage_mb,
                metrics.cpu_usage_percent
            ))
            conn.commit()
        
        # Store in memory
        self.query_history.append(metrics)
    
    def record_system_metrics(self, metrics: SystemMetrics):
        """Record system metrics to database and in-memory history."""
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, memory_used_mb, 
                 memory_total_mb, disk_usage_percent, active_connections, queries_per_minute)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp, metrics.cpu_percent, metrics.memory_percent,
                metrics.memory_used_mb, metrics.memory_total_mb, metrics.disk_usage_percent,
                metrics.active_connections, metrics.queries_per_minute
            ))
            conn.commit()
        
        # Store in memory
        self.system_history.append(metrics)
    
    def get_query_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get query performance statistics."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_queries = [q for q in self.query_history if q.timestamp > cutoff]
        
        if not recent_queries:
            return {
                "total_queries": 0,
                "success_rate": 0,
                "avg_execution_time": 0,
                "avg_agent_steps": 0,
                "avg_result_count": 0,
                "error_breakdown": {},
                "performance_by_table": {}
            }
        
        total_queries = len(recent_queries)
        successful_queries = [q for q in recent_queries if q.success]
        failed_queries = [q for q in recent_queries if not q.success]
        
        success_rate = (len(successful_queries) / total_queries) * 100
        
        avg_execution_time = sum(q.execution_time_ms for q in successful_queries) / len(successful_queries) if successful_queries else 0
        avg_agent_steps = sum(q.agent_steps for q in successful_queries) / len(successful_queries) if successful_queries else 0
        avg_result_count = sum(q.result_count for q in successful_queries) / len(successful_queries) if successful_queries else 0
        
        # Error breakdown
        error_breakdown: Dict[str, int] = {}
        for q in failed_queries:
            error_type = q.error_type or "Unknown"
            error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1
        
        # Performance by table
        performance_by_table: Dict[str, List[float]] = {}
        for q in successful_queries:
            table = q.table_name or "CSV"
            if table not in performance_by_table:
                performance_by_table[table] = []
            performance_by_table[table].append(q.execution_time_ms)
        
        table_stats = {}
        for table, times in performance_by_table.items():
            table_stats[table] = {
                "query_count": len(times),
                "avg_execution_time": sum(times) / len(times),
                "min_execution_time": min(times),
                "max_execution_time": max(times)
            }
        
        return {
            "total_queries": total_queries,
            "success_rate": float(f"{success_rate:.2f}"),
            "avg_execution_time": float(f"{avg_execution_time:.2f}"),
            "avg_agent_steps": float(f"{avg_agent_steps:.2f}"),
            "avg_result_count": float(f"{avg_result_count:.2f}"),
            "error_breakdown": error_breakdown,
            "performance_by_table": table_stats
        }
    
    def get_system_stats(self, hours: int = 1) -> Dict[str, Any]:
        """Get system performance statistics."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.system_history if m.timestamp > cutoff]
        
        if not recent_metrics:
            return {
                "avg_cpu": 0,
                "avg_memory": 0,
                "avg_disk": 0,
                "max_active_connections": 0,
                "avg_queries_per_minute": 0,
                "current_load": {}
            }
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics)
        max_connections = max(m.active_connections for m in recent_metrics)
        avg_qpm = sum(m.queries_per_minute for m in recent_metrics) / len(recent_metrics)
        
        # Current system load
        current = self._collect_system_metrics()
        
        return {
            "avg_cpu": float(f"{avg_cpu:.2f}"),
            "avg_memory": float(f"{avg_memory:.2f}"),
            "avg_disk": float(f"{avg_disk:.2f}"),
            "max_active_connections": max_connections,
            "avg_queries_per_minute": float(f"{avg_qpm:.2f}"),
            "current_load": {
                "cpu": float(f"{current.cpu_percent:.2f}"),
                "memory": float(f"{current.memory_percent:.2f}"),
                "memory_used_mb": float(f"{current.memory_used_mb:.2f}"),
                "disk": float(f"{current.disk_usage_percent:.2f}"),
                "active_connections": current.active_connections,
                "queries_per_minute": float(current.queries_per_minute)
            }
        }
    
    def get_agent_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get agent-specific performance metrics."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_queries = [q for q in self.query_history if q.timestamp > cutoff]
        
        if not recent_queries:
            return {
                "avg_steps_per_query": 0,
                "steps_distribution": {},
                "performance_by_steps": {},
                "efficiency_trends": []
            }
        
        # Steps distribution
        steps_counts: Dict[int, int] = {}
        for q in recent_queries:
            steps_counts[q.agent_steps] = steps_counts.get(q.agent_steps, 0) + 1
        
        avg_steps = sum(q.agent_steps for q in recent_queries) / len(recent_queries)
        
        # Performance by steps
        performance_by_steps: Dict[int, List[float]] = {}
        for q in recent_queries:
            if q.success:
                if q.agent_steps not in performance_by_steps:
                    performance_by_steps[q.agent_steps] = []
                performance_by_steps[q.agent_steps].append(q.execution_time_ms)
        
        steps_performance = {}
        for steps, times in performance_by_steps.items():
            steps_performance[steps] = {
                "query_count": len(times),
                "avg_execution_time": sum(times) / len(times),
                "success_rate": len([q for q in recent_queries if q.agent_steps == steps and q.success]) / len([q for q in recent_queries if q.agent_steps == steps]) * 100
            }
        
        # Efficiency trends (queries per hour by steps)
        hourly_trends: Dict[int, Dict[int, int]] = {}
        for q in recent_queries:
            hour = q.timestamp.hour
            if hour not in hourly_trends:
                hourly_trends[hour] = {}
            hourly_trends[hour][q.agent_steps] = hourly_trends[hour].get(q.agent_steps, 0) + 1
        
        efficiency_trends = []
        for hour in sorted(hourly_trends.keys()):
            total_hourly = sum(hourly_trends[hour].values())
            avg_steps_hourly = sum(steps * count for steps, count in hourly_trends[hour].items()) / total_hourly
            efficiency_trends.append({
                "hour": hour,
                "total_queries": total_hourly,
                "avg_steps": float(f"{avg_steps_hourly:.2f}"),
                "step_breakdown": hourly_trends[hour]
            })
        
        return {
            "avg_steps_per_query": float(f"{avg_steps:.2f}"),
            "steps_distribution": steps_counts,
            "performance_by_steps": steps_performance,
            "efficiency_trends": efficiency_trends
        }
    
    def get_health_check(self) -> Dict[str, Any]:
        """Get overall system health status."""
        system_stats = self.get_system_stats(hours=1)
        query_stats = self.get_query_stats(hours=1)
        
        # Determine health status
        cpu_health = "healthy" if system_stats["current_load"]["cpu"] < 80 else "warning" if system_stats["current_load"]["cpu"] < 95 else "critical"
        memory_health = "healthy" if system_stats["current_load"]["memory"] < 85 else "warning" if system_stats["current_load"]["memory"] < 95 else "critical"
        disk_health = "healthy" if system_stats["current_load"]["disk"] < 90 else "warning" if system_stats["current_load"]["disk"] < 95 else "critical"
        query_health = "healthy" if query_stats["success_rate"] > 95 else "warning" if query_stats["success_rate"] > 85 else "critical"
        
        overall_health = "healthy"
        if "critical" in [cpu_health, memory_health, disk_health, query_health]:
            overall_health = "critical"
        elif "warning" in [cpu_health, memory_health, disk_health, query_health]:
            overall_health = "warning"
        
        return {
            "status": overall_health,
            "timestamp": datetime.now().isoformat(),
            "system_health": {
                "cpu": cpu_health,
                "memory": memory_health,
                "disk": disk_health,
                "queries": query_health
            },
            "metrics": {
                "system": system_stats,
                "queries": query_stats
            },
            "recommendations": self._generate_recommendations(system_stats, query_stats)
        }
    
    def _generate_recommendations(self, system_stats: Dict, query_stats: Dict) -> List[str]:
        """Generate performance recommendations based on current metrics."""
        recommendations = []
        
        if system_stats["current_load"]["cpu"] > 80:
            recommendations.append("High CPU usage detected. Consider scaling resources or optimizing queries.")
        
        if system_stats["current_load"]["memory"] > 85:
            recommendations.append("High memory usage detected. Monitor for memory leaks or increase available memory.")
        
        if system_stats["current_load"]["disk"] > 90:
            recommendations.append("High disk usage detected. Clean up old logs or increase disk space.")
        
        if query_stats["success_rate"] < 95:
            recommendations.append("Query success rate is below 95%. Review error logs and improve input validation.")
        
        if query_stats["avg_execution_time"] > 5000:  # 5 seconds
            recommendations.append("Average query execution time is high. Consider query optimization or caching.")
        
        if not recommendations:
            recommendations.append("System is running optimally.")
        
        return recommendations

# Global metrics collector instance
metrics_collector = MetricsCollector()

# Convenience functions for easy integration
def start_monitoring(interval: int = 30):
    """Start background performance monitoring."""
    metrics_collector.start_monitoring(interval)

def stop_monitoring():
    """Stop background monitoring."""
    metrics_collector.stop_monitoring()

def record_query_start(query_id: str, session_id: str, question: str, table_name: str, is_csv: bool):
    """Record query start for performance tracking."""
    metrics_collector.record_query_start(query_id, session_id, question, table_name, is_csv)

def record_query_end(query_id: str, agent_steps: int, result_count: int, success: bool, error_type: Optional[str] = None):
    """Record query completion for performance tracking."""
    metrics_collector.record_query_end(query_id, agent_steps, result_count, success, error_type)

def get_health_status() -> Dict[str, Any]:
    """Get current system health status."""
    return metrics_collector.get_health_check()

def get_performance_stats(hours: int = 24) -> Dict[str, Any]:
    """Get comprehensive performance statistics."""
    return {
        "query_stats": metrics_collector.get_query_stats(hours),
        "system_stats": metrics_collector.get_system_stats(hours),
        "agent_performance": metrics_collector.get_agent_performance(hours),
        "health": metrics_collector.get_health_check()
    }
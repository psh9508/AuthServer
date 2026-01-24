"""
Prometheus metrics for server observability
"""
from prometheus_client import Counter, Histogram

# ==========================================
# 1. Login Counter
# ==========================================
login_counter = Counter(
    'server_login_total',
    'Tracks the number of login attempts with their status and failure reason',
    ['status', 'reason']
)


# ==========================================
# 2. Login Duration Histogram
# ==========================================
login_duration = Histogram(
    'server_login_duration_seconds',
    'Measures the duration of login operations (success/failure)',
    ['status'],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)


# ==========================================
# 3. Helper Functions
# ==========================================
def record_login_success():
    """Record a successful login"""
    login_counter.labels(status='success', reason='').inc()


def record_login_failure(reason: str):
    """Record a failed login with specific reason"""
    login_counter.labels(status='failure', reason=reason).inc()
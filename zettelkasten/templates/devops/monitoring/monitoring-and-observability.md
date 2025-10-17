# Monitoring and Observability

Monitoring and observability help you understand system behavior and quickly identify issues.

## Three Pillars of Observability

### 1. Metrics
Numerical measurements over time.

```yaml
# Prometheus metrics example
http_requests_total{method="GET", status="200"} 1234
response_time_seconds{endpoint="/api/users"} 0.145
cpu_usage_percent{instance="web-1"} 65.2
```

- [definition] Metrics: Time-series numerical data
- [example] CPU usage, request rate, error rate, response time
- [tool] Prometheus: Industry-standard metrics collection

### 2. Logs
Discrete events with timestamps and details.

```json
{
  "timestamp": "2025-10-16T10:30:00Z",
  "level": "ERROR",
  "service": "api",
  "message": "Database connection failed",
  "error": "connection timeout",
  "request_id": "abc123"
}
```

- [definition] Logs: Timestamped event records
- [benefit] Detailed context for debugging
- [tool] ELK Stack (Elasticsearch, Logstash, Kibana)

### 3. Traces
End-to-end request flows through distributed systems.

```
Request ID: abc123
├─ API Gateway (10ms)
├─ Auth Service (50ms)
├─ User Service (120ms)
│  ├─ Database Query (80ms)
│  └─ Cache Hit (2ms)
└─ Response (5ms)
Total: 185ms
```

- [definition] Tracing: Request path through microservices
- [benefit] Identify bottlenecks in distributed systems
- [tool] Jaeger, Zipkin for distributed tracing

## Monitoring Stack

### Prometheus + Grafana

```yaml
# Prometheus config
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-service'
    static_configs:
      - targets: ['api:8080']
```

```python
# Instrument Python application
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
requests_total = Counter('requests_total', 'Total HTTP requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

# Use in application
@app.route('/api/endpoint')
def endpoint():
    requests_total.inc()
    with request_duration.time():
        # Handle request
        return {"status": "ok"}
```

## Key Metrics to Monitor

### Application Metrics
- **Request Rate**: Requests per second
- **Error Rate**: Errors per second or percentage
- **Response Time**: P50, P95, P99 latencies
- **Saturation**: Resource utilization (CPU, memory, disk)

### Infrastructure Metrics
- **CPU Usage**: Per container/node
- **Memory Usage**: Current and trends
- **Disk I/O**: Read/write rates
- **Network Traffic**: In/out bandwidth

### Business Metrics
- **Active Users**: Current concurrent users
- **Conversion Rate**: Feature usage metrics
- **Revenue**: Per service/feature

## Alerting Best Practices

```yaml
# Prometheus alert rule
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"
```

- [principle] **Alert on Symptoms, Not Causes**: Alert on user impact
- [best-practice] Avoid alert fatigue - only critical alerts
- [pattern] On-call rotation for alert handling

## SLIs, SLOs, and SLAs

- **SLI (Service Level Indicator)**: Quantitative measure (e.g., 99.9% uptime)
- **SLO (Service Level Objective)**: Target value for SLI
- **SLA (Service Level Agreement)**: Contract with consequences

Example:
- SLI: Request success rate
- SLO: 99.95% of requests succeed
- SLA: Credits if below 99.9%

## Relations
- builds_on [[DevOps Culture]]
- uses [[Prometheus]]
- uses [[Grafana]]
- related_to [[Incident Management]]
- enables [[Site Reliability Engineering]]

## Observability vs Monitoring

- [monitoring] **Known Unknowns**: Alert on expected failures
- [observability] **Unknown Unknowns**: Explore and understand novel failures

*You can't improve what you don't measure - monitor everything!*

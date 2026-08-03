# Backend System Monitoring & Observability Guide

This guide describes the monitoring, observability, logging, request tracing, health checks, and performance tracking subsystems built into the **AI Virtual Wear Simulation Backend**.

---

## 1. Structured JSON Logging Architecture

All logging output across FastAPI, middleware handlers, services, and recommendation engines uses a structured JSON log format:

```json
{
  "timestamp": "2026-07-31T23:00:00.123456+00:00",
  "logLevel": "INFO",
  "message": "API Request processed: GET /api/v1/products",
  "logger": "virtual_wear",
  "requestId": "cd7f3f33-f9b8-42be-8077-50ff16a759e4",
  "endpoint": "/api/v1/products",
  "method": "GET",
  "statusCode": 200,
  "latency": 6.14
}
```

### Log Levels
- **`INFO`**: Normal API execution, startup validation, cache hits/misses, request completion.
- **`WARNING`**: Expected HTTP client errors (404 Not Found, 422 Unprocessable Entity), missing user preference profile lookups.
- **`ERROR`**: Critical unhandled server exceptions (500), startup dependency failures.

---

## 2. Request ID Tracing (`X-Request-ID`)

Every HTTP request entering the FastAPI server is assigned a unique UUID v4 tracking identifier by `RequestIdMiddleware`:
1. If incoming request contains `X-Request-ID` header, it is reused for distributed tracing.
2. If missing, a new UUID v4 string is generated.
3. The tracking ID is attached to `request.state.request_id`, passed to `log_structured()`, and returned in the HTTP response header `X-Request-ID` as well as the JSON payload `requestId`.

---

## 3. Health Check Subsystem (`GET /api/v1/health`)

Monitors operational readiness across all Phase 1 backend components:

| Component Key | Healthy State | Degraded / Unhealthy Trigger |
| :--- | :--- | :--- |
| `status` | `"healthy"` | `"unhealthy"` if critical datasets or config missing |
| `products` | `"loaded"` | `"missing"` if `products.json` cannot be read |
| `users` | `"loaded"` | `"missing"` if `user_preferences.json` cannot be read |
| `configuration` | `"loaded"` | `"missing"` if `recommendation_config.json` missing |
| `strategy` | `"RuleBased"` | Active strategy name |
| `cache` | `"enabled"` | `"disabled"` if cache unavailable |
| `analytics` | `"available"` | Operational status |

---

## 4. Cache Statistics Monitoring

The recommendation cache records execution metrics accessible via `RecommendationEngine.cache.get_stats()`:
- `totalRequests`: Total recommendation calls processed
- `hits`: Recommendations served directly from memory cache
- `misses`: Recommendations computed via scorer & filters
- `hitRatePercent`: Cache hit ratio percentage (`(hits / totalRequests) * 100`)

---

## 5. Automated Performance Benchmarking

Run the automated performance reporting utility at any time:

```bash
python backend/scripts/performance_report.py
```

This generates `backend/reports/performance_report.md` measuring latencies, throughput (requests/sec), and memory footprint.

# Performance Troubleshooting Guide

## Overview
Slow dashboard load times or degraded API response times can stem from several causes: plan limits, data volume, network conditions, or temporary infrastructure issues. This guide helps diagnose and resolve performance complaints.

## Details

### Dashboard loading slowly
- First check: is the slowness specific to one page/view, or the entire application?
- Page-specific slowness: usually a data volume issue (e.g., loading 10,000 rows without pagination).
- Whole-app slowness: may indicate a browser extension conflict, network issue, or platform-side degradation.

### Root cause diagnosis steps
1. Ask the customer to test in an incognito window (rules out browser extensions).
2. Ask them to test on a different network (rules out ISP/VPN issues).
3. Check our status page for any active performance incidents.
4. Ask for a browser HAR file if the issue persists (Network tab → right-click → Save as HAR).

### API response time expectations
- Standard API calls: p50 < 100ms, p99 < 500ms.
- Bulk export endpoints: may take up to 60 seconds for large datasets. Use async export endpoints for datasets > 10,000 records.
- Search endpoints: p50 < 200ms with proper index configuration.

### Known performance bottlenecks
- Reports with date ranges > 12 months may be slow; recommend using the export endpoint instead.
- Importing CSV files > 50MB triggers an async job — the customer should not wait on the page but instead check the import history.
- Webhook delivery latency can spike during high-traffic periods; queue depth is visible in Settings → Developer → Webhook Logs.

### Platform usage limits
- Starter plan: dashboard limited to 30-day data window. Queries outside this range are truncated.
- Pro plan: 12-month data window for dashboards. Full export available via API.
- Enterprise: no data window limits.

## Edge Cases
- If one specific customer is consistently slow but others are not, check if they're in a different geographic region (EU vs. US) and whether the nearest data center is healthy.
- Memory-intensive browser tabs: customers with many tabs open may experience slowness unrelated to our platform.

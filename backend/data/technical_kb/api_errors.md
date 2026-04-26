# API Error Reference Guide

## Overview
This guide covers the most common API errors customers encounter when integrating with our platform. It includes error codes, root causes, and resolution steps for each.

## Details

### HTTP 400 Bad Request
- Cause: Malformed request body, missing required fields, or invalid field values.
- Resolution: Check the API documentation for required fields. Validate JSON syntax. Look for null values where strings are expected.
- Common mistake: Sending `Content-Type: text/plain` instead of `Content-Type: application/json`.

### HTTP 401 Unauthorized
- Cause: Missing or invalid API key.
- Resolution: Verify the API key is included in the `Authorization: Bearer <token>` header. Regenerate the API key in Settings → API → API Keys if suspected compromised.
- Note: API keys have a 90-day rotation policy for Enterprise customers.

### HTTP 403 Forbidden
- Cause: Valid API key but insufficient permissions for the requested resource.
- Resolution: Check the key's permission scopes in Settings → API → API Keys. Ensure the key has read/write access for the endpoint being called.

### HTTP 429 Too Many Requests
- Cause: Rate limit exceeded.
- Limits: Starter: 100 req/min, Pro: 500 req/min, Enterprise: custom.
- Resolution: Implement exponential backoff. Check the `Retry-After` response header for the cooldown period.
- The rate limit resets every 60 seconds (sliding window).

### HTTP 500 Internal Server Error
- Cause: Server-side error. This is our fault, not the customer's.
- Resolution: Ask customer to share the request ID from the `X-Request-ID` response header. This allows our engineering team to find the specific error in logs.
- If persistent (>5 minutes), check our status page at status.ourplatform.com.

### HTTP 503 Service Unavailable
- Cause: Planned maintenance or unexpected service degradation.
- Resolution: Check status.ourplatform.com. Subscribe to incident notifications.

## Process Steps
1. Identify the HTTP status code.
2. Check if it's reproducible (intermittent vs. consistent).
3. Collect the `X-Request-ID` header from a failing request.
4. Check our API status page for known outages.
5. Escalate to engineering with the Request ID if no known outage.

## Edge Cases
- 401 on a valid, recently-generated key: the key may not have propagated to all edge nodes yet. Wait 60 seconds and retry.
- 500 errors during maintenance windows are expected; they resolve automatically.
- Webhooks that fail with 5xx on the customer's endpoint are retried up to 5 times with exponential backoff.

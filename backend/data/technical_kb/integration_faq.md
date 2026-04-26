# Integration & Webhook FAQ

## Overview
Customers integrate our platform with their own systems via REST API and webhooks. This document covers setup, authentication, webhook configuration, and common integration problems.

## Details

### Setting up webhooks
1. Go to Settings → Developer → Webhooks → Add Endpoint.
2. Enter the HTTPS endpoint URL (HTTP is not supported for security reasons).
3. Select the event types to subscribe to (e.g., `ticket.created`, `user.updated`).
4. Copy the webhook signing secret — you'll need this to verify payload signatures.
5. Click Save. A test event is sent immediately to verify the endpoint is reachable.

### Verifying webhook signatures
- Every webhook payload includes an `X-Signature-256` header.
- Compute HMAC-SHA256 of the raw request body using your signing secret.
- Compare with the header value. If they don't match, discard the event.
- Use constant-time comparison to prevent timing attacks.

### Webhook retry behavior
- We retry failed deliveries (non-2xx response or timeout) up to 5 times.
- Retry schedule: 1 min, 5 min, 30 min, 2 hours, 8 hours.
- After 5 failures, the endpoint is automatically disabled. The customer must re-enable it in the dashboard.

### Common integration issues
- **Webhook not received**: Check firewall rules — our IPs are listed at docs.ourplatform.com/webhook-ips.
- **Duplicate events**: Implement idempotency using the `event_id` in the payload header.
- **Out-of-order events**: Use the `created_at` timestamp, not the arrival time, for ordering.
- **Large payloads**: Events with attachments use a `data_url` field instead of inlining the content. Fetch the URL within 24 hours — it expires.

### OAuth integration
- We support OAuth 2.0 Authorization Code flow for third-party integrations.
- Tokens expire after 1 hour; use the refresh token (valid 30 days) to get a new access token.
- Scopes: `read:tickets`, `write:tickets`, `read:users`, `admin` (Enterprise only).

## Edge Cases
- If a customer's endpoint returns 200 but processes events asynchronously, they should respond immediately with 200 and queue the work to avoid timeouts.
- Zapier/Make integrations: use our native integrations rather than the raw webhook when available — they handle retries and auth automatically.

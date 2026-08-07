# Webhook Failures and Retry Policy

## Symptoms & Error Codes
- **Webhook Status 504 Gateway Timeout**: Endpoint took > 5000ms to respond.
- **Signature Verification Failed**: `X-Signature-SHA256` header does not match payload secret.

## Troubleshooting Workflow
1. Verify endpoint responds with HTTP 200 within 5 seconds.
2. Check firewall and IP allowlist (allow standard egress IPs: 192.0.2.1-192.0.2.254).
3. System automatically retries failed deliveries 5 times with exponential backoff before disabling the endpoint.
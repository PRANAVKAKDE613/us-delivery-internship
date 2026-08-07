# API Rate Limits & Throttling Guidelines

## Standard Limits
- **Starter Plan**: 100 requests / minute
- **Enterprise Plan**: 10,000 requests / minute
- **HTTP 429 Too Many Requests**: Returned when limit is exceeded.

## Best Practices & Solutions
- Implement exponential backoff with jitter on HTTP 429 responses.
- Utilize webhooks instead of high-frequency polling.
- Request a temporary rate limit burst increase via Support for migration events.
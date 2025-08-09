# Plant Assistant Security for GitHub Copilot

## Security
- Auth: JWT for sessions (fastapi-jwt-auth); or OAuth for social logins.
- API: CORS config, rate limiting (slowapi), HTTPS enforcement.
- Data: Encrypt sensitive info (e.g., Fernet for user data); opt-in for photo storage (GDPR consent forms).

## Detailed Practices
- Input Sanitization: Pydantic for validation, bleach for text.
- Auditing: Log access with structlog.

## Rationale
- Protects user data; complies with regs to avoid fines.

## Scaling Considerations
- Add WAF (Web Application Firewall); penetration testing annually.
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

### 1. Do NOT create a public issue

Please **do not** create a GitHub issue for security vulnerabilities. This helps protect users who may be affected.

### 2. Report via GitHub Security Advisories

1. Go to the [Security tab](https://github.com/thanhtrungnguyen/plant-assistant/security)
2. Click "Report a vulnerability"
3. Fill out the security advisory form with detailed information

### 3. Email Contact (Alternative)

If you cannot use GitHub Security Advisories, you can email:
- **Primary Contact**: [Your Email Here]
- **Subject**: `[SECURITY] Plant Assistant Vulnerability Report`

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Steps to Reproduce**: Step-by-step instructions
- **Impact**: What an attacker could achieve
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: If you have ideas for fixing it
- **Your Contact**: How we can reach you for questions

### Response Timeline

We take security seriously and will respond as follows:

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Regular Updates**: Weekly until resolved
- **Resolution**: Varies by severity (critical issues get priority)

### Security Updates

When we release security updates:

1. **Critical**: Emergency release within 24-48 hours
2. **High**: Release within 1 week
3. **Medium/Low**: Include in next planned release

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version
2. **Environment Variables**: Use strong secrets and never commit them
3. **Database**: Use strong database passwords
4. **Network**: Use HTTPS in production
5. **Access Control**: Implement proper authentication

### For Contributors

1. **Dependencies**: Keep dependencies updated
2. **Code Review**: All changes require review
3. **Testing**: Write security-focused tests
4. **Secrets**: Never commit secrets or credentials
5. **Input Validation**: Always validate user input

## Security Features

### Current Security Measures

- **Authentication**: JWT-based authentication
- **Password Hashing**: Secure password hashing
- **Input Validation**: Pydantic validation for all inputs
- **CORS**: Configurable CORS settings
- **Rate Limiting**: API rate limiting (planned)
- **HTTPS**: SSL/TLS support in production
- **Environment Isolation**: Separate environments for dev/staging/prod

### Planned Security Enhancements

- [ ] Two-factor authentication (2FA)
- [ ] API rate limiting
- [ ] Advanced logging and monitoring
- [ ] Security headers middleware
- [ ] Content Security Policy (CSP)
- [ ] Regular security audits

## Compliance

This project follows security best practices including:

- **OWASP Top 10**: Protection against common web vulnerabilities
- **Dependency Scanning**: Automated vulnerability scanning
- **Code Quality**: Static analysis and linting
- **Secure Defaults**: Secure configuration by default

## Security Configuration

### Required Environment Variables

Never commit these to version control:

```bash
# Required for production
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
MAIL_SERVER=your-mail-server

# Optional but recommended
CORS_ORIGINS=["https://yourdomain.com"]
ENVIRONMENT=production
```

### GitHub Secrets Setup

Set these secrets in your GitHub repository:

- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: Production database URL
- `TEST_DATABASE_URL`: Test database URL  
- `POSTGRES_PASSWORD`: Database password
- `MAIL_SERVER`: Email server configuration
- `MAIL_PORT`: Email server port
- `CORS_ORIGINS`: Allowed CORS origins

## Acknowledgments

We appreciate security researchers and the community for helping keep Plant Assistant secure.

---

**Remember**: Security is a shared responsibility. If you see something, say something!

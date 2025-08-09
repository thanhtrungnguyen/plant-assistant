# Plant Assistant Non-Functional Requirements for GitHub Copilot

## Non-Functional Requirements
- **Usability**: Mobile-responsive UI with intuitive navigation; Shadcn UI ensures WCAG 2.1 compliance (e.g., screen reader support). Dark mode and i18n ready.
- **Performance**: Response times <2s for AI queries; handle 1,000 concurrent users. Use caching (e.g., Redis later) and optimize images.
- **Security**: Encrypt data at rest/transit; GDPR compliant with consent for photos. Auth via JWT, rate limiting to prevent abuse.
- **Monetization**: Free tier (limited queries), premium ($4.99/month for unlimited, advanced features). Use Stripe integration post-MVP.
- **Reliability**: 99% uptime; error logging with Sentry. Disclaimers for AI advice (e.g., "Not substitute for professional help").

## Detailed Specs
- Accessibility: Alt text for images, keyboard navigation.
- Scalability: Cloud-ready (e.g., Vercel for frontend, Heroku for backend).
- Maintainability: Code coverage >80%, docs in README.

## Rationale
- Based on industry standards (e.g., OWASP for security). Ensures app is user-friendly and trustworthy.

## Scaling Considerations
- Add load testing with Locust; auto-scaling on AWS.
- Compliance Updates: Monitor for new regs like CCPA.